# Copyright 2018-2019 ASI Data Science
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


from datetime import datetime, timedelta
from collections import namedtuple

import requests
import pytz

import faculty.config


AccessToken = namedtuple("AccessToken", ["token", "expires_at"])


class MemoryAccessTokenCache(object):
    def __init__(self):
        self._store = {}

    def get(self, profile):
        access_token = self._store.get(profile)
        utc_now = datetime.now(tz=pytz.utc)
        if access_token is None or access_token.expires_at < utc_now:
            return None
        else:
            return access_token

    def add(self, profile, access_token):
        self._store[profile] = access_token


def _get_access_token(profile):

    url = "{}://hudson.{}/access_token".format(
        profile.protocol, profile.domain
    )
    payload = {
        "client_id": profile.client_id,
        "client_secret": profile.client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    body = response.json()

    token = body["access_token"]
    now = datetime.now(tz=pytz.utc)
    expires_at = now + timedelta(seconds=body["expires_in"])

    return AccessToken(token, expires_at)


class Session(object):

    __session_cache = {}

    def __init__(self, profile, access_token_cache):
        self.profile = profile
        self.access_token_cache = access_token_cache

    @classmethod
    def get(cls, *args, access_token_cache=None, **kwargs):
        key = (args, access_token_cache) + tuple(kwargs.items())
        try:
            session = cls.__session_cache[key]
        except KeyError:
            profile = faculty.config.resolve_profile(*args, **kwargs)
            access_token_cache = access_token_cache or MemoryAccessTokenCache()
            session = cls(profile, access_token_cache)
            cls.__session_cache[key] = session
        return session

    def access_token(self):
        access_token = self.access_token_cache.get(self.profile)
        if access_token is None:
            access_token = _get_access_token(self.profile)
            self.access_token_cache.add(self.profile, access_token)
        return access_token
