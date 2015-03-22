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

from builtins import str
from builtins import object

import requests
from cobra.internal.codec.jsoncodec import fromJSONStr, parseJSONError
from cobra.internal.codec.xmlcodec import fromXMLStr, parseXMLError
from cobra.mit.request import QueryError, CommitError, RestError
import json


class RestAccess(object):

    def __init__(self, session):
        self._session = session
        self._requests = requests.Session()

    def _get(self, request):
        """
        Internal _get method which performs raw request and returns requests
        response object
        """
        uriPathAndOptions = request.getUriPathAndOptions(self._session)
        headers = self._session.getHeaders(uriPathAndOptions, None)
        return self._requests.get(request.getUrl(self._session),
                                  headers=headers, verify=self._session.secure,
                                  timeout=self._session.timeout)

    def get(self, request):
        """Return data from the server for the given request on the
        given session

        Args:
          request (cobra.mit.request.AbstractQuery): The query object

        Raises:
          cobra.mit.request.QueryError: If the response indicates an error
            occurred
          ValueError: If the response could not be parsed

        Returns:
          cobra.mit.mo.Mo: The query response parsed into a managed object
        """
        rsp = self._get(request)
        if rsp.status_code != requests.codes.ok:
            return self.__parseError(rsp, QueryError, rsp.status_code)
        return self.__parseResponse(rsp)

    def _post(self, request):
        """
        Internal _post method which performs raw request and returns requests
        response object.

        This method will also handle redirects for POST as needed.
        """
        uriPathAndOptions = request.getUriPathAndOptions(self._session)
        headers = self._session.getHeaders(uriPathAndOptions, None)
        rsp = self._requests.post(request.getUrl(self._session),
                                  **request.requestargs(self._session))
        # handle a redirect, for example from http to https
        while rsp.status_code in (requests.codes.moved, requests.codes.found):
            loc = rsp.headers['Location']
            uriPathAndOptions = request.getUriPathAndOptions(self._session)
            session.url = loc.rstrip(uriPathAndOptions)
            return self._post(request)
        return rsp

    def post(self, request):
        """Return data from the server for the given request on the
        given session by posting the data in the request object, the response
        is parsed for errors.

        Args:
          request (cobra.mit.request.AbstractRequest): The request object

        Raises:
          cobra.mit.request.CommitError: If the response indicates  an error
          ValueError: If the response can not be parsed

        Returns:
          requests.response: The raw requests response object for a successful
            request
        """
        rsp = self._post(request)
        if rsp.status_code != requests.codes.ok:
            return self.__parseError(rsp, CommitError, rsp.status_code)
        return rsp

    def __parseError(self, rsp, errorClass, httpCode):
        try:
            if self._session.formatType == self._session.XML_FORMAT:
                parseXMLError(rsp.text, errorClass, httpCode)
            parseJSONError(rsp.text, errorClass, httpCode)
        except ValueError as ex:
            raise RestError(None, str(ex), httpCode)

    def __parseResponse(self, rsp):
        if self._session.formatType == self._session.XML_FORMAT:
            return fromXMLStr(rsp.text)
        return fromJSONStr(rsp.text)
