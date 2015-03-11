.. _Getting Started with the Cisco APIC Python API:

**********************************************
Getting Started with the Cisco APIC Python API
**********************************************

The following sections describe how to get started when developing with the
APIC Python API.

Preparing for Access
====================

A typical APIC Python API program contains the following initial setup
statements, which are described in the following sections:

.. code-block:: python

   from cobra.mit.access import MoDirectory
   from cobra.mit.session import LoginSession

Path Settings
-------------

If you installed the cobra sdk egg file in the standard python site-packages,
the modules are already included in the python path.

If you installed it in a different directory, add the SDK directory to your
PYTHONPATH environment variable. You can alternatively use the python
**sys.path.append** method to specify or update a path as shown by any of
these examples:

.. code-block:: python

   import sys
   sys.path.append('your_sdk_path')


Connecting and Authenticating
==============================

To access the APIC, you must log in with credentials from a valid user
account. To make configuration changes, the account must have administrator
privileges in the domain in which you will be working. Specify the APIC
management IP address and account credentials in the **LoginSession** object
to authenticate to the APIC as shown in this example:

.. code-block:: python

   apicUrl = 'https://192.168.10.80'
   loginSession = LoginSession(apicUrl, 'admin', 'mypassword')
   moDir = MoDirectory(loginSession)
   moDir.login()
   # Use the connected moDir queries and configuration...
   moDir.logout()

A successful login returns a reference to a directory object that you will use
for further operations. In the implementation of the of the management
information tree (MIT), managed objects (MOs) are represented as directories.

Object Lookup
=============

Use the **MoDirectory.lookupByDn** to look up an object within the MIT object
tree by its distinguished name (DN). This example looks for an object called
'uni':

.. code-block:: python

   uniMo = moDir.lookupByDn('uni')

A successful lookup operation returns a reference to the object that has the
specified DN.

You can also look up an object by class:

.. code-block:: python

   uniMo = moDir.lookupByClass('polUni')

This option returns a list of all objects of the class.

You can also look up an object using the dnquery class or the class query
class. For more information, see the Request module.

Object Creation
================

The following example shows the creation of a tenant object:

.. code-block:: python
    
   from cobra.model.fv import Tenant
   fvTenantMo = Tenant(uniMo, 'Tenant1')

In this example, the command creates an object of the fv.Tenant class and
returns a reference to the object. The tenant object is named 'Tenant1' and
is created under an existing 'uni' object referenced by 'uniMo.'  An object
can be created only under an object of a parent class to the class of the
object being created. See the *Cisco APIC Management Information Model
Reference* to determine the legal parent classes of an object you want to
create.

Querying Objects
================

You can use the **MoDirectory.query** function to query an object within the
APIC configuration, such as an application, tenant, or port. For example:

.. code-block:: python

   from cobra.mit.request import DnQuery
   dnQuery = DnQuery(fvTenantMo.dn)
   dnQuery.queryTarget = 'children'
   childMos = moDir.query(dnQuery)


Committing a Configuration
===========================

Use the **MoDirectory.commit** function to save a new configuration to the mit:

.. code-block::

   from cobra.mit.request import ConfigRequest
   cfgRequest = ConfigRequest()
   cfgRequest.addMo(fvTenantMo)
   moDir.commit(cfgRequest)

