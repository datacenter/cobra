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

from cobra.mit.naming import Dn
from cobra.internal.codec.jsoncodec import toJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr


class AbstractRequest(object):
    """Abstract base class for all other request types
    
    Attributes:
      options (str): The HTTP request query string for this object - readonly

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
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

        :param list options: A list of options to turn into an option string

        :returns: The options string
        :rtype: str
        """
        optionStr = ''
        if options:
            options = ['%s=%s' % (n, str(v)) if v else None
                       for n, v in options.items()]
            optionStr += '&'.join(filter(None, options))
        return optionStr

    def getUriPathAndOptions(self, session):
        """
        Returns the full URI path and options portion of the URL that will be
        used in a query

        :param session: The session object which contains information needed
            to build the URI
        :type session: :py:class:`cobra.mit.session.LoginSession` or
            :py:class:`cobra.mit.session.CertSession`

        :returns: The URI and options string
        :rtype: str
        """
        return "%s.%s%s%s" % (self.uriBase, session.formatStr,
                              '?' if self.options else '', self.options)

    @property
    def options(self):
        return AbstractRequest.makeOptions(self.__options)

    @property
    def id(self):
        return self.__options.get('_dc', None)

    @id.setter
    def id(self, value):
        self.__options['_dc'] = value

    @property
    def uriBase(self):
        return self.__uriBase

    @uriBase.setter
    def uriBase(self, value):
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

      replica (int): The replica option can direct a query to a specific replica.
        The possible values are:

        * 1
        * 2
        * 3
        
      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self):
        super(AbstractQuery, self).__init__()
        self.__options = {}

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(AbstractQuery, self).options]))

    @property
    def propInclude(self):
        return self.__options.get('rsp-prop-include', None)

    @propInclude.setter
    def propInclude(self, value):
        allowedValues = {'_all_', 'naming-only', 'config-explicit',
                         'config-all', 'config-only', 'oper'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-prop-include'] = value

    @property
    def subtreePropFilter(self):
        return self.__options.get('rsp-subtree-filter', None)

    @subtreePropFilter.setter
    def subtreePropFilter(self, pFilter):
        self.__options['rsp-subtree-filter'] = str(pFilter)

    @property
    def subtreeClassFilter(self):
        return self.__options.get('rsp-subtree-class', None)

    @subtreeClassFilter.setter
    def subtreeClassFilter(self, value):
        if isinstance(value, list):
            value = ','.join(value)
        self.__options['rsp-subtree-class'] = value

    @property
    def subtreeInclude(self):
        return self.__options.get('rsp-subtree-include', None)

    @subtreeInclude.setter
    def subtreeInclude(self, value):
        allowedValues = {'audit-logs', 'event-logs', 'faults', 'fault-records',
                         'health', 'health-records', 'deployment-records',
                         'relations', 'stats', 'tasks', 'count', 'no-scoped',
                         'required'}
        allValues = value.split(',')
        for v in allValues:
            if v not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['rsp-subtree-include'] = value

    @property
    def queryTarget(self):
        return self.__options.get('query-target', None)

    @queryTarget.setter
    def queryTarget(self, value):
        allowedValues = {'self', 'children', 'subtree'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['query-target'] = value

    @property
    def classFilter(self):
        return self.__options.get('target-subtree-class', None)

    @classFilter.setter
    def classFilter(self, value):
        if isinstance(value, str):
            value = value.split(',')

        value = [name.replace('.', '') for name in value]
        value = ','.join(value)
        self.__options['target-subtree-class'] = value

    @property
    def propFilter(self):
        return self.__options.get('query-target-filter', None)

    @propFilter.setter
    def propFilter(self, pFilter):
        self.__options['query-target-filter'] = str(pFilter)

    @property
    def subtree(self):
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        allowedValues = {'no', 'children', 'full'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value

    @property
    def replica(self):
        return self.__options.get('replica', None)

    @replica.setter
    def replica(self, value):
        allowedValues = set([1, 2, 3])
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['replica'] = value


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

      replica (int): The replica option can direct a query to a specific replica.
        The possible values are:

        * 1
        * 2
        * 3
        
      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn):
        """Initialize a DnQuery object
        
        Args:
          dn (str or cobra.mit.naming.Dn): The Dn to query
        """
        super(DnQuery, self).__init__()
        self.__dnStr = str(dn)
        self.__options = {}
        self.uriBase = "/api/mo/%s" % self.__dnStr

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(DnQuery, self).options]))

    @property
    def dnStr(self):
        return self.__dnStr

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class ClassQuery(AbstractQuery):
    """Query based on class name

    Attributes:
      options (str): The HTTP request query string string for this DnQuery
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

      replica (int): The replica option can direct a query to a specific replica.
        The possible values are:

        * 1
        * 2
        * 3
        
      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, className):
        """Initialize a ClassQuery instance
        
        Args:
          className (str): The className to query for
        """
        super(ClassQuery, self).__init__()
        self.__className = className.replace('.', '')
        self.__options = {}
        self.uriBase = "/api/class/%s" % self.className

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(ClassQuery, self).options]))

    @property
    def className(self):
        return self.__className

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TraceQuery(AbstractQuery):
    """Trace Query using a base Dn and a target class

    Attributes:
      options (str): The HTTP request query string string for this DnQuery
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

      replica (int): The replica option can direct a query to a specific replica.
        The possible values are:

        * 1
        * 2
        * 3
        
      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, dn, targetClass):
        """Initialize a TraceQuery instance

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
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(TraceQuery, self).options]))

    @property
    def targetClass(self):
        return self.__options.get('target-class', None)

    @targetClass.setter
    def targetClass(self, value):
        self.__options['target-class'] = value.replace('.', '')

    @property
    def dnStr(self):
        return self.__dnStr

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TagsRequest(AbstractRequest):
    """Hybrid query and request for tags

    This class does both setting of tags (request) and retriving of tags
    (query).
    
    Attributes:
      options (str): The HTTP request query string string for this DnQuery
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
        """Initialize a tags query/request object
        
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
    def data(self):
        return str({})

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(TagsRequest, self).options]))

    @property
    def dnStr(self):
        return self.__dnStr

    @property
    def remove(self):
        return self.__options['remove']

    @remove.setter
    def remove(self, tags):
        tags = self._get_tags_string(tags)
        self.__options['remove'] = tags

    @property
    def add(self):
        return self.__options['add']

    @add.setter
    def add(self, tags):
        tags = self._get_tags_string(tags)
        self.__options['add'] = tags

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

    @staticmethod
    def _get_tags_string(value):
        if isinstance(value, list):
            value = ','.join(value)
        elif not isinstance(value, basestring):
            # # TODO: PYTHON 3 TIMEBOMB basestring ##
            raise ValueError("add or remove should be a list or a string " +
                             "{0}".format(type(value)))
        return value


class AliasRequest(AbstractRequest):
    """Hybrid query and request for alias support

    This class does both setting of aliases (request) and retriving of aliases
    (query).
    
    Attributes:
      options (str): The HTTP request query string string for this DnQuery
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
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(AliasRequest, self).options]))

    @property
    def dnStr(self):
        return self.__dnStr

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
        """Get the arguments to be used by the HTTP request

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': self.data
        }
        return kwargs

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)

    def clear(self):
        """Clear the alias"""
        self.__options['set'] = ""
        self.__options['clear'] = "yes"


class ConfigRequest(AbstractRequest):
    """Change the configuration

    :py:func:`cobra.mit.access.MoDirectory.commit` function uses this class.
    
    Attributes:
      options (str): The HTTP request query string string for this DnQuery
        object - readonly

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
        """Initialize a ConfigRequest instance"""
        super(ConfigRequest, self).__init__()
        self.__options = {}
        self.__ctxRoot = None
        self.__configMos = {}
        self.__rootMo = None
        self.uriBase = "/api/mo"

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(ConfigRequest, self).options]))

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

    @property
    def subtree(self):
        return self.__options.get('rsp-subtree', None)

    @subtree.setter
    def subtree(self, value):
        allowedValues = {'no', 'full', 'modified'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['rsp-subtree'] = value

    def requestargs(self, session):
        """Get the arguments to be used by the HTTP request

        session (cobra.mit.session.AbstractSession): The session to be used to
          build the the request arguments

        Returns:
          dict: The arguments
        """
        uriPathandOptions = self.getUriPathAndOptions(session)
        data = self.xmldata if session.formatStr == 'xml' else self.data
        headers = session.getHeaders(uriPathandOptions, data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'timeout': session.timeout,
            'data': data
        }
        return kwargs

    def addMo(self, mo):
        """Add a managed object (MO) to the configuration request

        Args
          mo (cobra.mit.mo.Mo): The managed object to add

        Raises:
          ValueError: If the context root of the MO is not alowed. This can
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
        """Remove a managed object (MO) from the configuration request

        Args:
          mo (cobra.mit.mo.Mo): The managed object to add
        """
        del self.__configMos[mo.dn]
        self.__rootMo = None
        if len(self.__configMos) == 0:
            self.__ctxRoot = None

    def hasMo(self, dn):
        """Check if the configuration request has a specific MO

        Args:
        dn (str): The distinguished name of the mo to check

        Returns (bool): True if the MO is in the configuration request,
          otherwise False
        """
        return dn in self.__configMos

    def getRootMo(self):
        """Get the Root Mo for this configuration request
        
        Returns:
          None or cobra.mit.mo.Mo: The root Mo for the config request
        """
        def addDescendantMo(rMo, descendantMo):
            rDn = rMo.dn
            descendantDn = descendantMo.dn
            parentDn = descendantDn.getParent()
            while rDn != parentDn:
                # This is a descendant. make the parent mo
                parentMo = ConfigRequest.__getMoForDnInFlatTree(parentDn,
                                                                flatTreeDict)
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
        dns = self.__configMos.keys()
        rootDn = Dn.findCommonParent(dns)
        configMos = dict(self.__configMos)

        # Check if the the root is in the list of MOs to be configure.
        # If it is there, remove it, else create a new MO, but in any case
        # add the MO to the flat tree dictionary for further lookups.
        rootMo = configMos.pop(rootDn) if rootDn in configMos else None
        rootMo = ConfigRequest.__getMoForDnInFlatTree(rootDn, flatTreeDict,
                                                      rootMo)

        # Add the rest of the mos to the root.
        childMos = sorted(configMos.values(), key=lambda x: x.dn)
        for childMo in childMos:
            addDescendantMo(rootMo, childMo)

        self.__rootMo = rootMo
        return rootMo

    def getUriPathAndOptions(self, session):
        """Get the full URI path and options portion of the URL

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
        """Get the URL containing all the query options

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
        return flatTree.setdefault(dn, mo if mo else ConfigRequest.__makeMoFromDn(dn))

    @staticmethod
    def __makeMoFromDn(dn):
        klass = dn.moClass
        namingVals = list(dn.rn().namingVals)
        pDn = dn.getParent()
        return klass(pDn, *namingVals)


class MultiQuery(AbstractQuery):
    """Perform a multiquery
    
    Attributes:
      options (str): The HTTP request query string string for this DnQuery
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

      replica (int): The replica option can direct a query to a specific replica.
        The possible values are:

        * 1
        * 2
        * 3
        
      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, target):
        """Initialize a MultiQuery instance
        
        Args:
        target (str): The target for this MultiQuery
        """
        super(MultiQuery, self).__init__()
        self.__options = {}
        self.__target = target
        self.uriBase = "/api/mqapi2/%s" % self.target

    @property
    def options(self):
        return '&'.join(filter(None, [AbstractRequest.makeOptions(
            self.__options), super(MultiQuery, self).options]))

    @property
    def target(self):
        return self.__target

    def getUrl(self, session):
        """Get the URL containing all the query options

        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: The url
        """
        return session.url + self.getUriPathAndOptions(session)


class TroubleshootingQuery(MultiQuery):
    """Setup a troubleshooting query

    Attributes:
      mode (str): The troubleshooting mode for this TroubleshootingQuery
        Valid values are:

        * createsession
        * interactive
        * generatereport

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
        """
        :param target: The target for this TroubleshootingQuery
        :type target: str
        """
        super(TroubleshootingQuery, self).__init__('troubleshoot.%s' % target)


    @property
    def mode(self):
        return self.__options.get('mode', None)

    @mode.setter
    def mode(self, value):
        allowedValues = {'createsession', 'interactive', 'generatereport'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['mode'] = value

    @property
    def format(self):
        return self.__options.get('format', None)

    @format.setter
    def format(self, value):
        allowedValues = {'xml', 'json', 'txt', 'html', 'pdf'}
        if value not in allowedValues:
            raise ValueError('"%s" is invalid, valid values are "%s"' %
                             (value, str(allowedValues)))
        self.__options['format'] = value

    @property
    def include(self):
        return self.__options.get('include', None)

    @include.setter
    def include(self, value):
        allowedValues = {'topo', 'services', 'stats', 'faults', 'events'}
        allValues = value.split(',')
        for v in allValues:
            if v not in allowedValues:
                raise ValueError('"%s" is invalid, valid values are "%s"' %
                                 (value, str(allowedValues)))
        self.__options['include'] = value

    @property
    def session(self):
        return self.__options.get('session', None)

    @session.setter
    def session(self, value):
        self.__options['session'] = value

    @property
    def srcep(self):
        return self.__options.get('srcep', None)

    @srcep.setter
    def srcep(self, value):
        self.__options['srcep'] = value

    @property
    def dstep(self):
        return self.__options.get('dstep', None)

    @dstep.setter
    def dstep(self, value):
        self.__options['dstep'] = value


    @property
    def starttime(self):
        return self.__options.get('starttime', None)

    @starttime.setter
    def starttime(self, value):
        self.__options['starttime'] = value


    @property
    def endtime(self):
        return self.__options.get('endtime', None)

    @endtime.setter
    def endtime(self, value):
        self.__options['endtime'] = value


class RestError(Exception):
    """Exceptions that occur due to REST API errors

    Attributes:
      reason (str): The reason string for the exception

      error (int): The REST error code for the exception

      httpCode (int): The HTTP response code
    """
    def __init__(self, errorCode, reasonStr, httpCode):
        """Initialize a RestError instance

        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        self.reason = reasonStr
        self.error = errorCode
        self.httpCode = httpCode

    def __str__(self):
        return self.reason


class CommitError(RestError):
    """Exceptions that occur when trying to commit changes

    Attributes:
      reason (str): The reason string for the exception

      error (int): The REST error code for the exception

      httpCode (int): The HTTP response code
    """
    def __init__(self, errorCode, reasonStr, httpCode=None):
        """Initialize a CommitError instance

        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        super(CommitError, self).__init__(errorCode, reasonStr, httpCode)


class QueryError(RestError):
    """Exceptions that occur during queries

    Attributes:
      reason (str): The reason string for the exception

      error (int): The REST error code for the exception

      httpCode (int): The HTTP response code
    """
    def __init__(self, errorCode, reasonStr, httpCode=None):
        """Initialize a QueryError instance
        
        Args:
          errorCode (int): The REST error code for the exception

          reasonStr (str): The reason for the exception

          httpCode (int): The HTTP response code
        """
        super(QueryError, self).__init__(errorCode, reasonStr, httpCode)
