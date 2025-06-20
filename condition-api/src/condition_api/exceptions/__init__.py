# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Application Specific Exceptions, to manage the business errors.

@log_error - a decorator to automatically log the exception to the logger provided

BusinessException - error, status_code - Business rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound, UnprocessableEntity
from werkzeug.wrappers.response import Response


class BusinessError(Exception):
    """Exception that adds error code and error."""

    def __init__(self, error, status_code, *args, **kwargs):
        """Return a valid BusinessException."""
        super().__init__(*args, **kwargs)
        self.error = error
        self.status_code = status_code


class ResourceExistsError(Conflict):
    """Exception raised when a duplicate resource exists."""

    def __init__(self, message, *args, **kwargs):
        """Return a valid ResourceExistsError."""
        super().__init__(*args, **kwargs)
        self.description = message
        self.response = Response(message, status=Conflict.code)


class BadRequestError(BadRequest):
    """Exception raised when there are issues with the api input"""

    def __init__(self, message, *args, **kwargs):
        """Return a valid BadRequestError."""
        super().__init__(*args, **kwargs)
        self.description = message
        self.response = Response(message, status=BadRequest.code)


class ResourceNotFoundError(NotFound):
    """Exception raised when resource not found"""

    def __init__(self, message, *args, **kwargs):
        """Return a valid ResourceExistsError."""
        super().__init__(*args, **kwargs)
        self.description = message
        self.response = Response(message, status=NotFound.code)


class PermissionDeniedError(Forbidden):
    """Exception raised when resource not found"""

    def __init__(self, message, *args, **kwargs):
        """Return a valid ResourceExistsError."""
        super().__init__(*args, **kwargs)
        self.description = message
        self.response = Response(message, status=Forbidden.code)


class UnprocessableEntityError(UnprocessableEntity):
    """Exception raised when resource is not processable"""

    def __init__(self, message, *args, **kwargs):
        """Return a valid UnprocessableEntityError."""
        super().__init__(*args, **kwargs)
        self.description = message
        self.response = Response(message, status=UnprocessableEntity.code)


class ConditionNumberExistsError(ValueError):
    """Raised when the condition number already exists in the document."""


class ConditionNumberExistsInProjectError(ValueError):
    """Raised when the condition number already exists in the project."""

    def __init__(self, message, is_amendment=False):
        """Init"""
        super().__init__(message)
        self.is_amendment = is_amendment
