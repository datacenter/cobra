Access Module
=================
.. module:: access

The access module enables you to maintain network endpoints and manage APIC
connections.

The following sections describe the classes in the access module.
	

MoDirectory
------------------

Class that creates a connection to the APIC and manage the MIT configuration.
MoDirectory enables you to create queries based on the object class,
distinguished name, or other properties, and to commit a new configuration.
MoDirectory requires an existing session and endpoint.

.. autoclass:: cobra.mit.access.MoDirectory
   :members:
   :special-members:

