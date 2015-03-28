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

"""accessimpl.py.

The implementation of the access layer for the ACI Python SDK (cobra).
"""

# These imports are for python2/3 compatibility
from builtins import object  # pylint:disable=redefined-builtin
from builtins import str     # pylint:disable=redefined-builtin

import requests
from cobra.mit.request import RestError


class RestAccess(object):

    """Rest access object.

    The implementation of of REST access for ACI.
    """

    def __init__(self, session):
        """Initialize an instance of RestAccess."""
        self._session = session
        self._requests = requests.Session()

    @staticmethod
    def responseIsOk(response):
        """Check if the response from the remote server is ok.

        Returns:
          bool: True if the response did not indicate an error, False otherwise
        """
        # pylint:disable=no-member
        return response.status_code == requests.codes.ok

    def get(self, request):
        """Query the server.

        Return data from the server for the given request on the given session.

        Args:
          request (cobra.mit.request.AbstractQuery): The query object

        Raises:
          cobra.mit.request.QueryError: If the response indicates an error
            occurred
          ValueError: If the response could not be parsed

        Returns:
          cobra.mit.mo.Mo: The query response parsed into a managed object
        """
        uriPathAndOptions = request.getUriPathAndOptions(self._session)
        headers = self._session.getHeaders(uriPathAndOptions, None)
        rsp = self._requests.get(request.getUrl(self._session),
                                 headers=headers, verify=self._session.secure,
                                 timeout=self._session.timeout)
        if not self.responseIsOk(rsp):
            raise RestError(0, str(rsp.text), rsp.status_code)
        return str(rsp.text)

    def post(self, request):
        """Return data from the server.

        For the given request on the session, return POST data from the
        server.  The response is parsed for errors.

        Args:
          request (cobra.mit.request.AbstractRequest): The request object

        Raises:
          cobra.mit.request.CommitError: If the response indicates  an error
          ValueError: If the response can not be parsed

        Returns:
          requests.response: The raw requests response object for a successful
            request
        """
        uriPathAndOptions = request.getUriPathAndOptions(self._session)
        self._session.getHeaders(uriPathAndOptions, None)
        rsp = self._requests.post(request.getUrl(self._session),
                                  **request.requestargs(self._session))
        # handle a redirect, for example from http to https
        # pylint:disable=no-member
        while rsp.status_code in (requests.codes.moved, requests.codes.found):
            loc = rsp.headers['Location']
            uriPathAndOptions = request.getUriPathAndOptions(self._session)
            self._session.url = loc.rstrip(uriPathAndOptions)
            return self.post(request)

        if not self.responseIsOk(rsp):
            raise RestError(0, str(rsp.text), rsp.status_code)
        return str(rsp.text)
