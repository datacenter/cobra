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

    def commit(self, configObject):
        """
        Short-form commit operation for a configRequest
        """
        if configObject.getRootMo() is None:
            raise CommitError(0, "No mos in config request")
        return self._accessImpl.post(configObject)

    def lookupByDn(self, dnStrOrDn):
        """
        A short-form managed object (MO) query using the distinguished name(Dn)
        of the MO.
        """
        dnQuery = DnQuery(dnStrOrDn)
        mos = self.query(dnQuery)
        return mos[0] if mos else None

    def lookupByClass(self, classNames, parentDn=None, propFilter=None):
        """
        A short-form managed object (MO) query by class.
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
