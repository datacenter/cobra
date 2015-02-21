Managed Object (MO) Module
===========================
.. module:: mo

A Managed Object (MO) is an abstract representation of a physical or logical entity that contain a set of configurations and properties, such as a server, processor, or resource pool. The MO module represents MOs.

The APIC system configuration and state are modeled as a collection of managed objects (MOs). For example, servers, chassis, I/O cards, and processors are physical entities represented as MOs; resource pools, user roles, service profiles, and policies are logical entities represented as MOs.

The following sections describe the classes in the MO module.

.. autoclass:: cobra.mit.mo.Mo
   :members:
   :special-members:


Adding a Tenant
------------------
A tenant is a policy owner in the virtual fabric. A tenant can be either a private or a shared entity. For example,
you can create a securely partitioned private tenant or a tenant with contexts and bridge domains that are shared by
other tenants. Common names for shared tenants are common, default, or infra.

In the management information model, a tenant is represented by a managed object (MO) of class fv:Tenant.
According to the *Cisco APIC Management Information Model Reference*, an object of the fv:Tenant class is
a child of the policy resolution universe (uni) class and has a distinguished name (DN) format of uni/tn-[name].

To create a new tenant, specify the class and naming information, either in the message body or in the URI.
To create a new tenant named ExampleCorp using the Python API, use the Tenant() method as follows::

    # Import the config request
    from cobra.mit.request import ConfigRequest
    configReq = ConfigRequest()

    # Import the tenant class from the model
    from cobra.model.fv import Tenant

    # Get the top level policy universe directory
    uniMo = moDir.lookupByDn('uni')

    # create the tenant object
    fvTenantMo = Tenant(uniMo, 'ExampleCorp')

Adding a User
------------------
An APIC user account contains, in addition to a name and password, information about the user's privilege level (role) and the scope (domain) of the user's control in the fabric. A cloud administrator, for example, might
have global control, including the ability to create tenants and to assign additional administrators, while a
tenant administrator is typically restricted to the tenant's domain or network. When you configure a user
account, you can specify additional configuration items, such as a password expiration policy, or you can
omit those items to accept the default settings.
In the management information model, an APIC user is represented by a managed object (MO) of class
aaa:User. According to the *Cisco APIC Management Information Model Reference*, an object of the aaa:User
class has a distinguished name (DN) format of uni/userext/user-[name]. The direct properties (attributes)
of the aaa:User class do not include fields for the user domain or privilege level, but the reference for this
class indicates a child class (subtree) of aaa:UserDomain, which has a child class of aaa:UserRole.

The API command structure that you would use to add the new user can include the configuration of the user domain and privilege level
in these child classes in the following hierarchy:

* aaa:User - The user object can contain one or more user domain child objects.
* aaa:UserDomain - The user domain object can contain one or more user role objects.

Accessing Properties
---------------------
When you create a managed object (MO), you can access properties as follows::

    userMo = User('uni/userext', 'george')
    userMo.firstName = 'George'
    userMo.lastName = 'Washington'

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

