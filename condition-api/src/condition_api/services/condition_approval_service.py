"""Single source of truth for recomputing a condition's attribute-approval flag."""
from condition_api.models.condition import Condition
from condition_api.models.iem_terms import IEMTerms
from condition_api.models.management_plan import ManagementPlan
from condition_api.models.report import Report


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
