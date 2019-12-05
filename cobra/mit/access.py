# Copyright 2019 Cisco Systems, Inc.
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

"""The Access module for the ACI Python SDK (cobra).

This module ties together the session object and requests to allow a single
interface by which requests are made.
"""

from builtins import object

from cobra.mit.request import DnQuery, ClassQuery, CommitError
from cobra.internal.rest.accessimpl import RestAccess


class MoDirectory(object):

    """
    The MoDirectory class creates a connection to the APIC and the MIT.
    MoDirectory requires an existing session and endpoint.
    """

    def __init__(self, session):
        """
        Arguments:
            session: Specifies a session
        """
        self._accessImpl = RestAccess(session)
        self.session = session

    def login(self):
        """
        Creates a session to an APIC.
        """
        self._accessImpl.login()

    def logout(self):
        """
        Ends a session to an APIC.
        """
        self._accessImpl.logout()

    def reauth(self):
        """
        Re-authenticate this session with the current authentication cookie.
        This method can be used to extend the validity of a successful login
        credentials. This method may fail if the current session expired on
        the server side. If this method fails, the user must login again to
        authenticate and effectively create a new session.
        """
        self._accessImpl.refreshSession()

    def query(self, queryObject):
        """
        Queries the MIT for a specified object. The queryObject provides a
        variety of search options.
        """
        return self._accessImpl.get(queryObject)

    def commit(self, configObject, sync_wait_timeout=None):
        """
        Short-form commit operation for a configRequest
        """
        # If a sync_wait_timeout is specified, then we call the post_sync_wait
        # method of the accessImpl, otherwise call post method
        if sync_wait_timeout:
            return self._accessImpl.post_sync_wait(configObject, timeout=sync_wait_timeout)
        else:
            return self._accessImpl.post(configObject)

    def lookupByDn(self, dnStrOrDn, **queryParams):
        """
        A short-form managed object (MO) query using the distinguished name(Dn)
        of the MO.

        Args:
          dnStrOrDn:   dn of the object to lookup
          queryParams: a dictionary including the properties to the
            added to the query.
        """
        dnQuery = DnQuery(dnStrOrDn)
        self.__setQueryParams(dnQuery, queryParams)
        mos = self.query(dnQuery)
        return mos[0] if mos else None

    def lookupByClass(self, classNames, parentDn=None, **queryParams):
        """
        A short-form managed object (MO) query by class.

        Args:
          classNames: Name of the class to lookup
          parentDn:   dn of the root object were to start search from (optional)
          queryParams: a dictionary including the properties to the
            added to the query.
        """
        if parentDn:
            dnQuery = DnQuery(parentDn)
            dnQuery.classFilter = classNames
            dnQuery.queryTarget = 'subtree'
            self.__setQueryParams(dnQuery, queryParams)
            mos = self.query(dnQuery)
        else:
            classQuery = ClassQuery(classNames)
            self.__setQueryParams(classQuery, queryParams)
            mos = self.query(classQuery)
        return mos

    def exists(self, dnStrOrDn):
        """Checks if managed object (MO) with given distinguished name (dn) is present or not

        Args:
          dnStrOrDn (str or cobra.mit.naming.Dn): A distinguished name as a
            :class:`cobra.mit.naming.Dn` or string

        Returns:
          bool: True, if MO is present, else False.
        """
        mo = self.lookupByDn(dnStrOrDn, subtreeInclude='count')
        return mo is not None and int(mo.count) > 0

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
        for param, value in list(queryParams.items()):
            if value is not None:
                setattr(query, param, value)
