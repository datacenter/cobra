# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Access module for the ACI Python SDK (cobra).

This module ties together the session object and requests to allow a single
interface by which requests are made.
"""

from builtins import object  # pylint:disable=redefined-builtin
from future.utils import viewitems

from cobra.mit.request import (DnQuery, ClassQuery, CommitError, QueryError,
                               RestError)


class MoDirectory(object):

    """Creates a connection to the APIC and the MIT.

    MoDirectory requires an existing session.

    Attributes:
      session (cobra.mit.session.AbstractSession): The session tied to this
        MoDirectory instance.
    """

    def __init__(self, session):
        """Initialize a MoDirectory instance.

        Args:
          session (cobra.mit.session.AbstractSession): The session

        """
        self._session = session

    @property
    def session(self):
        """Get the session for this MoDirectory instance.

        Returns:
          cobra.mit.session.AbstractSession: The session tied to this
          MoDirectory instance.
        """
        return self._session

    def login(self):
        """Create a session to an APIC."""
        self.session.login()

    def logout(self):
        """End a session to an APIC."""
        self.session.logout()

    def reauth(self):
        """Re-authenticate the session with the current authentication cookie.

        This method can be used to extend the validity of a successful login
        credentials. This method may fail if the current session expired on
        the server side. If this method fails, the user must login again to
        authenticate and effectively create a new session.
        """
        self.session.refresh()

    def query(self, queryObject):
        """Query the Model Information Tree.

        The various types of potential queryObjects provide a variety of
        search options

        Args:
          queryObject (cobra.mit.request.AbstractRequest): A query object

        Returns:
          list: A list of Managed Objects (MOs) returned from the query
        """
        try:
            rsp = self.session.get(queryObject)
            return self.__parseResponse(rsp)
        except RestError as ex:
            self.__parseError(ex.reason, QueryError, ex.httpCode)

    def commit(self, configObject):
        """Commit operation for a request object.

        Commit a change on the APIC or fabric node.

        Args:
          configObject (cobra.mit.request.AbstractRequest): The configuration
            request to commit

        Returns:
          str:  The response as a string


        Raises:
          CommitError: If no MOs have been added to the config request
        """
        try:
            rsp = self.session.post(configObject)
            return self.__parseResponse(rsp)
        except RestError as ex:
            self.__parseError(ex.reason, CommitError, ex.httpCode)

    def lookupByDn(self, dnStrOrDn, **kwargs):
        """Query the APIC or fabric node by distinguished name (Dn).

        A short-form managed object (MO) query using the Dn of the MO
        of the MO.

        Args:
          dnStrOrDn (str or cobra.mit.naming.Dn): A distinguished name as a
            :class:`cobra.mit.naming.Dn` or string
          **kwargs: Arbitrary parameters to be passed to the query
            generated internally, to further filter the result

        Returns:
          None or cobra.mit.mo.Mo: None if no MO was returned otherwise
            :class:`cobra.mit.mo.Mo`
        """
        dnQuery = DnQuery(dnStrOrDn)
        self.__setQueryParams(dnQuery, kwargs)
        mos = self.query(dnQuery)
        return mos[0] if mos else None

    def lookupByClass(self, classNames, parentDn=None, **kwargs):
        """Lookup MO's by class.

        A short-form managed object (MO) query by class.

        Args:
          classNames (str or list): The class name list of class names.
            If parentDn is set, the classNames are used as a filter in a
            subtree query for the parentDn
          parentDn (cobra.mit.naming.Dn or str, optional): The distinguished
            name of the parent object as a :class:`cobra.mit.naming.Dn` or
            string.
          **kwargs: Arbitrary parameters to be passed to the query
            generated internally, to further filter the result

        Returns:
          list: A list of the managed objects found in the query.
        """
        if parentDn:
            dnQuery = DnQuery(parentDn)
            dnQuery.classFilter = classNames
            dnQuery.queryTarget = 'subtree'
            self.__setQueryParams(dnQuery, kwargs)
            mos = self.query(dnQuery)
        else:
            classQuery = ClassQuery(classNames)
            self.__setQueryParams(classQuery, kwargs)
            mos = self.query(classQuery)
        return mos

    def __parseError(self, rsp, errorClass, httpCode):
        """Parse errors.

        Parse any errors that may have occurred in rsp and raise the exception
        errorClass.

        Args:
          rsp (str): The response that contains the error.
          errorClass (Exception): The exception that should be raised once the
            response is parsed.
          httpCode (int): The HTTP error code, example 400.

        Raises:
          Exception: The errorClass.

        """
        self.session.codec.error(rsp, errorClass, httpCode)

    def __parseResponse(self, rsp):
        """Parse a response.

        Args:
          rsp (str): The response to parse.

        Returns:
          cobra.mit.mo.Mo: The response parsed into a managed object.
        """
        return self.session.codec.fromStr(rsp)

    @staticmethod
    def __setQueryParams(query, queryParams):
        """Utility function to set the query parameters.

        Utility function used to set in the 'query' passed as
        argument, the 'queryParams' dictionary. The key in the
        dictionary will be used as the property name to set, with
        the value content.

        Args:
          query: query class to be modified
          queryParams: a dictionary including the properties to the
            added to the query.
        """
        for param, value in viewitems(queryParams):
            if value is not None:
                setattr(query, param, value)
