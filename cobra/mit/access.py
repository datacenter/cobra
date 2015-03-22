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

from builtins import object

from cobra.internal.codec.jsoncodec import fromJSONStr, parseJSONError
from cobra.internal.codec.xmlcodec import fromXMLStr, parseXMLError
from cobra.mit.request import (DnQuery, ClassQuery, CommitError, QueryError,
                               RestError)


class MoDirectory(object):
    """Creates a connection to the APIC and the MIT.

    MoDirectory requires an existing session.

    """

    def __init__(self, session):
        """Initialize a MoDirectory instance

        Args:
          session (cobra.mit.session.AbstractSession): The session

        """
        self._session = session

    def login(self):
        """Creates a session to an APIC."""
        self._session.login()

    def logout(self):
        """Ends a session to an APIC."""
        self._session.logout()

    def reauth(self):
        """Re-authenticate the session with the current authentication cookie.

        This method can be used to extend the validity of a successful login
        credentials. This method may fail if the current session expired on
        the server side. If this method fails, the user must login again to
        authenticate and effectively create a new session.
        """
        self._session.refreshSession()

    def query(self, queryObject):
        """Queries the Model Information Tree.

        The various types of potential queryObjects provide a variety of
        search options

        Args:
          queryObject (cobra.mit.request.AbstractRequest): A query object

        Returns:
          list: A list of Managed Objects (MOs) returned from the query
        """
        rsp = self._session.get(queryObject)
        if not self._session.responseIsOk(rsp.status_code):
            self.__parseError(rsp, QueryError, rsp.status_code)
        return self.__parseResponse(rsp)

    def commit(self, configObject):
        """Commit operation for a request object.

        Commit a change on the APIC or fabric node.

        Args:
          configObject (cobra.mit.request.AbstractRequest): The configuration
            request to commit

        Returns:
          requests.response:  The response.
          
            .. note::
               This is different behavior than the query method.

        Raises:
          CommitError: If no MOs have been added to the config request
        """
        rsp = self._session.post(configObject)
        if not self._session.responseIsOk(rsp.status_code):
            self.__parseError(rsp, CommitError, rsp.status_code)
        return self.__parseResponse(rsp)

    def lookupByDn(self, dnStrOrDn):
        """Query the APIC or fabric node by distinguished name (Dn)
        
        A short-form managed object (MO) query using the Dn of the MO
        of the MO.

        Args:
          dnStrOrDn (str or cobra.mit.naming.Dn): A distinguished name as a
            :class:`cobra.mit.naming.Dn` or string

        Returns:
          None or cobra.mit.mo.Mo: None if no MO was returned otherwise
            :class:`cobra.mit.mo.Mo`
        """
        dnQuery = DnQuery(dnStrOrDn)
        mos = self.query(dnQuery)
        return mos[0] if mos else None

    def lookupByClass(self, classNames, parentDn=None, propFilter=None):
        """Lookup MO's by class

        A short-form managed object (MO) query by class.

        Args:
          classNames (str or list): The class name list of class names.
            If parentDn is set, the classNames are used as a filter in a
            subtree query for the parentDn
          parentDn (cobra.mit.naming.Dn or str): The distinguished
            name of the parent object as a :class:`cobra.mit.naming.Dn` or
            string.
          propFilter (str): A property filter expression

        Returns:
          list: A list of the managed objects found in the query.
        """
        if parentDn:
            dnQuery = DnQuery(parentDn)
            dnQuery.classFilter = classNames
            dnQuery.queryTarget = 'subtree'
            if propFilter:
                dnQuery.propFilter = propFilter
            mos = self.query(dnQuery)
        else:
            classQuery = ClassQuery(classNames)
            if propFilter:
                classQuery.propFilter = propFilter
            mos = self.query(classQuery)
        return mos

    def __parseError(self, rsp, errorClass, httpCode):
        try:
            if self._session.formatType == self._session.XML_FORMAT:
                parseXMLError(rsp.text, errorClass, httpCode)
            parseJSONError(rsp.text, errorClass, httpCode)
        except ValueError as ex:
            raise
            #raise RestError(None, str(ex), httpCode)

    def __parseResponse(self, rsp):
        if self._session.formatType == self._session.XML_FORMAT:
            return fromXMLStr(rsp.text)
        return fromJSONStr(rsp.text)