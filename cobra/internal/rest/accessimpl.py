# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from cobra.internal.codec.jsoncodec import fromJSONStr, parseJSONError
from cobra.internal.codec.xmlcodec import fromXMLStr, parseXMLError
from cobra.mit.request import QueryError, CommitError, RestError, AbstractRequest
from cobra.mit.session import LoginSession, CertSession, AbstractSession
import json


class LoginRequest(AbstractRequest):
    """
    LoginRequest for standard user/password based authentication
    """

    def __init__(self, user, password):
        super(LoginRequest, self).__init__()
        self.user = user
        self.password = password

    @property
    def data(self):
        userJson = {
            'aaaUser': {
                'attributes': {
                    'name': self.user,
                    'pwd': self.password
                }
            }
        }
        return json.dumps(userJson, sort_keys=True)

    def requestargs(self, session):
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'data': self.data,
            'timeout': session.timeout
        }
        return kwargs

    @staticmethod
    def getUrl(session):
        url = session.url
        url += '/api/aaaLogin.json'
        return url


class RefreshRequest(AbstractRequest):
    """
    Session refresh request for standard user/password based authentication
    """

    def __init__(self, cookie):
        super(RefreshRequest, self).__init__()
        self.cookie = cookie

    @staticmethod
    def getUrl(session):
        url = session.url
        url += '/api/aaaRefresh.json'
        return url


class LoginHandler(object):
    @classmethod
    def login(cls, session):
        loginRequest = LoginRequest(session.user, session.password)
        url = loginRequest.getUrl(session)
        rsp = requests.post(url, **loginRequest.requestargs(session))
        session._parseResponse(rsp)

    @classmethod
    def logout(cls, session, accessimpl):
        pass

    @classmethod
    def refresh(cls, session, accessimpl):
        refreshRequest = RefreshRequest(session.cookie)
        session._parseResponse(accessimpl._get(refreshRequest))


class CertHandler(object):
    @classmethod
    def login(cls, session):
        pass

    @classmethod
    def logout(cls, session, accessimpl):
        pass

    @classmethod
    def refresh(cls, session, accessimpl):
        pass


class RestAccess(object):
    loginHandlers = {
        LoginSession: LoginHandler,
        CertSession: CertHandler,
    }

    def __init__(self, session):
        self._session = session
        self._requests = requests.Session()

    def login(self):
        """
        Authenticate the user/certification provided by the session
        object.
        Args:
            session (LoginSession/CertSession): Session object
        """
        sessionClass = self._session.__class__
        loginHandler = RestAccess.loginHandlers.get(sessionClass, None)
        if loginHandler is not None:
            loginHandler.login(self._session)

    def logout(self):
        sessionClass = self._session.__class__
        loginHandler = RestAccess.loginHandlers.get(sessionClass, None)
        if loginHandler is not None:
            loginHandler.logout(self._session, self)

    def refreshSession(self):
        """Refresh the _cookie for the given session object
        Args:
            session (LoginSession/CertSession)
        """
        sessionClass = self._session.__class__
        loginHandler = RestAccess.loginHandlers.get(sessionClass, None)
        if loginHandler is not None:
            loginHandler.refresh(self._session, self)

    def _get(self, request):
        """
        Internal _get method which performs raw request and returns requests
        response object
        """
        uriPathAndOptions = request.getUriPathAndOptions(self._session)
        headers = self._session.getHeaders(uriPathAndOptions, None)
        return self._requests.get(request.getUrl(self._session), headers=headers,
                            verify=self._session.secure,
                            timeout=self._session.timeout)

    def get(self, request):
        """Return data from the server for the given request on the
        given session
        Args:
            request (DnQuery/ClassQuery/TraceQuery/AbstractQuery child): Query
                object
        Return:
            requests.response
        """
        rsp = self._get(request)
        if rsp.status_code != requests.codes.ok:
            return self.__parseError(rsp, QueryError, rsp.status_code)
        return self.__parseResponse(rsp)

    def post(self, request):
        """Return data from the server for the given request on the
        given session by posting the data in the request object
        Args:
            request (ConfigRequest): ConfigRequest object
        Return:
            requests.response
        """
        url = request.getUrl(self._session)
        rsp = self._requests.post(url, **request.requestargs(self._session))
        if rsp.status_code != requests.codes.ok:
            return self.__parseError(rsp, CommitError, rsp.status_code)
        return rsp

    def __parseError(self, rsp, errorClass, httpCode):
        try:
            if self._session.formatType == AbstractSession.XML_FORMAT:
                parseXMLError(rsp.text, errorClass, httpCode)
            parseJSONError(rsp.text, errorClass, httpCode)
        except ValueError as ex:
            raise RestError(None, str(ex), httpCode)

    def __parseResponse(self, rsp):
        if self._session.formatType == AbstractSession.XML_FORMAT:
            return fromXMLStr(rsp.text)
        return fromJSONStr(rsp.text)

