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

"""Tests to assure the CORS utilities.

Test-Suite to ensure that the CORS decorator is working as expected.
"""
from condition_api.utils.util import cors_preflight

import pytest


TEST_CORS_METHODS_DATA = [
    ('GET'),
    ('PUT'),
    ('POST'),
    ('DELETE'),
    ('GET,PUT'),
    ('GET,POST'),
    ('PUT,POST'),
    ('GET,PUT,POST'),
]

ALLOWED_ORIGIN = 'https://conditions.example.gov.bc.ca'


def _preflight_options(methods):
    """Build a class decorated with cors_preflight and return its options method."""
    @cors_preflight(methods)  # pylint: disable=too-few-public-methods
    class TestCors():
        pass

    return TestCors().options  # pylint: disable=no-member


@pytest.mark.parametrize('methods', TEST_CORS_METHODS_DATA)
def test_cors_preflight_allowed_origin(app, monkeypatch, methods):
    """An allow-listed Origin is echoed back with credentials on preflight."""
    monkeypatch.setenv('CORS_ORIGIN', ALLOWED_ORIGIN)
    options = _preflight_options(methods)

    with app.test_request_context(headers={'Origin': ALLOWED_ORIGIN}):
        rv = options()

    headers = rv[2]
    assert headers['Access-Control-Allow-Origin'] == ALLOWED_ORIGIN
    assert headers['Access-Control-Allow-Credentials'] == 'true'
    assert headers['Vary'] == 'Origin'
    assert headers['Access-Control-Allow-Methods'] == methods


@pytest.mark.parametrize('methods', TEST_CORS_METHODS_DATA)
def test_cors_preflight_disallowed_origin(app, monkeypatch, methods):
    """A non-allow-listed Origin is not reflected (no wildcard) on preflight."""
    monkeypatch.setenv('CORS_ORIGIN', ALLOWED_ORIGIN)
    options = _preflight_options(methods)

    with app.test_request_context(headers={'Origin': 'https://not-allowed.example'}):
        rv = options()

    headers = rv[2]
    assert 'Access-Control-Allow-Origin' not in headers
    assert 'Access-Control-Allow-Credentials' not in headers
    assert headers['Access-Control-Allow-Methods'] == methods
