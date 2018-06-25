# Copyright 2018 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import uuid

import pytest
import requests

from sherlockml.clients.base import InvalidResponseBody
from sherlockml.clients.user import UserClient
from tests.clients.fixtures import (
    patch_sherlockmlauth, PROFILE, HUDSON_URL, AUTHORIZATION_HEADER
)

TEST_USER_ID = uuid.uuid4()


def test_authenticated_user_id(requests_mock, patch_sherlockmlauth):

    requests_mock.get(
        '{}/authenticate'.format(HUDSON_URL),
        request_headers=AUTHORIZATION_HEADER,
        json={'account': {'userId': str(TEST_USER_ID)}}
    )

    client = UserClient(PROFILE)
    assert client.authenticated_user_id() == TEST_USER_ID


def test_authenticated_user_id_error_response(
    requests_mock, patch_sherlockmlauth
):

    requests_mock.get(
        '{}/authenticate'.format(HUDSON_URL),
        request_headers=AUTHORIZATION_HEADER,
        status_code=400
    )

    client = UserClient(PROFILE)
    with pytest.raises(requests.HTTPError):
        client.authenticated_user_id()


@pytest.mark.parametrize('mock_kwargs', [
    {'text': 'invalid-json'},
    {'json': {}},
    {'json': {'account': {'userId': 'invalid-uuid'}}}
])
def test_authenticated_user_id_bad_response(
    requests_mock, patch_sherlockmlauth, mock_kwargs
):

    requests_mock.get(
        '{}/authenticate'.format(HUDSON_URL),
        request_headers=AUTHORIZATION_HEADER,
        **mock_kwargs
    )

    client = UserClient(PROFILE)
    with pytest.raises(InvalidResponseBody):
        client.authenticated_user_id()
