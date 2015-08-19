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

"""The request module for the ACI Python SDK (cobra)."""

from builtins import str     # pylint:disable=redefined-builtin
from builtins import object  # pylint:disable=redefined-builtin

import json
from cobra.mit.naming import Dn
from cobra.internal.codec.jsoncodec import toJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr


class AbstractRequest(object):

    """Abstract base class for all other request types.

    Attributes:
      options (str): The HTTP request query string for this object - readonly

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self):
        """Instantiate an AbstractRequest instance."""
        self.__options = {}
        self.id = None  # pylint:disable=invalid-name
        self.__uriBase = ""

    @classmethod
    def makeOptions(cls, options):
        """Make the request options.

        Returns a string containing the concatenated values of all key/value
        pairs for the options defined in dict options

        Args:
          options (list): A list of options to turn into an option string

        Returns:
          str: The options strings
        """
        optionStr = ''
        if options:
            options = ['%s=%s' % (n, str(v)) if v else None
                       for n, v in list(options.items())]
            optionStr += '&'.join([_f for _f in options if _f])
        return optionStr

    def getUriPathAndOptions(self, session):
        """Get the uri path and options.

        Returns the full URI path and options portion of the URL that will be
        used in a query

        Args:
          session (cobra.mit.session.AbstractSession): The session object which
            contains information needed to build the URI

        Returns:
          str: The URI and options strings
        """
        return "%s.%s%s%s" % (self.uriBase, session.formatStr,
                              '?' if self.options else '', self.options)

    def getHeaders(self, session, data=None):
        """Get the headers for the session.

        The data may be needed if a signature is needed to be calculated for
        a transaction.

        Args:
          session (cobra.mit.session.AbstractSession): The session
            the headers should be for.
          data (str, optional): The data for the request.  The default is None

        Returns:
          dict: A dictionary with the headers for the session.
        """
        uriPathandOptions = self.getUriPathAndOptions(session)
        # Data is needed for CertSession where the payload is used to calculate
        # a signature.
        return session.getHeaders(uriPathandOptions, data)

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this abstract request as a string
            joined by &'s.
        """
        return AbstractRequest.makeOptions(self.__options)

    @property
    def id(self):  # pylint:disable=invalid-name
        """Get the id.

        Returns:
           str: The id for this request.
        """
        return self.__options.get('_dc', None)

    @id.setter
    def id(self, value):  # pylint:disable=invalid-name
        """Set the id.

        Args:
          value (str): The id to use for this request.
        """
        self.__options['_dc'] = value

    @property
    def uriBase(self):
        """Get the base uri.

        Returns:
          str: A string representing the base URI for this request.
        """
        return self.__uriBase

    @uriBase.setter
    def uriBase(self, value):
        """Set the base uri.

        Args:
          value (str): The base uri for this request.
        """
        self.__uriBase = value


class AbstractQuery(AbstractRequest):

    """Abstract base class for a query.

    Attributes:
      options (str): The HTTP request query string for this object - readonly

      propInclude (str): the current response property include filter.
        This filter can be used to specify the properties that should be
        included in the response.  Valid values are:

        * _all_
        * naming-only
        * config-explicit
        * config-all
        * config-only
        * oper

      subtreePropFilter (str): The response subtree filter can be used to limit
        what is returned in a subtree response by property values

      subtreeClassFilter (str): The response subtree class filter can be used
        to filter a subtree response down to one or more classes.  Setting this
        can be done with either a list or a string, the value is always stored
        as a comma separated string.

      subtreeInclude (str): The response subtree include filter can be used to
        limit the response to a specific type of information from the subtree,
        these include:

        * audit-logs
        * event-logs
        * faults
        * fault-records
        * health
        * health-records
        * relations
        * stats
        * tasks
        * count
        * no-scoped
        * required

      queryTarget (str): The query target filter can be used to specify what
        part of the MIT to query.  You can query:

        * self - The object itself
        * children - The children of the object
        * subtree - All the objects lower in the heirarchy

      classFilter (str): The target subtree class filter can be used to specify
        which subtree class to filter by.  You can set this using a list or
        a string.  The value is always stored as a comma separated string.

      propFilter (str): The query target property filter can be used to limit
        which objects are returned based on the value that is set in the
        specific property within those objects.

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      replica (int): The replica option can direct a query to a specific
        replica.  The possible values are:

        * 1
        * 2
        * 3

      orderBy (list or str): Request that the results be ordered in a certain
        way.  This can be a list of property sort specifiers or a comma
        separated string. An example sort specifier: 'aaaUser.name|desc'.

      pageSize (int): Request that the results that are returned are limited
        to a certain number, the pageSize.

      page (int): Return a given 'page' from a paginated result. Pages
        starts from 0
        Example:
          # returns the second sets of MO of 10 entries.
          pageSize=10, page=1

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self):
        """Instantiate an AbstractQuery instance."""
        super(AbstractQuery, self).__init__()
        self.__options = {}

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this abstract query as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(AbstractQuery, self).options] if _f])

    @property
    def propInclude(self):
        """Get the property include.

        Returns:
          str: The property include (rsp-prop-include) value.
        """
        return self.__options.get('rsp-prop-include', None)

    @propInclude.setter
    def propInclude(self, value):
        """Set the property include value.

        Args:
          value (str): The value to set the property include to.  Valid values
            are:

            * _all_
            * naming-only
            * config-explicit
            * config-all
            * config-only
            * oper

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'_all_', 'naming-only', 'config-explicit',
                         'config-all', 'config-only', 'oper'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-prop-include'] = value

    @property
    def subtreePropFilter(self):
        """Get the subtree property filter.

        Returns:
          str: The subtree property filter (rsp-subtree-filter) value.
        """
        return self.__options.get('rsp-subtree-filter', None)

    @subtreePropFilter.setter
    def subtreePropFilter(self, pFilter):
        """Set the subtree property filter.

        Args:
          pFilter (str): The subtree property filter.
        """
        self.__options['rsp-subtree-filter'] = str(pFilter)

    @property
    def subtreeClassFilter(self):
        """Get the the subtree class filter.

        Returns:
          str: The subtree class filter (rsp-subtree-class)
        """
        return self.__options.get('rsp-subtree-class', None)

    @subtreeClassFilter.setter
    def subtreeClassFilter(self, value):
        """Set the subtree class filter.

        Args:
          value (str or list of str):  A list of subtree class filter strings
            or a string for the subtree class filter.
        """
        if isinstance(value, list):
            value = ','.join(value)
        self.__options['rsp-subtree-class'] = value

    @property
    def subtreeInclude(self):
        """Get the subtree include.

        Returns:
          str: The subtree include (rsp-subtree-include) value.
        """
        return self.__options.get('rsp-subtree-include', None)

    @subtreeInclude.setter
    def subtreeInclude(self, value):
        """Set the subtree include.

        Args:
          value (str):  The subtree include value.  Valid values are:

            * audit-logs
            * event-logs
            * faults
            * fault-records
            * health
            * health-rcords
            * deployment-records
            * relations
            * stats
            * tasks
            * count
            * no-scoped
            * required

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'audit-logs', 'event-logs', 'faults', 'fault-records',
                         'health', 'health-records', 'deployment-records',
                         'relations', 'stats', 'tasks', 'count', 'no-scoped',
                         'required'}
        allValues = value.split(',')
        for val in allValues:
            if val not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['rsp-subtree-include'] = value

    @property
    def queryTarget(self):
        """Get the query target.

        Returns:
          str: The query target (query-target).
        """
        return self.__options.get('query-target', None)

    @queryTarget.setter
    def queryTarget(self, value):
        """Set the query target.

        Args:
          value (str): The query target value.  The valid values are:

            * self
            * children
            * subtree

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'self', 'children', 'subtree'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['query-target'] = value

    @property
    def classFilter(self):
        """Get the class filter.

        Returns:
          str: The class filter (target-subtree-class)
        """
        return self.__options.get('target-subtree-class', None)

    @classFilter.setter
    def classFilter(self, value):
        """Set the class filter.

        Args:
          value (str or list of strings): The class filter value as either a
            string or a list of strings.
        """
        if not isinstance(value, list):
            value = value.split(',')

        value = [name.replace('.', '') for name in value]
        value = ','.join(value)
        self.__options['target-subtree-class'] = value

    @property
    def propFilter(self):
        """Get the the property filter.

        Returns:
          str: The property filter (query-target-filter)
        """
        return self.__options.get('query-target-filter', None)

    @propFilter.setter
    def propFilter(self, pFilter):
        """Set the property filter.

        Args:
          pFilter (str): The value the property filter should be set to.
        """
        self.__options['query-target-filter'] = str(pFilter)

    @property
    def subtree(self):
        """Get the subtree.

        Returns:
          str: The subtree specifier (rsp-subtree).
        """
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        """Set the subtree specifier.

        Args:
          value (str): The subtree value can be:

            * no
            * children
            * full

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'no', 'children', 'full'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value

    @property
    def replica(self):
        """Get the replica.

        Returns:
          int: The replica option to be set on this query (replica).
        """
        return self.__options.get('replica', None)

    @replica.setter
    def replica(self, value):
        """Set the replica value.

        Args:
          value (int): The replica value to set.  Valid values are: 1, 2 or 3.

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = set([1, 2, 3])
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['replica'] = value

    @property
    def orderBy(self):
        """Get the orderBy sort specifiers string.

        Returns:
          str: The order-by string of sort specifiers.
        """
        return self.__options.get('order-by', None)

    @orderBy.setter
    def orderBy(self, sortSpecifiers):
        """Set the orderBy sort specifiers.

        Args:
          sortSpecifiers (str or list of str): A list of sort specifier strings
            or a comma separated string of sort specifiers.
        """
        if isinstance(sortSpecifiers, list):
            sortSpecifiers = ','.join(sortSpecifiers)
        self.__options['order-by'] = sortSpecifiers

    @property
    def pageSize(self):
        """Get the pageSize value.

        Returns:
          int: The number of results to be returned by a query.
        """
        return self.__options.get('page-size', None)

    @pageSize.setter
    def pageSize(self, pageSize):
        """Set the pageSize value.

        Args:
          pageSize (int): The number of results to be returned by a query.
        """
        try:
            numVal = int(pageSize)
        except:
            raise ValueError('{} pageSize needs to be an integer'.format(pageSize))
        self.__options['page-size'] = str(numVal)

    @property
    def page(self):
        """Get the page value.

        Returns:
          int: The number of the page returned in the query.
        """
        return self.__options.get('page', None)

    @page.setter
    def page(self, value):
        """Set the page value.

        Args:
          page (int): The position in the query which should be retrieved.
        """
        try:
            numVal = int(value)
        except:
            raise ValueError('{} page needs to be an integer'.format(value))
        self.__options['page'] = str(numVal)


class LoginRequest(AbstractRequest):

    """LoginRequest for standard user/password based authentication."""

    def __init__(self, user, password):
        """Instantiate a LoginRequest instance."""
        super(LoginRequest, self).__init__()
        self.user = user
        self.password = password
        self.uriBase = '/api/aaaLogin.json'

    @property
    def data(self):
        """Get the data.

        Currently only JSON is supported.

        Returns:
          str: The data that will be committed as a JSON string.
        """
        userJson = {
            'aaaUser': {
                'attributes': {
                    'name': self.user,
                    'pwd': self.password
                }
            }
        }
        # Keys are sorted because the APIC REST API requires the attributes
        # to come first.
        return json.dumps(userJson, sort_keys=True)

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request.

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        kwargs = {
            'headers': self.getHeaders(session, self.data),
            'verify': session.secure,
            'data': self.data,
            'timeout': session.timeout,
            'allow_redirects': False
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.uriBase


class ListDomainsRequest(AbstractRequest):

    """A class to get the possible security domains prior to login."""

    def __init__(self):
        """Instantiate a ListDomainsRequest instance."""
        super(ListDomainsRequest, self).__init__()
        self.uriBase = '/api/aaaListDomains.json'

    def getUrl(self, session):
        """Get the URL containing all the options if any.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this request.

        Returns:
          str: The url
        """
        return session.url + self.uriBase


class RefreshRequest(AbstractRequest):

    """Session refresh request.

    Does standard user/password based re-authentication.
    """

    def __init__(self, cookie):
        """Instantiate a RefreshRequest instance."""
        super(RefreshRequest, self).__init__()
        self.cookie = cookie
        self.uriBase = '/api/aaaRefresh.json'

    def getUrl(self, session):
        """Get the URL containing all the  options if any.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this request.

        Returns:
          str: The url
        """
        return session.url + self.uriBase


class FwUploadRequest(AbstractRequest):

    """Directly upload firmware to the APIC from the localhost.

    This requires MoDirectory.commit() to be called on the instance of this
    class.  For example:

        >>> from cobra.mit.access import MoDirectory
        >>> from cobra.mit.session import LoginSession
        >>> from cobra.mit.request import FwUploadRequest
        >>> session = LoginSession('https://10.1.1.1', 'admin', 'pas$w0rd')
        >>> modir = MoDirectory(session)
        >>> firmware = '/users/username/aci-apic-dk9.1.1.0e.iso'
        >>> fwReq = FwUploadRequest(firware)
        >>> modir.commit(fwReq)

    .. note::
       This is likely to be very slow due to an issue with httplib in Python.
       The httplib library has hardset the block size to 8192 bytes.
    """

    def __init__(self, uploadFile):
        super(FwUploadRequest, self).__init__()
        self._uploadFile = uploadFile
        self.uriBase = '/fwupload/'

    @property
    def uploadFile(self):
        """Get the uploadFile attribute."""
        return self._uploadFile

    @property
    def data(self):
        """Get the data.

        Returns:
          str: The data that will be committed.
        """
        return open(self.uploadFile, 'rb')

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request.

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        kwargs = {
            'headers': self.getHeaders(session),
            'verify': session.secure,
            'files': {
                'file': self.data
            }
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

class DnQuery(AbstractQuery):

    """Query based on distinguished name (Dn).

    Attributes:
      options (str): The HTTP request query string string for this DnQuery
        object - readonly

      dnStr (str): The base dn string for this DnQuery object - readonly

      propInclude (str): the current response property include filter.
        This filter can be used to specify the properties that should be
        included in the response.  Valid values are:

        * _all_
        * naming-only
        * config-explicit
        * config-all
        * config-only
        * oper

      subtreePropFilter (str): The response subtree filter can be used to limit
        what is returned in a subtree response by property values

      subtreeClassFilter (str): The response subtree class filter can be used
        to filter a subtree response down to one or more classes.  Setting this
        can be done with either a list or a string, the value is always stored
        as a comma separated string.

      subtreeInclude (str): The response subtree include filter can be used to
        limit the response to a specific type of information from the subtree,
        these include:

        * audit-logs
        * event-logs
        * faults
        * fault-records
        * health
        * health-records
        * relations
        * stats
        * tasks
        * count
        * no-scoped
        * required

      queryTarget (str): The query target filter can be used to specify what
        part of the MIT to query.  You can query:

        * self - The object itself
        * children - The children of the object
        * subtree - All the objects lower in the heirarchy

      classFilter (str): The target subtree class filter can be used to specify
        which subtree class to filter by.  You can set this using a list or
        a string.  The value is always stored as a comma separated string.

      propFilter (str): The query target property filter can be used to limit
        which objects are returned based on the value that is set in the
        specific property within those objects.

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      orderBy (list or str): Request that the results be ordered in a certain
        way.  This can be a list of property sort specifiers or a comma
        separated string. An example sort specifier: 'aaaUser.name|desc'.

      pageSize (int): Request that the results that are returned are limited
        to a certain number, the pageSize.

      replica (int): The replica option can direct a query to a specific
        replica.  The possible values are:

        * 1
        * 2
        * 3

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn):
        """Initialize a DnQuery object.

        Args:
          dn (str or cobra.mit.naming.Dn): The Dn to query
        """
        super(DnQuery, self).__init__()
        self.__dnStr = str(dn)
        self.__options = {}
        self.uriBase = "/api/mo/%s" % self.__dnStr

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this dn queryas a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(DnQuery, self).options] if _f])

    @property
    def dnStr(self):
        """Get the dn string.

        Returns:
          str: The dn string for this dn query.
        """
        return self.__dnStr

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class ClassQuery(AbstractQuery):

    """Query based on class name.

    Attributes:
      options (str): The HTTP request query string string for this ClassQuery
        object - readonly

      className (str): The className to query for - readonly

      propInclude (str): the current response property include filter.
        This filter can be used to specify the properties that should be
        included in the response.  Valid values are:

        * _all_
        * naming-only
        * config-explicit
        * config-all
        * config-only
        * oper

      subtreePropFilter (str): The response subtree filter can be used to limit
        what is returned in a subtree response by property values

      subtreeClassFilter (str): The response subtree class filter can be used
        to filter a subtree response down to one or more classes.  Setting this
        can be done with either a list or a string, the value is always stored
        as a comma separated string.

      subtreeInclude (str): The response subtree include filter can be used to
        limit the response to a specific type of information from the subtree,
        these include:

        * audit-logs
        * event-logs
        * faults
        * fault-records
        * health
        * health-records
        * relations
        * stats
        * tasks
        * count
        * no-scoped
        * required

      queryTarget (str): The query target filter can be used to specify what
        part of the MIT to query.  You can query:

        * self - The object itself
        * children - The children of the object
        * subtree - All the objects lower in the heirarchy

      classFilter (str): The target subtree class filter can be used to specify
        which subtree class to filter by.  You can set this using a list or
        a string.  The value is always stored as a comma separated string.

      propFilter (str): The query target property filter can be used to limit
        which objects are returned based on the value that is set in the
        specific property within those objects.

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      orderBy (list or str): Request that the results be ordered in a certain
        way.  This can be a list of property sort specifiers or a comma
        separated string. An example sort specifier: 'aaaUser.name|desc'.

      pageSize (int): Request that the results that are returned are limited
        to a certain number, the pageSize.

      replica (int): The replica option can direct a query to a specific
        replica.  The possible values are:

        * 1
        * 2
        * 3

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, className):
        """Initialize a ClassQuery instance.

        Args:
          className (str): The className to query for
        """
        super(ClassQuery, self).__init__()
        self.__className = className.replace('.', '')
        self.__options = {}
        self.uriBase = "/api/class/%s" % self.className

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this class query as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(ClassQuery, self).options] if _f])

    @property
    def className(self):
        """Get the class name.

        Returns:
          str: The class name for this class query
        """
        return self.__className

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TraceQuery(AbstractQuery):

    """Trace Query using a base Dn and a target class.

    Attributes:
      options (str): The HTTP request query string string for this TraceQuery
        object - readonly

      targetClass (str): The targetClass for this trace query

      dnStr (str): The base Dn string for this trace query

      propInclude (str): the current response property include filter.
        This filter can be used to specify the properties that should be
        included in the response.  Valid values are:

        * _all_
        * naming-only
        * config-explicit
        * config-all
        * config-only
        * oper

      subtreePropFilter (str): The response subtree filter can be used to limit
        what is returned in a subtree response by property values

      subtreeClassFilter (str): The response subtree class filter can be used
        to filter a subtree response down to one or more classes.  Setting this
        can be done with either a list or a string, the value is always stored
        as a comma separated string.

      subtreeInclude (str): The response subtree include filter can be used to
        limit the response to a specific type of information from the subtree,
        these include:

        * audit-logs
        * event-logs
        * faults
        * fault-records
        * health
        * health-records
        * relations
        * stats
        * tasks
        * count
        * no-scoped
        * required

      queryTarget (str): The query target filter can be used to specify what
        part of the MIT to query.  You can query:

        * self - The object itself
        * children - The children of the object
        * subtree - All the objects lower in the heirarchy

      classFilter (str): The target subtree class filter can be used to specify
        which subtree class to filter by.  You can set this using a list or
        a string.  The value is always stored as a comma separated string.

      propFilter (str): The query target property filter can be used to limit
        which objects are returned based on the value that is set in the
        specific property within those objects.

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      orderBy (list or str): Request that the results be ordered in a certain
        way.  This can be a list of property sort specifiers or a comma
        separated string. An example sort specifier: 'aaaUser.name|desc'.

      pageSize (int): Request that the results that are returned are limited
        to a certain number, the pageSize.

      replica (int): The replica option can direct a query to a specific
        replica.  The possible values are:

        * 1
        * 2
        * 3

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn, targetClass):
        """Initialize a TraceQuery instance.

        Args:
          dn (str or cobra.mit.naming.Dn): The base Dn for this query

          targetClass (str): The target class for this query
        """
        super(TraceQuery, self).__init__()
        self.__options = {}
        self.__dnStr = str(dn)
        self.targetClass = targetClass
        self.uriBase = "/api/trace/%s" % self.dnStr

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this trace query as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(TraceQuery, self).options] if _f])

    @property
    def targetClass(self):
        """Get the target class.

        Returns:
          str: The string representing the target class for this trace query.
        """
        return self.__options.get('target-class', None)

    @targetClass.setter
    def targetClass(self, value):
        """Set the target class.

        Args:
          value(str): The string representing the target class for this trace
            query.
        """
        self.__options['target-class'] = value.replace('.', '')

    @property
    def dnStr(self):
        """Get the base dn string.

        Returns:
          str: The string representing the base Dn for this trace query.
        """
        return self.__dnStr

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TagsRequest(AbstractRequest):

    """Hybrid query and request for tags.

    This class does both setting of tags (request) and retrieving of tags
    (query).

    Attributes:
      options (str): The HTTP request query string string for this TagsRequest
        object - readonly

      data (str): The payload for this request in JSON format - readonly

      dnStr (str): The base Dn for this request/query - readonly

      add (None or str or list): The tag(s) to add, default is None

      remove (None or str or list): The tag(s) to remove, default is None

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn, add=None, remove=None):
        """Initialize a tags query/request object.

        Args:
          dn (str or cobra.mit.naming.Dn): The base Dn for this request/query

          add (None or str or list): The tag(s) to add, default is None
          remove (None or str or list): The tag(s) to remove, default is None
        """
        self.__options = {}
        super(TagsRequest, self).__init__()
        self.__dnStr = str(dn)
        self.uriBase = "/api/tag/mo/%s" % self.__dnStr
        self.add = [] if add is None else add
        self.remove = [] if remove is None else remove

    @property
    def data(self):  # pylint:disable=no-self-use
        """Get the data.

        Currently only JSON is supported

        Returns:
          str: The data that will be committed as a JSON string.
        """
        return str({})

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this tags request as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(TagsRequest, self).options] if _f])

    @property
    def dnStr(self):
        """Get the dn string.

        Returns:
          str: The string representing the Dn that the tags will be committed
            to.
        """
        return self.__dnStr

    @property
    def remove(self):
        """Get the remove string.

        Returns:
          str: The string of tags that will be removed by this request.
        """
        return self.__options['remove']

    @remove.setter
    def remove(self, tags):
        """Set the remove string.

        Args:
          tags (list or str): The tags to remove via this tags request as a
            list or comma separated string.
        """
        tags = self._get_tags_string(tags)
        self.__options['remove'] = tags

    @property
    def add(self):
        """Get the add string.

        Returns:
          str: The string of tags that will be added by this request.
        """
        return self.__options['add']

    @add.setter
    def add(self, tags):
        """Set the add string.

        Args:
          tags (list or str): The tags to add via this tags request as a list
            or comma separated string.
        """
        tags = self._get_tags_string(tags)
        self.__options['add'] = tags

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request.

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        kwargs = {
            'headers': self.getHeaders(session, self.data),
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

    @staticmethod
    def _get_tags_string(value):
        """Get the tags string.

        Args:
          value (list or str): A list of tags or a string of tags comma
             separated.

        Raises:
          ValueError: If the value is not a list or a string.

        Returns:
          str: The tags string.
        """
        if isinstance(value, list):
            value = ','.join(value)
        elif not isinstance(value, str):
            raise ValueError("add or remove should be a list or a string " +
                             "{0}".format(type(value)))
        return value


class AliasRequest(AbstractRequest):

    """Hybrid query and request for alias support.

    This class does both setting of aliases (request) and retrieving of aliases
    (query).

    Attributes:
      options (str): The HTTP request query string string for this AliasRequest
        object - readonly

      data (str): The payload for this request in JSON format - readonly

      dnStr (str): The base Dn for this request/query - readonly

      alias (None or str): The alias to be set, if set to None, the alias is
        cleared

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn, alias=None):
        """Instantiate an AliasRequest instance."""
        self.__options = {}
        super(AliasRequest, self).__init__()
        self.__dnStr = str(dn)
        self.uriBase = "/api/alias/mo/%s" % self.__dnStr
        self.alias = alias

    @property
    def data(self):  # pylint:disable=no-self-use
        """Get the data.

        Currently only JSON is supported.

        Returns:
          str: The data that will be committed as a JSON string.
        """
        return str({})

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this alias request as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(AliasRequest, self).options] if _f])

    @property
    def dnStr(self):
        """Get the dnStr.

        Returns:
          str: The dn string for this alias request.
        """
        return self.__dnStr

    @property
    def alias(self):
        """Get the alias.

        Returns:
          str: The alias if it is set, otherwise an empty string.
        """
        return self.__options['set']

    @alias.setter
    def alias(self, value):
        """Set the alias.

        Args:
          value (str): The value to set the alias to.  If the value is None or
            an empty string, the alias is cleared.
        """
        if value is None or value == "":
            self.__options['clear'] = "yes"
        else:
            self.__options['clear'] = ""
        self.__options['set'] = value

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request.

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        kwargs = {
            'headers': self.getHeaders(session, self.data),
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

    def clear(self):
        """Clear the alias."""
        self.__options['set'] = ""
        self.__options['clear'] = "yes"


class ConfigRequest(AbstractRequest):

    """Change the configuration.

    :py:func:`cobra.mit.access.MoDirectory.commit` function uses this class.

    Attributes:
      options (str): The HTTP request query string string for this
        ConfigRequest object - readonly

      data (str): The payload for this request in JSON format - readonly

      xmldata (str): The payload for this request in XML format - readonly

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self):
        """Initialize a ConfigRequest instance."""
        super(ConfigRequest, self).__init__()
        self.__options = {}
        self.__ctxRoot = None
        self.__configMos = {}
        self.__rootMo = None
        self.uriBase = "/api/mo"

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this config request as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(ConfigRequest, self).options] if _f])

    @property
    def data(self):
        """Get the data as JSON.

        Raises:
          CommitError: If no Mo's have been added to this config request.

        Returns:
          str: The data that will be committed as a JSON string.
        """
        if self.getRootMo() is None:
            raise CommitError(0, "No mos in config request")

        return toJSONStr(self.getRootMo())

    @property
    def xmldata(self):
        """Get the data as XML.

        Raises:
          CommitError: If no Mo's ahve been added to this config request.

        Returns:
          str: The data as a XML string.
        """
        if self.getRootMo() is None:
            raise CommitError(0, "No mos in config request")

        return toXMLStr(self.getRootMo())

    @property
    def subtree(self):
        """Get the subtree.

        Returns:
          str: The subtree specifier.
        """
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        """Set the subtree specifier.

        Args:
          value (str): The subtree value can be:

            * no
            * full
            * modified

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'no', 'full', 'modified'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request.

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        data = self.xmldata if session.formatStr == 'xml' else self.data
        kwargs = {
            'headers': self.getHeaders(session, data),
            'verify': session.secure,
            'timeout': session.timeout,
            'data': str(data)
        }
        return kwargs

    def addMo(self, mo):
        """Add a managed object (MO) to the configuration request.

        Args
          mo (cobra.mit.mo.Mo): The managed object to add

        Raises:
          ValueError: If the context root of the MO is not allowed. This can
            happen if the MO being added does not have a common context root
            with the MOs that are already added to the configuration request
        """
        moCtx = mo.contextRoot
        if moCtx is None:
            raise ValueError('mo context not found for {0}'.format(str(mo.dn)))
        if not self.__ctxRoot:
            self.__ctxRoot = moCtx
        elif moCtx != self.__ctxRoot:
            raise ValueError('mo context "%s" not allowed for request "%s"' %
                             (mo.meta.moClassName,
                              self.__ctxRoot.moClassName))
        self.__configMos[mo.dn] = mo
        self.__rootMo = None

    def removeMo(self, mo):
        """Remove a managed object (MO) from the configuration request.

        Args:
          mo (cobra.mit.mo.Mo): The managed object to add
        """
        del self.__configMos[mo.dn]
        self.__rootMo = None
        if len(self.__configMos) == 0:
            self.__ctxRoot = None

    def hasMo(self, dn):
        """Check if the configuration request has a specific MO.

        Args:
        dn (str): The distinguished name of the mo to check

        Returns (bool): True if the MO is in the configuration request,
          otherwise False
        """
        return dn in self.__configMos

    def getRootMo(self):
        """Get the Root Mo for this configuration request.

        Returns:
          None or cobra.mit.mo.Mo: The root Mo for the config request
        """
        def addDescendantMo(rMo, descendantMo):
            """Add a descendant to a root Mo (rMo).

            Args:
              rMo (cobra.mit.mo.Mo): The root Mo to add the descendant to.
              descendantMo (cobra.mit.mo.Mo): The descendant to add to the root
                Mo.
            """
            rDn = rMo.dn
            descendantDn = descendantMo.dn
            parentDn = descendantDn.getParent()
            while rDn != parentDn:
                # This is a descendant.  Make the parent mo.
                parentMo = ConfigRequest.__getMoForDnInFlatTree(parentDn,
                                                                flatTreeDict)
                # pylint:disable=protected-access
                parentMo._attachChild(descendantMo)
                descendantMo = parentMo
                parentDn = parentDn.getParent()
            rMo._attachChild(descendantMo)  # pylint:disable=protected-access

        if self.__rootMo:
            return self.__rootMo

        if not self.__configMos:
            return None

        # This dict stores all entries added to the tree. Fast lookups
        flatTreeDict = {}
        dns = list(self.__configMos.keys())
        rootDn = Dn.findCommonParent(dns)
        configMos = dict(self.__configMos)

        # Check if the the root is in the list of MOs to be configure.
        # If it is there, remove it, else create a new MO, but in any case
        # add the MO to the flat tree dictionary for further lookups.
        rootMo = configMos.pop(rootDn) if rootDn in configMos else None
        rootMo = ConfigRequest.__getMoForDnInFlatTree(rootDn, flatTreeDict,
                                                      rootMo)

        # Add the rest of the mos to the root.
        childMos = sorted(list(configMos.values()), key=lambda x: x.dn)
        for childMo in childMos:
            addDescendantMo(rootMo, childMo)

        self.__rootMo = rootMo
        return rootMo

    def getUriPathAndOptions(self, session):
        """Get the full URI path and options portion of the URL.

        Args:
          session (cobra.mit.session.AbstractSession): The session object which
            contains information needed to build the URI

        Returns:
          str: The URI and options string
        """
        rootMo = self.getRootMo()
        if rootMo is None:
            return None
        dnStr = str(rootMo.dn)
        return "%s/%s.%s%s%s" % (self.uriBase, dnStr, session.formatStr,
                                 '?' if self.options else '', self.options)

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

    @staticmethod
    def __getMoForDnInFlatTree(dn, flatTree, mo=None):
        """Check if dn is in a dictionary, create-new/use mo if is not found.

        This method lookup for the given dn in a tree, if there is not any
        entry for that dn, it use the given mo or it creates a new mo.
        """
        return flatTree.setdefault(dn, mo if mo else
                                   ConfigRequest.__makeMoFromDn(dn))

    @staticmethod
    def __makeMoFromDn(dn):
        """Make a managed object from a Dn object.

        Args:
          dn (cobra.mit.naming.Dn): The Dn to build an Mo from.

        Returns:
          cobra.mit.mo.Mo: The managed object that the dn represented.
        """
        klass = dn.moClass
        namingVals = list(dn.rn().namingVals)
        pDn = dn.getParent()
        return klass(pDn, *namingVals)


class MultiQuery(AbstractQuery):

    """Perform a multiquery.

    Attributes:
      options (str): The HTTP request query string string for this MultiQuery
        object - readonly

      target (str): The target for this MultiQuery - readonly

      propInclude (str): the current response property include filter.
        This filter can be used to specify the properties that should be
        included in the response.  Valid values are:

        * _all_
        * naming-only
        * config-explicit
        * config-all
        * config-only
        * oper

      subtreePropFilter (str): The response subtree filter can be used to limit
        what is returned in a subtree response by property values

      subtreeClassFilter (str): The response subtree class filter can be used
        to filter a subtree response down to one or more classes.  Setting this
        can be done with either a list or a string, the value is always stored
        as a comma separated string.

      subtreeInclude (str): The response subtree include filter can be used to
        limit the response to a specific type of information from the subtree,
        these include:

        * audit-logs
        * event-logs
        * faults
        * fault-records
        * health
        * health-records
        * relations
        * stats
        * tasks
        * count
        * no-scoped
        * required

      queryTarget (str): The query target filter can be used to specify what
        part of the MIT to query.  You can query:

        * self - The object itself
        * children - The children of the object
        * subtree - All the objects lower in the heirarchy

      classFilter (str): The target subtree class filter can be used to specify
        which subtree class to filter by.  You can set this using a list or
        a string.  The value is always stored as a comma separated string.

      propFilter (str): The query target property filter can be used to limit
        which objects are returned based on the value that is set in the
        specific property within those objects.

      subtree (str): The response subtree filter can be used to define what
        objects you want in the response.  The possible values are:

        * no - No subtree requested
        * children - Only the children objects
        * full - A full subtree

      orderBy (list or str): Request that the results be ordered in a certain
        way.  This can be a list of property sort specifiers or a comma
        separated string. An example sort specifier: 'aaaUser.name|desc'.

      pageSize (int): Request that the results that are returned are limited
        to a certain number, the pageSize.

      replica (int): The replica option can direct a query to a specific
        replica.  The possible values are:

        * 1
        * 2
        * 3

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, target):
        """Initialize a MultiQuery instance.

        Args:
        target (str): The target for this MultiQuery
        """
        super(MultiQuery, self).__init__()
        self.__options = {}
        self.__target = target
        self.uriBase = "/api/mqapi2/%s" % self.target

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this MultiQuery request as a string
            joined by &'s.
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(MultiQuery, self).options] if _f])

    @property
    def target(self):
        """Get the target.

        Returns:
          str: The target for this MultiQuery request.
        """
        return self.__target

    def getUrl(self, session):
        """Get the URL containing all the query options.

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TroubleshootingQuery(MultiQuery):

    """Setup a troubleshooting query.

    Attributes:
      mode (str): The troubleshooting mode for this TroubleshootingQuery
        Valid values are:

        * createsession
        * interactive
        * generatereport

      options (str): The HTTP request query string for this
        TroubleshootingQuery object - readonly

      format (str): The output format.  Valid values are:

        * xml
        * json
        * txt
        * html
        * pdf

      include (str): The result include flags.
        Valid values are:

        * topo
        * services
        * stats
        * faults
        * events

      session (str): The session name.

      srcep (str): The source endpoint.

      dstep (str): The destination endpoint.

      starttime (str): The start time.

      endtime (str): The end time.
    """

    def __init__(self, target):
        """Initialize a TroubleshootingQuery instance.

        Args:
          target (str) : The target for this TroubleshootingQuery
        """
        super(TroubleshootingQuery, self).__init__('troubleshoot.%s' % target)

    @property
    def options(self):
        """Get the options.

        Returns:
          str: All the options for this abstract request as a string
            joined by &'s.
        """
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(TroubleshootingQuery, self).options]))

    @property
    def mode(self):
        """Get the mode.

        Returns:
          str: The mode for this troubleshooting request.
        """
        return self.__options.get('mode', None)

    @mode.setter
    def mode(self, value):
        """Set the mode.

        Args:
          value (str): The mode for this troubleshooting request.  Valid values
            are:

            * createsession
            * interactive
            * generatereport

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {
            'getsessiondetail', 'createsession', 'interactive',
            'getsessionslist',  'atomiccounter', 'traceroute',
            'getreportstatus',  'deletesession', 'span',
            'generatereport',   'modifysession',
            'getreportslist',   'clearreports'
        }
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['mode'] = value

    @property
    def format(self):
        """Get the format.

        Returns:
          str: The format for this troubleshooting request.
        """
        return self.__options.get('format', None)

    @format.setter
    def format(self, value):
        """Set the format.

        Args:
          value (str): The format for this troubleshooting request.  Valid
            values are:

            * xml
            * json
            * txt
            * html
            * pdf

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'xml', 'json', 'txt', 'html', 'pdf'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['format'] = value

    @property
    def include(self):
        """Get the include value.

        Returns:
          str: The include value for this troubleshooting request.
        """
        return self.__options.get('include', None)

    @include.setter
    def include(self, value):
        """Set the include property.

        Args:
          value (str): The include value.  Valid values are:

            * topo
            * services
            * stats
            * faults
            * events

        Raises:
          ValueError: If the value is not a valid value.
        """
        allowedValues = {'topo', 'services', 'stats', 'faults', 'events'}
        allValues = value.split(',')
        for val in allValues:
            if val not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['include'] = value

    @property
    def session(self):
        """Get the session.

        Returns:
          str: The session for this troubleshooting request.
        """
        return self.__options.get('session', None)

    @session.setter
    def session(self, value):
        """Set the session.

        Args:
          value (str): The session for this troubleshooting request.
        """
        self.__options['session'] = value

    @property
    def srcep(self):
        """Get the source EP.

        Returns:
          str: The source EP for this troubleshooting request.
        """
        return self.__options.get('srcep', None)

    @srcep.setter
    def srcep(self, value):
        """Set the source EP.

        Args:
          value (str): The source EP for this troubleshooting request.
        """
        self.__options['srcep'] = value

    @property
    def dstep(self):
        """Get the destination EP.

        Returns:
          str: The destination EP for this troubleshooting request.
        """
        return self.__options.get('dstep', None)

    @dstep.setter
    def dstep(self, value):
        """Set the destination EP.

        Args:
          value (str): The destination EP for this troubleshooting request.
        """
        self.__options['dstep'] = value

    @property
    def starttime(self):
        """Get the start time.

        Returns:
          str: The start time for the troubleshooting request.
        """
        return self.__options.get('starttime', None)

    @starttime.setter
    def starttime(self, value):
        """Set the start time.

        Args:
          value (str): The start time for the troubleshooting request.
        """
        self.__options['starttime'] = value

    @property
    def endtime(self):
        """Get the end time.

        Returns:
          None: If the end time is not set.
          str: The end time for the troubleshooting request if it is set.
        """
        return self.__options.get('endtime', None)

    @endtime.setter
    def endtime(self, value):
        """Set the endtime.

        Args:
          value (str): The end time for a troubleshooting request.
        """
        self.__options['endtime'] = value

    @property
    def sessionurl(self):
        """Return the sessionurl.

        Returns:
          str: The session URL.
        """
        return self.__options.get('sessionurl', None)

    @sessionurl.setter
    def sessionurl(self, value):
        """Set the sessionurl.

        Args:
          value (str): The session url.
        """
        self.__options['sessionurl'] = value

    def setCustomArgument(self, option, value):
        """Set a custom option to a specific value.

        Args:
          option (str): The option to set.
          value (str): The value to set the option to.
        """
        self.__options[arg] = value
        

class RestError(Exception):

    """Exceptions that occur due to REST API errors.

    Attributes:
      error (int): The REST error code for the exception
      reason (str): The reason string for the exception
      httpCode (int): The HTTP response code
    """

    def __init__(self, errorCode, reasonStr, httpCode):
        """Initialize a RestError instance.

        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        super(RestError, self).__init__(reasonStr)
        self.error = errorCode
        self.reason = reasonStr
        self.httpCode = httpCode

    def __str__(self):
        """Implement str()."""
        return self.reason


class CommitError(RestError):

    """Exceptions that occur when trying to commit changes.

    Attributes:
      reason (str): The reason string for the exception

      error (int): The REST error code for the exception

      httpCode (int): The HTTP response code
    """

    def __init__(self, errorCode, reasonStr, httpCode=None):
        """Initialize a CommitError instance.

        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        super(CommitError, self).__init__(errorCode, reasonStr, httpCode)


class QueryError(RestError):

    """Exceptions that occur during queries.

    Attributes:
      reason (str): The reason string for the exception

      error (int): The REST error code for the exception

      httpCode (int): The HTTP response code
    """

    def __init__(self, errorCode, reasonStr, httpCode=None):
        """Initialize a QueryError instance.

        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        super(QueryError, self).__init__(errorCode, reasonStr, httpCode)
