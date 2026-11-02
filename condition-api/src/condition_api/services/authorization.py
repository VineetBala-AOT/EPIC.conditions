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


"""The Authorization service.

This module is to handle authorization related queries.
"""
from flask import current_app

from condition_api.utils.roles import EpicConditionRole
from condition_api.utils.user_context import UserContext, user_context


# Roles that identify a caller as EPIC.conditions internal staff. Membership in
# one of these — not the mere presence of any realm role — is what grants the
# internal view (unapproved conditions, condition attributes) on the
# auth-optional read endpoints.
INTERNAL_ROLES = frozenset(role.value for role in EpicConditionRole)


def _token_roles(token_info):
    """Collect the caller's roles from both realm and client scopes.

    Mirrors the JWT_ROLE_CALLBACK (``get_roles`` in the app factory): Keycloak
    may deliver the application roles either as realm roles
    (``realm_access.roles``) or as client roles
    (``resource_access.<client>.roles``) depending on realm configuration, so we
    must look in both — otherwise staff whose roles live under ``resource_access``
    are misclassified as external and shown only the public (approved-only) view.
    """
    token_info = token_info or {}
    realm_roles = (token_info.get('realm_access') or {}).get('roles', [])
    client_name = current_app.config.get('JWT_OIDC_AUDIENCE')
    client_roles = (token_info.get('resource_access') or {}).get(client_name, {}).get('roles', [])
    return set(realm_roles) | set(client_roles)


# pylint: disable=unused-argument
@user_context
def check_auth(**kwargs):
    """Return True only if the caller holds an EPIC.conditions application role.

    Keycloak assigns default realm roles (e.g. ``default-roles-*``,
    ``offline_access``, ``uma_authorization``) to every authenticated user, so
    checking for *any* role would treat ordinary users as internal staff.
    Gate on the application's own roles instead, checking both realm and client
    role scopes.
    """
    user_from_context: UserContext = kwargs['user_context']
    token_roles = _token_roles(user_from_context.token_info)
    return bool(token_roles & INTERNAL_ROLES)
