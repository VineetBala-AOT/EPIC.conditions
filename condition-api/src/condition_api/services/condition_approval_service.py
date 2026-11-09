"""Single source of truth for recomputing a condition's attribute-approval flag."""
from sqlalchemy import and_, func, not_

from condition_api.models.condition import Condition
from condition_api.models.condition_attribute import ConditionAttribute
from condition_api.models.db import db
from condition_api.models.iem_terms import IEMTerms
from condition_api.models.management_plan import ManagementPlan
from condition_api.models.report import Report
from condition_api.models.report_submission import ReportSubmission
from condition_api.utils.enums import MANAGEMENT_PLAN_ASSOCIATED_REPORT_TYPE

# The three roll-up states a condition (or any of its parts) can be in, ordered from
# lowest to highest. These string values match the web app's DocumentStatus type so the
# badge can consume them directly.
STATUS_DATA_ENTRY_REQUIRED = "nodata"
STATUS_AWAITING_CONFIRMATION = "false"
STATUS_CONFIRMED = "true"


class ConditionApprovalService:
    """Recomputes condition.is_condition_attributes_approved from current state."""

    @staticmethod
    def recompute_attributes_approved(condition_id):
        """Set is_condition_attributes_approved from every package type the condition requires.

        Replaces the condition's shared attribute-approval flag with the AND of all
        management plans, all IEM Terms of Engagement packages, and all report
        submissions that currently exist for it (scoped to whichever of those the
        condition actually requires), instead of any single caller overwriting the
        flag from just its own entity type. Call this after any add, remove, or
        approval-toggle on a management plan, IEM terms package, report, or report
        submission so the flag always reflects the combined state.
        """
        condition = Condition.query.get(condition_id)
        if not condition:
            return

        all_approved = True

        if condition.requires_management_plan:
            plans = ManagementPlan.query.filter_by(condition_id=condition_id).all()
            all_approved = all_approved and bool(plans) and all(p.is_approved for p in plans)

        if condition.requires_iem_terms:
            terms = IEMTerms.query.filter_by(condition_id=condition_id).all()
            all_approved = all_approved and bool(terms) and all(t.is_approved for t in terms)

        if condition.requires_report:
            reports = Report.query.filter_by(condition_id=condition_id).all()
            submissions = [s for r in reports for s in r.submissions]
            all_approved = all_approved and bool(submissions) and all(s.is_approved for s in submissions)

        # If the condition requires no package types at all, there is nothing in the
        # attributes dimension to approve, so it is vacuously satisfied. (A bare
        # condition with no attributes is handled on the approval path in
        # ConditionService.update_condition; this keeps recompute consistent when the
        # last required package is removed and the condition becomes bare again.)

        condition.is_condition_attributes_approved = all_approved

    @staticmethod
    def compute_condition_status(condition):
        """Return the rolled-up 3-state status for a condition.

        The overall status of a condition is the *lowest* status among its parts
        (condition info, topic tags, and each attribute package), where the order is:
        Data Entry Required ("nodata") < Awaiting Confirmation ("false") < Confirmed
        ("true"). This mirrors the per-item rules the web app applies to management
        plans, IEM Terms of Engagement, and report submissions so the condition,
        conditions-list, and consolidated badges all agree.

        - "nodata": at least one required package still needs data entry (a management
          plan or IEM Terms package with no attribute values yet, or a management-plan
          associated report submission that has not been linked to a plan).
        - "true": the condition is fully confirmed (info + tags + all attributes).
        - "false": otherwise (has data, but not everything is approved yet).

        `condition` is a Condition model instance.
        """
        if ConditionApprovalService._has_data_entry_required(condition):
            return STATUS_DATA_ENTRY_REQUIRED

        fully_approved = bool(
            condition.is_approved
            and condition.is_topic_tags_approved
            and condition.is_condition_attributes_approved
        )
        return STATUS_CONFIRMED if fully_approved else STATUS_AWAITING_CONFIRMATION

    @staticmethod
    def compute_statuses_for(approved_by_id):
        """Return {condition_id: status} for many conditions in a few queries.

        `approved_by_id` maps each condition id to its already-computed combined
        approval boolean (is_approved AND is_condition_attributes_approved AND
        is_topic_tags_approved) — the same value `compute_condition_status`
        derives per condition, but the read builders already have it as a query
        column, so it is passed in rather than re-fetched. Data-entry-required is
        resolved for the whole set with `condition_ids_needing_data_entry`
        (set-based), so this produces the identical result as calling
        `compute_condition_status` per condition while avoiding the per-condition
        package queries that version issues one row at a time.
        """
        needing = ConditionApprovalService.condition_ids_needing_data_entry(
            list(approved_by_id)
        )
        statuses = {}
        for condition_id, fully_approved in approved_by_id.items():
            if condition_id in needing:
                statuses[condition_id] = STATUS_DATA_ENTRY_REQUIRED
            elif fully_approved:
                statuses[condition_id] = STATUS_CONFIRMED
            else:
                statuses[condition_id] = STATUS_AWAITING_CONFIRMATION
        return statuses

    @staticmethod
    def document_needs_data_entry(document_id=None, amended_document_id=None):
        """Return True if any valid condition on the document still needs data entry.

        Used to roll the "Data Entry Required" state up to the document, category, and
        project badges. Invalid placeholder conditions (no name and no number) are
        ignored, matching how the document/project approval status is computed.
        `document_id` targets an original document's conditions; `amended_document_id`
        targets an amendment's conditions.
        """
        valid = not_(
            and_(Condition.condition_name.is_(None), Condition.condition_number.is_(None))
        )
        query = db.session.query(Condition.id).filter(valid)
        if amended_document_id is not None:
            query = query.filter(Condition.amended_document_id == amended_document_id)
        else:
            query = query.filter(
                Condition.document_id == document_id,
                Condition.amended_document_id.is_(None),
            )
        condition_ids = [row.id for row in query.all()]
        return bool(ConditionApprovalService.condition_ids_needing_data_entry(condition_ids))

    @staticmethod
    def any_condition_needs_data_entry(conditions):
        """Return True if any Condition in the iterable needs data entry."""
        condition_ids = [condition.id for condition in conditions]
        return bool(ConditionApprovalService.condition_ids_needing_data_entry(condition_ids))

    @staticmethod
    def condition_ids_needing_data_entry(condition_ids):
        """Return the subset of condition_ids that still need data entry.

        Evaluates all three package rules with set-based SQL — three aggregate
        queries total, independent of how many conditions are passed — instead of
        per-condition package queries, so rolling "Data Entry Required" up to the
        document, category, and project badges stays cheap even for projects with
        many conditions. The rules mirror `_has_data_entry_required` for a single
        condition (each gated by the matching requires_* flag).
        """
        if not condition_ids:
            return set()

        has_value = and_(
            ConditionAttribute.attribute_value.isnot(None),
            func.trim(ConditionAttribute.attribute_value) != "",
        )

        needing = set()

        # Management plans with no non-empty attribute value yet.
        mp_rows = (
            db.session.query(ManagementPlan.condition_id)
            .join(Condition, Condition.id == ManagementPlan.condition_id)
            .filter(
                Condition.id.in_(condition_ids),
                Condition.requires_management_plan.is_(True),
                ~db.session.query(ConditionAttribute.id)
                .filter(
                    ConditionAttribute.condition_id == Condition.id,
                    ConditionAttribute.management_plan_id == ManagementPlan.id,
                    has_value,
                )
                .exists(),
            )
            .all()
        )
        needing.update(row.condition_id for row in mp_rows)

        # IEM Terms packages with no non-empty attribute value yet.
        iem_rows = (
            db.session.query(IEMTerms.condition_id)
            .join(Condition, Condition.id == IEMTerms.condition_id)
            .filter(
                Condition.id.in_(condition_ids),
                Condition.requires_iem_terms.is_(True),
                ~db.session.query(ConditionAttribute.id)
                .filter(
                    ConditionAttribute.condition_id == Condition.id,
                    ConditionAttribute.iem_terms_id == IEMTerms.id,
                    has_value,
                )
                .exists(),
            )
            .all()
        )
        needing.update(row.condition_id for row in iem_rows)

        # Management-plan associated report submissions not yet linked to a plan.
        report_rows = (
            db.session.query(Report.condition_id)
            .join(Condition, Condition.id == Report.condition_id)
            .join(ReportSubmission, ReportSubmission.report_id == Report.id)
            .filter(
                Condition.id.in_(condition_ids),
                Condition.requires_report.is_(True),
                Report.report_type == MANAGEMENT_PLAN_ASSOCIATED_REPORT_TYPE,
                ReportSubmission.linked_management_plan_id.is_(None),
            )
            .all()
        )
        needing.update(row.condition_id for row in report_rows)

        return needing

    @staticmethod
    def _has_data_entry_required(condition):
        """Return True if any present, required package still needs data entry.

        Only packages that currently exist are considered — a required package type
        with nothing added yet is not shown on the detail page, so it must not force
        the whole condition to "Data Entry Required".
        """
        condition_id = condition.id

        if condition.requires_management_plan:
            plans = ManagementPlan.query.filter_by(condition_id=condition_id).all()
            for plan in plans:
                if not ConditionApprovalService._package_has_attribute_data(
                    condition_id, management_plan_id=plan.id
                ):
                    return True

        if condition.requires_iem_terms:
            terms = IEMTerms.query.filter_by(condition_id=condition_id).all()
            for term in terms:
                if not ConditionApprovalService._package_has_attribute_data(
                    condition_id, iem_terms_id=term.id
                ):
                    return True

        if condition.requires_report:
            reports = Report.query.filter_by(condition_id=condition_id).all()
            for report in reports:
                if report.report_type != MANAGEMENT_PLAN_ASSOCIATED_REPORT_TYPE:
                    continue
                for submission in report.submissions:
                    if submission.linked_management_plan_id is None:
                        return True

        return False

    @staticmethod
    def _package_has_attribute_data(condition_id, management_plan_id=None, iem_terms_id=None):
        """Return True if the package has at least one non-empty attribute value.

        Matches the web app's `attributeHasData` check (any attribute value that is not
        blank after trimming).
        """
        query = db.session.query(ConditionAttribute.id).filter(
            ConditionAttribute.condition_id == condition_id,
            ConditionAttribute.attribute_value.isnot(None),
            func.trim(ConditionAttribute.attribute_value) != "",
        )
        if management_plan_id is not None:
            query = query.filter(ConditionAttribute.management_plan_id == management_plan_id)
        if iem_terms_id is not None:
            query = query.filter(ConditionAttribute.iem_terms_id == iem_terms_id)
        return query.first() is not None
