"""Service for project management."""
from sqlalchemy import func, case
from sqlalchemy.orm import aliased
from condition_api.models.condition import Condition
from condition_api.models.subcondition import Subcondition
from condition_api.models.condition_requirement import ConditionRequirement
from condition_api.models.document import Document
from condition_api.models.db import db
from condition_api.models.project import Project


class ProjectService:
    """Project management service."""

    @staticmethod
    def get_project_details(project_id):
        """Fetch project details along with related documents, conditions, subconditions, and condition requirements by project ID."""

        # Aliases for the tables
        projects = aliased(Project)
        documents = aliased(Document)
        conditions = aliased(Condition)
        subconditions = aliased(Subcondition)
        condition_requirements = aliased(ConditionRequirement)

        # Step 1: Fetch Project details
        project_data = db.session.query(
            projects.project_id,
            projects.project_name,
            projects.project_type,
        ).filter(projects.project_id == project_id).first()

        if not project_data:
            return None

        # Initialize the project structure
        project = {
            "project_id": project_data.project_id,
            "project_name": project_data.project_name,
            "project_type": project_data.project_type,
            "documents": [],
        }

        # Step 2: Fetch Document details based on project_id
        document_data = db.session.query(
            documents.document_id,
            documents.display_name,
            documents.document_file_name,
            documents.document_type,
            documents.date_issued,
            documents.act,
            documents.project_id,
            documents.first_nations,
            documents.consultation_records_required,
        ).filter(documents.project_id == project_id).all()

        # Create a map to hold documents
        document_map = {}
        for doc in document_data:
            document_map[doc.document_id] = {
                "document_id": doc.document_id,
                "display_name": doc.display_name,
                "document_file_name": doc.document_file_name,
                "document_type": doc.document_type,
                "date_issued": doc.date_issued,
                "act": doc.act,
                "project_id": doc.project_id,
                "first_nations": doc.first_nations,
                "consultation_records_required": doc.consultation_records_required,
                "conditions": [],
            }
            # Append each document to the project documents array
            project["documents"].append(document_map[doc.document_id])

        # Step 3: Fetch Condition details based on document IDs
        document_ids = [doc["document_id"] for doc in project["documents"]]
        condition_data = db.session.query(
            conditions.id.label('condition_id'),
            conditions.condition_name,
            conditions.condition_number,
            conditions.condition_text,
            conditions.topic_tags,
            conditions.subtopic_tags,
            conditions.document_id,
        ).filter(conditions.document_id.in_(document_ids)).all()

        # Add conditions to the corresponding document
        condition_map = {}
        for cond in condition_data:
            condition_map[cond.condition_id] = {
                "condition_id": cond.condition_id,
                "condition_name": cond.condition_name,
                "condition_number": cond.condition_number,
                "condition_text": cond.condition_text,
                "topic_tags": cond.topic_tags,
                "subtopic_tags": cond.subtopic_tags,
                "subconditions": [],
                "condition_requirements": [],
            }
            # Append condition to its respective document
            document_map[cond.document_id]["conditions"].append(condition_map[cond.condition_id])

        # Step 4: Fetch Subcondition details based on condition IDs
        condition_ids = [cond["condition_id"] for cond in condition_map.values()]
        subcondition_data = db.session.query(
            subconditions.id.label('subcondition_id'),
            subconditions.subcondition_identifier,
            subconditions.subcondition_text,
            subconditions.condition_id,
            subconditions.parent_subcondition_id,
        ).filter(subconditions.condition_id.in_(condition_ids)).all()

        # Create a map to handle hierarchical subconditions
        subcondition_map = {}
        for subcond in subcondition_data:
            subcondition = {
                "subcondition_id": subcond.subcondition_id,
                "subcondition_identifier": subcond.subcondition_identifier,
                "subcondition_text": subcond.subcondition_text,
                "subconditions": [],
            }
            subcondition_map[subcond.subcondition_id] = subcondition

            if subcond.parent_subcondition_id:
                # Append to parent subcondition
                parent = subcondition_map.get(subcond.parent_subcondition_id)
                if parent:
                    parent["subconditions"].append(subcondition)
            else:
                # Append top-level subcondition to the condition
                condition_map[subcond.condition_id]["subconditions"].append(subcondition)

        # Step 5: Fetch Condition Requirement details
        condition_requirement_data = db.session.query(
            condition_requirements.condition_id,
            condition_requirements.deliverable_name,
            condition_requirements.is_plan,
            condition_requirements.approval_type,
            condition_requirements.stakeholders_to_consult,
            condition_requirements.stakeholders_to_submit_to,
            condition_requirements.consultation_required,
            condition_requirements.related_phase,
            condition_requirements.days_prior_to_commencement,
        ).filter(condition_requirements.condition_id.in_(condition_ids)).all()

        # Add condition requirements to the corresponding condition
        for cr in condition_requirement_data:
            condition_map[cr.condition_id]["condition_requirements"].append({
                "deliverable_name": cr.deliverable_name,
                "is_plan": cr.is_plan,
                "approval_type": cr.approval_type,
                "stakeholders_to_consult": cr.stakeholders_to_consult,
                "stakeholders_to_submit_to": cr.stakeholders_to_submit_to,
                "consultation_required": cr.consultation_required,
                "related_phase": cr.related_phase,
                "days_prior_to_commencement": cr.days_prior_to_commencement,
            })

        return project


    @staticmethod
    def get_all_projects():
        """Fetch all projects along with related documents."""

        # Aliases for the tables
        projects = aliased(Project)
        documents = aliased(Document)
        conditions = aliased(Condition)

        # Step 1: Fetch Projects
        project_data = db.session.query(
            projects.project_id,
            projects.project_name,
            projects.project_type,
        ).all()

        if not project_data:
            return None

        # Step 2: Initialize the result list to store project data along with documents
        result = []

        # Step 3: Iterate over each project and fetch related documents
        for project in project_data:
            project_id = project.project_id

            # Fetch related documents for the current project
            document_data = db.session.query(
                documents.document_id,
                documents.display_name,
                documents.document_file_name,
                documents.document_type,
                documents.date_issued,
                documents.act,
                documents.project_id,
                documents.first_nations,
                documents.consultation_records_required,
                # Subquery to check if all related conditions have is_approved=True
                func.min(case((conditions.is_approved == False, 0), else_=1)).label('all_approved')
            ).outerjoin(conditions, conditions.document_id == documents.document_id
            ).filter(documents.project_id == project_id
            ).group_by(
                documents.document_id,
                documents.display_name,
                documents.document_file_name,
                documents.document_type,
                documents.date_issued,
                documents.act,
                documents.project_id,
                documents.first_nations,
                documents.consultation_records_required
            ).all()

            # Create a document map for the current project
            document_map = {}
            project_documents = []

            for doc in document_data:
                status = bool(doc.all_approved)
                document_map[doc.document_id] = {
                    "document_id": doc.document_id,
                    "display_name": doc.display_name,
                    "document_file_name": doc.document_file_name,
                    "document_type": doc.document_type,
                    "date_issued": doc.date_issued,
                    "act": doc.act,
                    "project_id": doc.project_id,
                    "first_nations": doc.first_nations,
                    "consultation_records_required": doc.consultation_records_required,
                    "status": status,
                }
                # Append each document to the project's document array
                project_documents.append(document_map[doc.document_id])

            # Step 4: Append the project along with its documents to the result list
            result.append({
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_type": projects.project_type,
                "documents": project_documents
            })

        # Return the result containing all projects and their related documents
        return result
