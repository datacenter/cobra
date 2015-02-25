Naming Module
=================
.. module:: naming

The APIC system configuration and state are modeled as a collection of managed
objects (MOs), which are abstract representations of a physical or logical
entity that contain a set of configurations and properties. For example,
servers, chassis, I/O cards, and processors are physical entities that are
represented as MOs; resource pools, user roles, service profiles, and policies
are logical entities represented as MOs.

At runtime, all MOs are organized in a tree structure, which is called the
Management Information Tree (MIT). This tree provides structured and consistent
access to all MOs in the system. Each MO is identified by its relative name
(RN) and distinguished name (DN).  You can manage MO naming by using the naming
module of the Python API.

You can use the naming module to create and parse object names, as well as
access a variety of information about the object, including the relative name,
parent or ancestor name, naming values, meta class, or MO class.  You can also
perform operations on an MO such as appending an Rn to a Dn or cloning an MO.

Relative Name (RN)
------------------

A relative name (RN) identifies an object from its siblings within the context
of the parent MO. An Rn is a list of prefixes and properties that uniquely
identify the object from its siblings.

For example, the Rn for an MO of type aaaUser is user-john.  user- is the
naming prefix and john is the *name* value.

You can use an RN class to convert between an MO's RN and constituent naming
values.

The string form of an RN is {prefix}{val1}{prefix2}{Val2} (...)

.. note::
   The naming value is enclosed in brackets ([]) if the meta object specifies
   that properties be delimited.


.. autoclass:: cobra.mit.naming.Rn
   :members:
   :special-members:
   :exclude-members: __weakref__,__cmp__,__hash__,__str__

Distinguished Name (DN)
-----------------------

A distinguished name (DN) uniquely identifies a managed object (MO). A DN is an
ordered list of relative names, such as the following:

	dn = rn1/rn2/rn3/....

In the next example, the DN provides a fully qualified path for user-john from
the top of the MIT to the MO.

	dn = "uni/userext/user-john"

	This DN consists of these relative names:

=================  =============   =======================
  Relative Name        Class             Description
=================  =============   =======================
  uni               polUni            Policy universe
  userext           aaaUserEp         User endpoint
  user-john         aaaUser           Local user account
=================  =============   =======================

.. note::
   When using the API to filter by distinguished name (DN), we recommend that
   you use the full DN rather than a partial DN.


.. autoclass:: cobra.mit.naming.Dn
   :members:
   :special-members:
   :exclude-members: __weakref__,__cmp__,__hash__,__str__,__len__
