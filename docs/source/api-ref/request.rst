Request Module
==============
.. module:: request

The request module handles configuration and queries to the APIC.

You can use the request module to:

* Create or update a managed object (MO)
* Call a method within an MO
* Delete an MO
* Run a query to read the properties and status of an MO or discover objects

Using Queries
-------------

Queries return information about an MO or MO properties within the APIC
management information tree (MIT).  You can apply queries that are based on a
distinguished name (DN) and MO class.

Specifying a Query Scope
------------------------

You can limit the scope of the response to an API query by applying scoping
filters. You can limit the scope to the first level of an object or to one or
more of its subtrees or children based on class, properties, categories,
or qualification by a logical filter expression. This list describes the
available scopes:

* self-(Default) Considers only the MO itself, not children or subtrees.
* children-Considers only the children of the MO, not the MO itself.
* subtree-Considers only the subtrees of the MO, not the MO itself.

Applying Query Filters
----------------------

You can query on a variety of query filters, including:
 
* MO class
* Property
* Subtree
* Subtree and class

You can also include optional subtree values, including:

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

Applying Configuration Requests
-------------------------------

The request module handles configuration requests that are issued by the access
module.  The ConfigRequest class enables you to:

* Add an MO
* Remove an MO
* Verify if an MO is present in an uncommitted configuration
* Return the root MO for a given object

AbstractRequest
---------------

Class that represents an abstract request.  AbstractQuery and ConfigRequest
derive from this class.

.. autoclass:: cobra.mit.request.AbstractRequest
   :members:
   :special-members:
   :exclude-members: __weakref__

AbstractQuery
-------------

Class that represents an abstract query. ClassQuery and DnQuery derive from
this class.

.. autoclass:: cobra.mit.request.AbstractQuery
   :members:
   :special-members:

LoginRequest
------------

Class that represents a login request.

.. autoclass:: cobra.mit.request.LoginRequest
   :members:
   :special-members:

ListDomainsRequest
------------------

Class that represents a request for login/security domains.  This can be done
prior to login.

.. autoclass:: cobra.mit.request.ListDomainsRequest
   :members:
   :special-members:

RefreshRequest
--------------

Class that represents a request to refresh a session.

.. autoclass:: cobra.mit.request.RefreshRequest
   :members:
   :special-members:

FwUploadRequest
---------------

Class that represents a request to upload firmware to an APIC.

.. autoclass:: cobra.mit.request.RefreshRequest
   :members:
   :special-members:

DnQuery
-------

Class that creates a query object based on distinguished name (DN).

.. autoclass:: cobra.mit.request.DnQuery
   :members:
   :special-members:

ClassQuery
----------

Class that creates a query object based on object class.

.. autoclass:: cobra.mit.request.ClassQuery
   :members:
   :special-members:

ConfigRequest
-------------

Class that handles configuration requests. The
:func:`cobra.mit.access.MoDirectory.commit` function uses this class.::

    # Import the config request
    from cobra.mit.request import ConfigRequest
    configReq = ConfigRequest()

.. autoclass:: cobra.mit.request.ConfigRequest
   :members:
   :special-members:

Tag Request
-----------

Tags can be added to select MOs and become objects of type TagInst contained by
that MO.  Rather than having to instantiate an object of type tagInst and query
for the containing MO, instantiate a tagInst object and add it to the
containing MO then commit the whole thing, the REST API offers the ability to
add one or more tags to a specific Dn using a specific API call.  Cobra
utilizes this API call in the TagsRequest class.

Tags can then be used to group or label objects and do quick and easy searches
for objects with a specific tag using a normal ClassQuery with a property
filter.

Tag queries allow you to provide a Dn and either a list of tags or a string
(which should be comma separated in the form: tag1,tag2,tag3) for the add
or remove properties.  The class then builds the proper REST API queries as
needed to add the tag(s) to the MO.

The class can also be used to do tag queries (HTTP GETs) against specific
Dn's using the cobra.mit.access.MoDirectory.query() method with the
cobra.mit.request.TagRequest instance provided as the query object.

Example Usage:

    >>> from cobra.mit.session import LoginSession
    >>> from cobra.mit.access import MoDirectory
    >>> from cobra.mit.request import TagsRequest
    >>> session = LoginSession('https://192.168.10.10', 'george', 'pa$sW0rd!', secure=False)
    >>> modir = MoDirectory(session)
    >>> modir.login()
    >>> tags = TagsRequest('uni/tn-common/ap-default')
    >>> q = modir.query(tags)
    >>> print q[0].name
    pregnantSnake
    >>> tags.remove = "pregnantSnake"
    >>> modir.commit(tags)
    <Response [200]>
    >>> tags.add = ['That','is','1','dead','bird']
    >>> modir.commit(tags)
    <Response [200]>
    >>> tags.add = "" ; tags.remove = []
    >>> q = modir.query(tags)
    >>> tags.remove = ','.join([rem.name for rem in q])
    >>> print tags.remove
    u'is,That,dead,bird,1'
    >>> print tags.getUrl(session)
    https://192.168.10.10/api/tag/mo/uni/tn-common/ap-default.json?remove=bird,1,is,That,dead
    >>> modir.commit(tags)
    <Response [200]>
    >>> modir.query(tags)
    []
    >>>

.. autoclass:: cobra.mit.request.TagsRequest
   :members:
   :special-members:

AliasRequest
------------

A class that represents a request to add/remove aliases.

.. autoclass:: cobra.mit.request.AliasRequest
   :members:
   :special-members:

TraceQuery
----------

A class that creates a trace query

.. autoclass:: cobra.mit.request.TraceQuery
   :members:
   :special-members:


MultiQuery
----------

Class that represents a multi-query request.

.. autoclass:: cobra.mit.request.MultiQuery
   :members:
   :special-members:

TroubleshootingQuery
--------------------

Class that represents a Troubleshooting Query.

.. autoclass:: cobra.mit.request.TroubleshootingQuery
   :members:
   :special-members:

RestError
---------

A class that handles errors from the REST API.  This is a base class for all
query/request exceptions.

.. autoclass:: cobra.mit.request.RestError
   :members:
   :special-members:

CommitError
-----------

A class that handles errors that occur when a change is being committed.

.. autoclass:: cobra.mit.request.CommitError
   :members:
   :special-members:

QueryError
----------

A class that handles errors during queries.

.. autoclass:: cobra.mit.request.QueryError
   :members:
   :special-members:
