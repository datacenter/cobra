Managed Object (MO) Module
===========================
.. module:: mo

A Managed Object (MO) is an abstract representation of a physical or logical
entity that contain a set of configurations and properties, such as a server,
processor, or resource pool. The MO module represents MOs.

The APIC system configuration and state are modeled as a collection of managed
objects (MOs). For example, servers, chassis, I/O cards, and processors are
physical entities represented as MOs; resource pools, user roles, service
profiles, and policies are logical entities represented as MOs.

Accessing Properties
---------------------
When you create a managed object (MO), you can access properties as follows:

.. code-block:: python

    >>> userMo = User('uni/userext', 'george')
    >>> userMo.firstName = 'George'
    >>> userMo.lastName = 'Washington'

Managing Properties
---------------------
You can use the following methods to manage property changes on a managed object (MO):
    * dirtyProps-Returns modified properties that have not been committed.
    * isPropDirty-Indicates if there are unsaved changes to the MO properties.
    * resetProps-Resets MO properties, discarding uncommitted changes.

Accessing Related Objects
--------------------------
The managed object (MO) object properties enable you to access related objects in the MIT using the following functions:
    * parentDn-Returns the distinguished name (DN) of the parent managed object (MO).
    * parent-Returns the parent MO.
    * children-Returns the names of child MOs.
    * numChildren-Returns the number of child MOs.

Verifying Object Status
-------------------------
You can use the status property to access the status of the Mo.

.. autoclass:: cobra.mit.mo.Mo
   :members:
   :special-members:


