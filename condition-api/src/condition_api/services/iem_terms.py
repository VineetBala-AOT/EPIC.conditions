"""Service for IEM Terms of Engagement management."""
from marshmallow import ValidationError

from condition_api.models.db import db
from condition_api.models.condition import Condition
from condition_api.models.iem_terms import IEMTerms
from condition_api.services.condition_approval_service import ConditionApprovalService


class IEMTermsService:
    """Service for managing IEM Terms of Engagement related operations."""

    @staticmethod
    def update_iem_terms(terms_id, payload):
        """Update an IEM Terms package name or approval status."""
        terms = IEMTerms.find_by_id(terms_id)
        if not terms:
            raise ValueError("IEM Terms not found for the given ID.")

        if "name" in payload:
            name = payload["name"]
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("IEM Terms name cannot be blank.")
            terms.name = name.strip()

        if "is_approved" in payload:
            terms.is_approved = payload["is_approved"]
            ConditionApprovalService.recompute_attributes_approved(terms.condition_id)

        db.session.commit()
        return terms

    @staticmethod
    def delete_iem_terms(terms_id):
        """Delete an IEM Terms package and recompute the condition's approval flag."""
        terms = IEMTerms.query.filter_by(id=terms_id).one_or_none()
        if not terms:
            return False
        condition_id = terms.condition_id
        db.session.delete(terms)
        db.session.flush()
        # If this was the last IEM Terms package, the condition no longer requires
        # one. Clearing the flag lets recompute treat the now package-free
        # attributes dimension as satisfied instead of leaving the condition stuck
        # at "awaiting" with no package left to approve.
        remaining = IEMTerms.query.filter_by(condition_id=condition_id).count()
        if remaining == 0:
            condition = Condition.query.get(condition_id)
            if condition:
                condition.requires_iem_terms = False
        ConditionApprovalService.recompute_attributes_approved(condition_id)
        db.session.commit()
        return True
