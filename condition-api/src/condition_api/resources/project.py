# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoints for managing a project resource."""

from http import HTTPStatus
from flask_restx import Namespace, Resource, cors
from marshmallow import ValidationError

from condition_api.schemas.project import ProjectSchema
from condition_api.services.project_service import ProjectService
from condition_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper

API = Namespace("projects", description="Endpoints for Project Management")
"""Custom exception messages
"""

project_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ProjectSchema(), "Project"
)

@cors_preflight("GET, OPTIONS")
@API.route("/<string:project_id>", methods=["GET", "OPTIONS"])
class ProjectDetailsResource(Resource):
    """Resource for fetching project details by project_id."""

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Get projects by account id")
    @API.response(code=HTTPStatus.CREATED, model=project_list_model, description="Get projects")
    @API.response(HTTPStatus.BAD_REQUEST, "Bad Request")
    @cors.crossdomain(origin="*")
    def get(project_id):
        """Fetch project details and conditions by project ID."""
        try:
            project_details = ProjectService.get_project_details(project_id)
            if not project_details:
                return {"message": "Project not found"}, HTTPStatus.NOT_FOUND

            # Instantiate the schema
            project_details_schema = ProjectSchema()

            # Call dump on the schema instance
            return project_details_schema.dump(project_details), HTTPStatus.OK
        except ValidationError as err:
            return {"message": str(err)}, HTTPStatus.BAD_REQUEST