# Copyright © 2019 Province of British Columbia
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
"""Test Utils.

Test Utility for creating test scenarios.
"""
from enum import Enum

from condition_api.config import get_named_config

from faker import Faker


fake = Faker()

CONFIG = get_named_config('testing')


class TestProjectInfo(Enum):
    """Test scenarios of Project Creation."""

    project1 = {
        "name": fake.word(),
        "description": fake.sentence(),
        "address": fake.address(),
        "type_id": fake.random_int(min=1, max=9),
        "sub_type_id": fake.random_int(min=1, max=10),
        "proponent_id": fake.random_int(min=1, max=10),
        "region_id_env": fake.random_int(min=1, max=10),
        "region_id_flnro": fake.random_int(min=1, max=10),
        "latitude": fake.latitude(),
        "longitude": fake.longitude(),
        "abbreviation": fake.word().upper()[:10]

    }

    project2 = {
        "name": fake.word(),
    }


class TestStaffInfo(Enum):
    """Test scenarios of Staff Creation."""

    staff1 = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "is_active": True,
        "position_id": fake.random_int(min=1, max=12)
    }

    update_staff = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "is_active": True,
        "position_id": fake.random_int(min=1, max=12)
    }

    validate_staff = {
        "email": fake.email()
    }


class TestIssues(Enum):
    """Test scenarios of Issues Creation."""

    issue2 = {
        "title": fake.word(),
        "description": fake.sentence(),
        "start_date": fake.date_time_this_decade(tzinfo=None).isoformat(),
        "expected_resolution_date": fake.date_time_between(start_date='now', end_date='+10d', tzinfo=None).isoformat(),
        "is_active": True,
        "is_high_priority": True,
        "updates": [fake.sentence()]
    }


class TestWorkIssuesInfo(Enum):
    """Test scenarios for WorkIssues."""

    issue1 = {
        "title": fake.word(),
        "is_active": True,
        "is_high_priority": False,
        "start_date": fake.date_time_this_decade(tzinfo=None),
        "expected_resolution_date": fake.date_time_this_decade(tzinfo=None),
    }


class TestStatus(Enum):
    """Test scenarios of WorkStatus."""

    status1 = {
        "description": fake.sentence(),
        "posted_date": fake.date_time_this_decade(tzinfo=None).isoformat(),
        "is_approved": False,
        "approved_by": None,
        "approved_date": None,
    }


class TestWorkIssueUpdatesInfo(Enum):
    """Test scenarios for WorkIssueUpdates."""

    update1 = {
        "description": fake.sentence(),
        "posted_date": fake.date_time_this_decade(tzinfo=None).isoformat(),
        "is_approved": False,
        "approved_by": None,
    }


class TestJwtClaims(dict, Enum):
    """Test scenarios of jwt claims."""

    staff_admin_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'preferred_username': f'{fake.user_name()}@idir',
        'given_name': fake.first_name(),
        'family_name': fake.last_name(),
        'tenant_id': 1,
        "aud": CONFIG.JWT_OIDC_TEST_AUDIENCE,
        'email': 'staff@gov.bc.ca',
        'realm_access': {
            'roles': [
                'view_conditions',
                'create',
                'edit',
                'extended_edit'

            ]
        }
    }
    manage_user_role = {
        'iss': CONFIG.JWT_OIDC_TEST_ISSUER,
        'sub': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'idp_userid': 'f7a4a1d3-73a8-4cbc-a40f-bb1145302064',
        'preferred_username': f'{fake.user_name()}@idir',
        "aud": CONFIG.JWT_OIDC_TEST_AUDIENCE,
        'given_name': fake.first_name(),
        'family_name': fake.last_name(),
        'tenant_id': 1,
        'email': 'example@example.com',
        'realm_access': {
            'roles': [
                'view_conditions'
            ]
        }
    }


class TestProponent(Enum):
    """Test scenarios for proponents"""

    proponent1 = {
        "name": fake.word()
    }

    proponent2 = {
        "name": fake.word()
    }


class TestFirstNation(Enum):
    """Test scenarios for first nations"""

    first_nation1 = {
        "name": fake.word(),
        "is_active": False,
        "notes": fake.sentence(),
        "pip_link": fake.domain_word(),
    }

    first_nation2 = {
        "name": fake.word(),
        "is_active": True,
        "notes": fake.sentence(),
        "pip_link": fake.domain_word(),
    }


class TestPipOrgType(Enum):
    """Test scenarios for PIP Org Types"""

    pip_org_type1 = {
        "name": fake.word()
    }


class TestRoleEnum(Enum):
    """Test scenarios for roles"""

    RESPONSIBLE_EPD = 1
    TEAM_LEAD = 2
    OFFICER_ANALYST = 3
    FN_CAIRT = 4
    OTHER = 5


class TestWorkFirstNationEnum(Enum):
    """Test scenarios for work first nation"""

    work_first_nation1 = {
        "indigenous_category_id": fake.random_int(min=1, max=8),
        "indigenous_consultation_level_id": fake.random_int(min=1, max=4),
        "is_active": True
    }


class TestWorkNotesEnum(Enum):
    """Test scenarios for work notes"""

    work_notes1 = {
        "notes": fake.sentence(),
        "note_type": "status_notes"
    }

    work_notes2 = {
        "notes": fake.sentence(),
        "note_type": "issue_notes"
    }


class TestTaskTemplateEnum(Enum):
    """Test scenarios for task templates"""

    task_template1 = {
        "name": fake.word(),
        "ea_act_id": 3,
        "work_type_id": 1,
        "phase_id": 1,
    }


class TestElevatedRoleEnum(Enum):
    """Test elevated role enum"""

    MANAGE_FIRST_NATIONS = 1


class TestElevatedRole(Enum):
    """Test scenarios for elevated roles"""

    elevated_role1 = {
        "id": TestElevatedRoleEnum.MANAGE_FIRST_NATIONS.value,
        "name": fake.word(),
        "description": fake.sentence(),
        "sort_order": 1
    }


class TestStaffElevatedRole(Enum):
    """Test scenarios for staff elevated roles"""

    staff_elevated_role1 = {
        "staff_id": fake.random_int(min=1, max=200),
        "elevated_role_id": TestElevatedRoleEnum.MANAGE_FIRST_NATIONS.value,
        "is_active": True
    }

    staff_elevated_role2 = {
        "staff_id": fake.random_int(min=1, max=200),
        "elevated_role_id": TestElevatedRoleEnum.MANAGE_FIRST_NATIONS.value,
        "is_active": True
    }

    staff_elevated_role_active = {
        "id": 1,
        "staff_id": 234,
        "elevated_role_id": TestElevatedRoleEnum.MANAGE_FIRST_NATIONS.value,
        "is_active": True
    }

    staff_elevated_role_inactive = {
        "id": 1,
        "staff_id": 234,
        "elevated_role_id": TestElevatedRoleEnum.MANAGE_FIRST_NATIONS.value,
        "is_active": False
    }
