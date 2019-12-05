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

"""The request module for the ACI Python SDK (cobra)."""

import sys
if sys.version_info[0] == 3:
    from builtins import str
from builtins import object

#from past.builtins import basestring
#from past.builtins import cmp
from cobra.mit.naming import Dn
from .jsoncodec import toJSONStr
from .xmlcodec import toXMLStr


def filterUrl(st):
    return st.replace('+', '%2B')


class AbstractRequest(object):
    """
    AbstractRequest is the base class for all other request types, including
    AbstractQuery, ConfigRequest, UploadPackage, LoginRequest and RefreshRequest
    """

    def __init__(self):
        self.__options = {}
        self.id = None
        self.__uriBase = ""

    @classmethod
    def makeOptions(cls, options):
        """
        Returns a string containing the concatenated values of all key/value
        pairs for the options defined in dict options
        """
        optionStr = ''
        if options:
            options = ['%s=%s' % (n, str(v)) if v else None
                       for n, v in list(options.items())]
            optionStr += '&'.join([_f for _f in options if _f])
        return optionStr

    def getUriPathAndOptions(self, session):
        return "%s.%s%s%s" % (self.uriBase, session.formatStr,
                              '?' if self.options else '', filterUrl(self.options))

    @property
    def options(self):
        """
        Return the HTTP request query string string for this object
        """
        return AbstractRequest.makeOptions(self.__options)

    # property setters / getters for this class

    @property
    def id(self):
        """
        Returns the id of this query if set, else None
        """
        return self.__options.get('_dc', None)

    @id.setter
    def id(self, value):
        """
        Sets the id of this query. The id is an internal troubleshooting
        value useful for tracing the processing of a request within the cluster
        """
        self.__options['_dc'] = value

    @property
    def uriBase(self):
        return self.__uriBase

    @uriBase.setter
    def uriBase(self, value):
        self.__uriBase = value

    def getUrl(self, session):
        """
        Returns the dn query URL containing all the query options defined on
        this object
        """
        return session.url + self.getUriPathAndOptions(session)


class CheckRequestStateQuery(AbstractRequest):
    """
    Class representing a check request state query, used to query
     the state of a request in progress
    """

    def __init__(self):
        super(CheckRequestStateQuery, self).__init__()
        self.__options = {}
        self.uriBase = '/api/checkRequestState'

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(CheckRequestStateQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def requestId(self):
        """
        Returns the current requestId filter
        """
        return self.__options.get('id', None)

    @requestId.setter
    def requestId(self, value):
        """
        Sets the request id to query
        """
        self.__options['id'] = value


class DeploymentQuery(AbstractRequest):
    """
    Class to create a deployment query to find the impacted deployment entities for changes in specific dn.
    """

    def __init__(self, dn):
        """
        Args:
            dnStr (str): DN to query
        """
        super(DeploymentQuery, self).__init__()
        self.__dnStr = str(dn)
        self.__options = {'rsp-subtree-include': 'full-deployment'}
        self.uriBase = "/api/mo/%s" % self.__dnStr

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(DeploymentQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def dnStr(self):
        """
        Returns the base dnString for this DnQuery
        """
        return self.__dnStr

    @property
    def targetNode(self):
        """
        Returns the node specific information
        """
        return self.__options.get('target-node', None)

    @targetNode.setter
    def targetNode(self, value):
        """
        Args:
            value (int): id of the node
        """
        self.__options['target-node'] = value

    @property
    def targetPath(self):
        """
        Returns the path selected for the query
        """
        return self.__options.get('target-path', None)

    @targetNode.setter
    def targetPath(self, value):
        """
        Args:
            value (str): specific target path for this query
        """
        self.__options['target-path'] = value

    @property
    def includeRelations(self):
        """
        Returns the path selected for the query
        """
        return self.__options.get('include-relns', None)

    @includeRelations.setter
    def includeRelations(self, value):
        """
        Args:
            value (str): specific target path for this query
        """
        value = 'yes' if value else 'no'
        self.__options['include-relns'] = value


class AbstractQuery(AbstractRequest):
    """
    Class representing an abstract query. The class is used by classQuery
    and Dnquery.
    """

    def __init__(self):
        super(AbstractQuery, self).__init__()
        self.__options = {}

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(AbstractQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def propInclude(self):
        """
        Returns the current response property include filter
        """
        return self.__options.get('rsp-prop-include', None)

    @propInclude.setter
    def propInclude(self, value):
        """
        Filters that can specify the properties that should be included in the
        response body
        """
        allowedValues = ['all', 'naming-only', 'config-explicit',
                         'config-all', 'config-only', 'oper']
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-prop-include'] = value

    @property
    def subtreePropFilter(self):
        """
        Returns the subtree prop filter.
        """
        return self.__options.get('rsp-subtree-filter', None)

    @subtreePropFilter.setter
    def subtreePropFilter(self, pFilter):
        """
        Returns the subtree prop filter.
        """
        self.__options['rsp-subtree-filter'] = str(pFilter)

    @property
    def subtreeClassFilter(self):
        """
        Returns the current subtree class filter.
        """
        return self.__options.get('rsp-subtree-class', None)

    @subtreeClassFilter.setter
    def subtreeClassFilter(self, value):
        """
        Returns the children of a single class.
        """
        if isinstance(value, list):
            value = ','.join(value)
        self.__options['rsp-subtree-class'] = value

    @property
    def subtreeInclude(self):
        """
        Returns the current subtree query values.
        """
        return self.__options.get('rsp-subtree-include', None)

    @subtreeInclude.setter
    def subtreeInclude(self, value):
        """
        Specifies optional values for a subtree query, including:
        *audit-logs
        *event-logs
        *faults
        *fault-records
        *ep-records
        *health
        *health-records
        *relations
        *stats
        *tasks
        *count
        *no-scoped
        *required
        *subtree
        """
        allowedValues = {'audit-logs', 'event-logs', 'faults', 'fault-records', 'ep-records',
                         'health', 'health-records', 'deployment-records', 'relations', 'stats',
                         'tasks', 'count', 'no-scoped', 'required', 'subtree'}
        allValues = value.split(',')
        for v in allValues:
            if v not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['rsp-subtree-include'] = value

    @property
    def queryTarget(self):
        """
        Returns the query type.
        """
        return self.__options.get('query-target', None)

    @queryTarget.setter
    def queryTarget(self, value):
        """
        Sets the query type. You can query the object (self), child objects
        (children), or all objects lower in the heirarchy (subtree).
        """
        allowedValues = {'self', 'children', 'subtree'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['query-target'] = value

    @property
    def classFilter(self):
        """
        Returns the current class filter type.
        """
        return self.__options.get('target-subtree-class', None)

    @classFilter.setter
    def classFilter(self, value):
        """
        Filters by a specified class.
        """

        if not isinstance(value, list):
            value = value.split(',')

        value = [name.replace('.', '') for name in value]
        value = ','.join(value)
        self.__options['target-subtree-class'] = value

    @property
    def propFilter(self):
        """
        Returns the current property filter type.
        """
        return self.__options.get('query-target-filter', None)

    @propFilter.setter
    def propFilter(self, pFilter):
        """
        Filters by a specified property value.
        """
        self.__options['query-target-filter'] = str(pFilter)

    @property
    def subtree(self):
        """
        Returns the current type of subtree filter.
        """
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        """
        Filters query values within a subtree- you can filter by MOs (children)
        or return the entire subtree (full).
        """
        allowedValues = {'no', 'children', 'full'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value

    @property
    def replica(self):
        """
        Returns the current value for the replica option.
        """
        return self.__options.get('replica', None)

    @replica.setter
    def replica(self, value):
        """
        Direct the query to a specific replica
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

    @property
    def cacheId(self):
        return self.__options.get('cache-session', None)

    @cacheId.setter
    def cacheId(self, value):
        if value is None and 'cache-session' in self.__options:
            del self.__options['cache-session']
            return
        try:
            numVal = int(value)
        except:
            raise ValueError('{} cache id needs to be an integer'.format(value))
        self.__options['cache-session'] = str(numVal)

    @property
    def deleteCacheId(self):
        return self.__options.get('delete-session', None)

    @deleteCacheId.setter
    def deleteCacheId(self, value):
        try:
            numVal = int(value)
        except:
            raise ValueError('{} delete cache id needs to be an integer'.format(value))
        self.__options['delete-session'] = str(numVal)


class DnQuery(AbstractQuery):
    """
    Class to create a query based on distinguished name (Dn).
    """

    def __init__(self, dn):
        """
        Args:
            dnStr (str): DN to query
        """
        super(DnQuery, self).__init__()
        self.__dnStr = str(dn)
        self.__options = {}
        self.uriBase = "/api/mo/{0}".format(self.__dnStr)

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(DnQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def dnStr(self):
        """
        Returns the base dnString for this DnQuery
        """
        return self.__dnStr

    def __hash__(self):
        url = '{0}/{1}'.format(self.__dnStr, self.options)
        return hash(url)

    # def __cmp__(self, other):
    #     thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
    #     otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
    #     return cmp(thisUrl, otherUrl)

    def __lt__(self, other):
        """Implement <."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl < otherUrl

    def __le__(self, other):
        """Implement <=."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl <= otherUrl

    def __eq__(self, other):
        """Implement ==."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl == otherUrl

    def __ne__(self, other):
        """Implement !=."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl != otherUrl

    def __gt__(self, other):
        """Implement >."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl > otherUrl

    def __ge__(self, other):
        """Implement >=."""
        thisUrl = '{0}/{1}'.format(self.__dnStr, self.options)
        otherUrl = '{0}/{1}'.format(other.dnStr, other.options)
        return thisUrl >= otherUrl


class ClassQuery(AbstractQuery):
    """
    Class to create a query based on object class.
    """

    def __init__(self, className):
        super(ClassQuery, self).__init__()
        self.__className = className.replace('.', '')
        self.__options = {}
        self.uriBase = "/api/class/{0}".format(self.className)

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(ClassQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def className(self):
        """
        Returns the className targeted by this ClassQuery
        """
        return self.__className

    def __hash__(self):
        url = '{0}/{1}'.format(self.__className, self.options)
        return hash(url)

    # def __cmp__(self, other):
    #     thisUrl = '{0}/{1}'.format(self.__className, self.options)
    #     otherUrl = '{0}/{1}'.format(other.className, other.options)
    #     return cmp(thisUrl, otherUrl)

    def __lt__(self, other):
        """Implement <."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl < otherUrl

    def __le__(self, other):
        """Implement <=."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl <= otherUrl

    def __eq__(self, other):
        """Implement ==."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl == otherUrl

    def __ne__(self, other):
        """Implement !=."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl != otherUrl

    def __gt__(self, other):
        """Implement >."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl > otherUrl

    def __ge__(self, other):
        """Implement >=."""
        thisUrl = '{0}/{1}'.format(self.__className, self.options)
        otherUrl = '{0}/{1}'.format(other.className, other.options)
        return thisUrl >= otherUrl


class TraceQuery(AbstractQuery):
    """
    Class to create a trace query using base Dn and targetClass
    """

    def __init__(self, dn, targetClass):
        super(TraceQuery, self).__init__()
        self.__options = {}
        self.__dnStr = str(dn)
        self.targetClass = targetClass
        self.uriBase = "/api/trace/%s" % self.dnStr

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(TraceQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def targetClass(self):
        """
        Returns the target class
        """
        return self.__options.get('target-class', None)

    @targetClass.setter
    def targetClass(self, value):
        """
        Sets the targetClass for this traceQuery
        """
        self.__options['target-class'] = value.replace('.', '')

    @property
    def dnStr(self):
        """
        Returns the base dnString for this DnQuery
        """
        return self.__dnStr


class TagsRequest(AbstractRequest):
    """
    Tags request to add or remove tags for a Dn.
    """

    def __init__(self, dn, add=None, remove=None):
        """
        :param dn: The Dn to do the Tags request against
        :type dn: cobra.mit.naming.Dn or str

        :param add: The comma separated string or list of tags to add
        :type add: str or list

        :param remove: The comma separated string or list of tags to remove
        :type remove: str or list
        """
        self.__options = {}
        super(TagsRequest, self).__init__()
        self.__dnStr = str(dn)
        self.uriBase = "/api/tag/mo/%s" % self.__dnStr
        self.add = [] if add is None else add
        self.remove = [] if remove is None else remove

    @property
    def data(self):
        return str({})

    @property
    def options(self):
        """
        :returns: The url options string with & prepended
        :rtype: str
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(TagsRequest, self).options] if _f])

    @property
    def dnStr(self):
        """
        :returns: The Dn string for this request
        :rtype: str
        """
        return self.__dnStr

    @property
    def remove(self):
        """
        Tags that will be removed for this TagsRequest

        :returns: String form of the tags, comma separated
        :rtype: str
        """
        return self.__options['remove']

    @remove.setter
    def remove(self, tags):
        tags = self._get_tags_string(tags)
        self.__options['remove'] = tags

    @property
    def add(self):
        """
        Tags that will be added for this TagsRequest

        :returns: String form of the tags, comma separated
        :rtype: str
        """
        return self.__options['add']

    @add.setter
    def add(self, tags):
        tags = self._get_tags_string(tags)
        self.__options['add'] = tags

    def requestargs(self, session):
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs

    @staticmethod
    def _get_tags_string(value):
        if isinstance(value, list):
            value = ','.join(value)
        elif not isinstance(value, str):
            # # TODO: PYTHON 3 TIMEBOMB basestring ##
            raise ValueError("add or remove should be a list or a string " +
                             "{0}".format(type(value)))
        return value


# Aliases are not supported at FCS.  This is added for testing only and not
# documented on purpose
class AliasRequest(AbstractRequest):
    def __init__(self, dn, alias=None):
        self.__options = {}
        super(AliasRequest, self).__init__()
        self.__dnStr = str(dn)
        self.uriBase = "/api/alias/mo/%s" % self.__dnStr
        self.alias = alias

    @property
    def data(self):
        return str({})

    @property
    def options(self):
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(AliasRequest, self).options] if _f])

    @property
    def dnStr(self):
        return self.__dnStr

    def clear(self):
        self.__options['set'] = ""
        self.__options['clear'] = "yes"

    @property
    def alias(self):
        return self.__options['set']

    @alias.setter
    def alias(self, value):
        if value is None or value == "":
            self.__options['clear'] = "yes"
        else:
            self.__options['clear'] = ""
        self.__options['set'] = value

    def requestargs(self, session):
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs


class ConfigRequest(AbstractRequest):
    """
    Class to handle configuration requests. The commit function uses this
    class.
    """

    def __init__(self):

        super(ConfigRequest, self).__init__()
        self.__options = {}
        self.__ctxRoot = None
        self.__configMos = {}
        self.__rootMo = None
        self.uriBase = "/api/mo"

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(ConfigRequest, self).options] if _f])

    @property
    def data(self):
        if self.getRootMo() is None:
            raise CommitError(0, "No mos in config request")

        return toJSONStr(self.getRootMo())

    @property
    def xmldata(self):
        if self.getRootMo() is None:
            raise CommitError(0, "No mos in config request")

        return toXMLStr(self.getRootMo())

    def requestargs(self, session):
        uriPathandOptions = self.getUriPathAndOptions(session)
        data = self.xmldata if session.formatStr == 'xml' else self.data
        headers = session.getHeaders(uriPathandOptions, data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': str(data)
        }
        return kwargs

    def addMo(self, mo):
        """
        Adds a managed object (MO) to the configuration.
        """

        self.__configMos[mo.dn] = mo
        self.__rootMo = None

    def removeMo(self, mo):
        """
        Removes a managed object (MO) from the configuration.
        """
        del self.__configMos[mo.dn]
        self.__rootMo = None
        if len(self.__configMos) == 0:
            self.__ctxRoot = None

    def hasMo(self, dn):
        """
        Verifies whether managed object (MO) is present in an uncommitted
        configuration.
        """
        return dn in self.__configMos

    @property
    def configMos(self):
        mos = [mo for mo in list(self.__configMos.values())]
        mos.sort(key=lambda xmo: str(xmo.dn), reverse=True)
        return mos

    def getRootMo(self):
        def addDescendantMo(rMo, descendantMo):
            rDn = rMo.dn
            descendantDn = descendantMo.dn
            parentDn = descendantDn.getParent()
            ConfigRequest.__getMoForDnInFlatTree(descendantDn, flatTreeDict, descendantMo)
            while rDn != parentDn:
                # This is a descendant. make the parent mo
                parentMo = ConfigRequest.__getMoForDnInFlatTree(parentDn, flatTreeDict)
                parentMo._attachChild(descendantMo)
                descendantMo = parentMo
                parentDn = parentDn.getParent()
            rMo._attachChild(descendantMo)

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
        rootMo = ConfigRequest.__getMoForDnInFlatTree(rootDn, flatTreeDict, rootMo)

        # Add the rest of the mos to the root.
        childMos = sorted(list(configMos.values()), key=lambda x: x.dn)
        for childMo in childMos:
            addDescendantMo(rootMo, childMo)

        self.__rootMo = rootMo
        return rootMo

    def getUriPathAndOptions(self, session):
        rootMo = self.getRootMo()
        if rootMo is None:
            raise CommitError(0, "No mos in config request")
        dnStr = str(rootMo.dn)
        return "%s/%s.%s%s%s" % (self.uriBase, dnStr, session.formatStr,
                                 '?' if self.options else '', self.options)

    @staticmethod
    def __getMoForDnInFlatTree(dn, flatTree, mo=None):
        """Check if dn is in a dictionary, create-new/use mo if is not found.

        This method lookup for the given dn in a tree, if there is not any
        entry for that dn, it use the given mo or it creates a new mo.
        """
        return flatTree.setdefault(dn, mo if mo else ConfigRequest.__makeMoFromDn(dn))

    @staticmethod
    def __makeMoFromDn(dn):
        klass = dn.moClass
        namingVals = list(dn.rn().namingVals)
        pDn = dn.getParent()
        return klass(pDn, *namingVals)

    # property setters / getters for this class

    @property
    def subtree(self):
        """
        Returns the current type of subtree filter.
        """
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        """
        Filters Mo values returned by the ConfigRequest. This can be the full
        tree of objects under the top level, just the modified attributes or
        none (default)
        """
        allowedValues = {'no', 'full', 'modified'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value


class MultiQuery(AbstractQuery):
    """
    Class to create a MultiQuery
    """

    def __init__(self, target):
        super(MultiQuery, self).__init__()
        self.__options = {}
        self.__target = target
        self.uriBase = "/mqapi2/%s" % self.target

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(MultiQuery, self).options] if _f])

    # property setters / getters for this class

    @property
    def target(self):
        """
        Returns the target for this MultiQuery
        """
        return self.__target


class TroubleshootingQuery(MultiQuery):
    """
    Class to create a troubleshooting query
    """

    def __init__(self, target):
        super(TroubleshootingQuery, self).__init__('troubleshoot.%s' % target)
        self.__options = {}

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(TroubleshootingQuery, self).options] if _f])

    @property
    def mode(self):
        """
        Returns the troubleshooting mode.
        """
        return self.__options.get('mode', None)

    @mode.setter
    def mode(self, value):
        """
        Sets the troubleshooting mode.
        """
        allowedValues = {'createsession', 'modifysession', 'deletesession',
                         'getsessionslist', 'interactive', 'generatereport',
                         'span', 'getreportslist', 'getreportstatus',
                         'getsessiondetail', 'clearreports', 'atomiccounter',
                         'traceroute', 'createl2session', 'latency'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['mode'] = value

    def setCustomArgument(self, arg, val):
        self.__options[arg] = val

    @property
    def format(self):
        """
        Returns the output format.
        """
        return self.__options.get('format', None)

    @format.setter
    def format(self, value):
        """
        Sets the output format.
        """
        allowedValues = {'xml', 'json', 'txt', 'html', 'pdf'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['format'] = value

    @property
    def include(self):
        """
        Returns the result include flags.
        """
        return self.__options.get('include', None)

    @include.setter
    def include(self, value):
        """
        Sets the result include flags.
        """

        allowedValues = {'topo', 'services', 'stats', 'faults', 'events', 'audits', 'fault-records', 'contracts', 'deployment-records'}
        allValues = value.split(',')
        for v in allValues:
            if v not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['include'] = value

    @property
    def action(self):
        """
        Returns the action flag.
        """
        return self.__options.get('action', None)

    @include.setter
    def action(self, value):
        """
        Sets the action flag.
        """

        allowedValues = {'start', 'stop', 'status'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['action'] = value

    @property
    def session(self):
        """
        Returns the session name.
        """
        return self.__options.get('session', None)

    @session.setter
    def session(self, value):
        """
        Sets the session name.
        """

        self.__options['session'] = value

    @property
    def srcep(self):
        """
        Returns the source endpoint.
        """
        return self.__options.get('srcep', None)

    @srcep.setter
    def srcep(self, value):
        """
        Sets the source endpoint.
        """

        self.__options['srcep'] = value

    @property
    def dstep(self):
        """
        Returns the destination endpoint.
        """
        return self.__options.get('dstep', None)

    @dstep.setter
    def dstep(self, value):
        """
        Sets the destination endpoint.
        """

        self.__options['dstep'] = value

    @property
    def srcextip(self):
        """
        Returns the source external ip address.
        """
        return self.__options.get('srcextip', None)

    @srcextip.setter
    def srcextip(self, value):
        """
        Sets the source external ip address.
        """

        self.__options['srcextip'] = value

    @property
    def dstextip(self):
        """
        Returns the destination external ip address.
        """
        return self.__options.get('dstextip', None)

    @dstextip.setter
    def dstextip(self, value):
        """
        Sets the destination external ip address.
        """

        self.__options['dstextip'] = value

    @property
    def starttime(self):
        """
        Returns the start time.
        """
        return self.__options.get('starttime', None)

    @starttime.setter
    def starttime(self, value):
        """
        Sets the start time.
        """

        self.__options['starttime'] = value

    @property
    def endtime(self):
        """
        Returns the end time.
        """
        return self.__options.get('endtime', None)

    @endtime.setter
    def endtime(self, value):
        """
        Sets the end time.
        """

        self.__options['endtime'] = value

    @property
    def sessionurl(self):
        """
        Returns the sessionurl.
        """
        return self.__options.get('sessionurl', None)

    @sessionurl.setter
    def sessionurl(self, value):
        """
        Sets the sessionurl.
        """
        self.__options['sessionurl'] = value

    @property
    def scheduler(self):
        """
        Returns the scheduler name.
        """
        return self.__options.get('scheduler', None)

    @scheduler.setter
    def scheduler(self, value):
        """
        Sets the scheduler name.
        """
        self.__options['scheduler'] = value


class Deployment(MultiQuery):
    """
    Class to create a deployment query
    """

    def __init__(self, target):
        super(Deployment, self).__init__('deployment.%s' % target)
        self.__options = {}

    @property
    def options(self):
        """
        Returns the concatenation of the class and base class options for HTTP
        request query string
        """
        return '&'.join([_f for _f in [AbstractRequest.makeOptions(
            self.__options), super(Deployment, self).options] if _f])

    @property
    def mode(self):
        """
        Returns the deployment query mode.
        """
        return self.__options.get('mode', None)

    @mode.setter
    def mode(self, value):
        """
        Sets the deployment query mode.
        """
        """
        allowedValues = {}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        """
        self.__options['mode'] = value

    def setCustomArgument(self, arg, val):
        self.__options[arg] = val


class RestError(Exception):
    def __init__(self, errorCode, reasonStr, httpCode):
        self.reason = reasonStr
        self.error = errorCode
        self.httpCode = httpCode

    def __str__(self):
        return self.reason


class CommitError(RestError):
    def __init__(self, errorCode, reasonStr, httpCode=None):
        super(CommitError, self).__init__(errorCode, reasonStr, httpCode)


class QueryError(RestError):
    def __init__(self, errorCode, reasonStr, httpCode=None):
        super(QueryError, self).__init__(errorCode, reasonStr, httpCode)
