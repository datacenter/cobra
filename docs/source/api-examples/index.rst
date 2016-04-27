
.. _Examples:


********
Examples
********


Before You Begin
================

Before applying these examples, refer to the APIC documentation to understand
the Cisco Application Centric Infrastructure (ACI) and the APIC. The APIC
documentation contains explanations and examples of these and other tasks
using the APIC GUI, CLI, and REST API. See the *Cisco APIC Getting Started
Guide* for detailed examples.


Initial Statements for All Examples
===================================

The following setup statements or their equivalents are assumed to be present
in any APIC Python API program using these code examples.

.. code-block:: python

    >>> from cobra.mit.session import LoginSession
    >>> from cobra.mit.access import MoDirectory
    >>> 
    >>> session = LoginSession('https://10.10.10.100', 'user', 'password')
    >>> moDir = MoDirectory(session) 
    >>> moDir.login()
    >>> 

The above code snippet creates an **MoDirectory**, connects it to the endpoint
and then performs authentication. The **moDir** can be used to query,
create/delete Mos from the end point.


Creating a Tenant
=================

The tenant (fv:Tenant object) is a container for policies that enable an
administrator to exercise domain based access control so that qualified users
can access privileges such as tenant administration and networking
administration. According to the *Cisco APIC Management Information Model
Reference*, an object of the fv:Tenant class is a child of the policy
resolution universe ('uni') class. This example creates a tenant named
'ExampleCorp' under the 'uni' object.

.. code-block:: python


    >>> # Import the config request class
    ... 
    >>> from cobra.mit.request import ConfigRequest
    >>> configReq = ConfigRequest()
    >>> 
    >>> # Import the tenant class from the model
    ... 
    >>> from cobra.model.fv import Tenant
    >>> 
    >>> # Get the top level policy universe directory
    ... 
    >>> uniMo = moDir.lookupByDn('uni')
    >>> 
    >>> # Create the tenant object
    ... 
    >>> fvTenantMo = Tenant(uniMo, 'ExampleCorp')
    >>> 

The command creates an object of the fv.Tenant class and returns a reference
to the object. A tenant contains primary elements such as filters, contracts,
bridge domains and application network profiles that we will create in later
examples.


Application Profiles
============================

An application profile (fv.Ap object) is a tenant policy that defines the
policies, services, and relationships between endpoint groups (EPGs) within
the tenant. The application profile contains EPGs that are logically related
to one another. This example defines a web application profile under the
tenant.

.. code-block:: python

    >>> # Import the Ap class from the model
    ...
    >>> from cobra.model.fv import Ap
    >>> fvApMo = Ap(fvTenantMo, 'WebApp')
    >>> 

Endpoint Groups
================

An endpoint group is a collection of network-connected devices, such as
clients or servers, that have common policy requirements. This example
creates a web application endpoint group named 'WebEPG' that is contained in
an application profile under the tenant.

.. code-block:: python

    >>> # Import the AEPg class from the model
    ... 
    >>> from cobra.model.fv import AEPg
    >>> fvAEPgMoWeb = AEPg(fvApMo, 'WebEPG')
    >>> 

Physical Domains
================

This example associates the web application endpoint group with a bridge
domain.

.. code-block:: python

    >>> # Import the related classes from the model    
    ... 
    >>> from cobra.model.fv import RsBd, Ctx, BD, RsCtx 
    >>> 
    >>> # Create a private network
    ... 
    >>> fvCtxMo = Ctx(fvTenantMo, 'private-net1')
    >>> 
    >>> # Create a bridge domain
    ... 
    >>> fvBDMo = BD(fvTenantMo, 'bridge-domain1')
    >>> 
    >>> # Create an association of the bridge domain to the private network
    ... 
    >>> fvRsCtx = RsCtx(fvBDMo, tnFvCtxName=fvCtxMo.name)
    >>> 
    >>> # Create a physical domain associated with the end point group
    ... 
    >>> fvRsBd1 = RsBd(fvAEPgMoWeb, fvBDMo.name)
    >>> 

Contracts and Filters
======================

A contract defines the protocols and ports on which a provider endpoint group
and a consumer endpoint group are allowed to communicate. You can use the
**directory.create** function to define a contract, add a subject, and
associate the subject and a filter.

This example creates a Web filter for HTTP (TCP port 80) traffic.

.. code-block:: python

    >>> # Import the Filter and related classes from model
    ... 
    >>> from cobra.model.vz import Filter, Entry, BrCP, Subj, RsSubjFiltAtt
    >>> 
    >>> # Create a filter container (vz.Filter object) within the tenant
    ... 
    >>> filterMo = Filter(fvTenantMo, 'WebFilter')
    >>> 
    >>> # Create a filter entry (vz.Entry object) that specifies bidirectional
    ... # HTTP (tcp/80) traffic
    ... 
    >>> entryMo = Entry(filterMo, 'HttpPort')
    >>> entryMo.dfromPort = 80      # HTTP port
    >>> entryMo.dFromPort = 80      # HTTP port
    >>> entryMo.dToPort = 80
    >>> entryMo.prot = 6            # TCP protocol number
    >>> entryMo.etherT = 'ip'       # EtherType
    >>> 
    >>> # Create a binary contract (vz.BrCP object) container within the
    ... # tenant
    ... 
    >>> vzBrCPMoHTTP = BrCP(fvTenantMo, 'WebContract')
    >>> 
    >>> # Create a subject container for assiciating the filter with the
    ... # contract
    ... 
    >>> vzSubjMo = Subj(vzBrCPMoHTTP, 'WebSubject')  
    >>> RsSubjFiltAtt(vzSubjMo, tnVzFilterName=filterMo.name)
    <cobra.model.vz.RsSubjFiltAtt object at 0x7fad1fce16d0>
    >>> 

Namespaces
==========

A namespace identifies a range of traffic encapsulation identifiers for a VMM
domain or a VM controller. A namespace is a shared resource and can be
consumed by multiple domains such as VMM and L4-L7 services. This example
creates and assigns properties to a VLAN namespace.

.. code-block:: python

    >>> # Import the namespaces related classes from model
    ... 
    >>> from cobra.model.fvns import VlanInstP, EncapBlk
    >>> 
    >>> fvnsVlanInstP = VlanInstP('uni/infra', 'namespace1', 'dynamic')
    >>> fvnsEncapBlk = EncapBlk(fvnsVlanInstP, 'vlan-5', 'vlan-20',
    ...                             name='encap')
    >>> nsCfg = ConfigRequest()
    >>> nsCfg.addMo(fvnsVlanInstP)
    >>> moDir.commit(nsCfg)
    <Response [200]>
    >>> 

VM Networking
=============

This example creates a virtual machine manager (VMM) and configuration.

.. code-block:: python

    >>> # Import the namespaces related classes from model
    ... 
    >>> from cobra.model.vmm import ProvP, DomP, UsrAccP, CtrlrP, RsAcc
    >>> from cobra.model.infra import RsVlanNs
    >>> 
    >>> vmmProvP = ProvP('uni', 'VMware')
    >>> vmmDomP = DomP(vmmProvP, 'Datacenter')
    >>> vmmUsrAccP = UsrAccP(vmmDomP, 'default', pwd='password', usr='user') 
    >>> vmmRsVlanNs = RsVlanNs(vmmDomP, fvnsVlanInstP.dn)  
    >>> vmmCtrlrP = CtrlrP(vmmDomP, 'vserver-01', hostOrIp='192.168.64.9')
    >>> vmmRsAcc = RsAcc(vmmCtrlrP, tDn=vmmUsrAccP.dn)
    >>> 
    >>> # Add the tenant object to the config request and commit
    ... 
    >>> configReq.addMo(fvTenantMo) 
    >>> moDir.commit(configReq)
    <Response [200]>
    >>> 

Creating a Complete Tenant Configuration
========================================

This example creates a tenant named 'ExampleCorp' and deploys a three-tier
application including Web, app, and database servers. See the similar
three-tier application example in the *Cisco APIC Getting Started Guide* for
additional description of the components being configured.

.. literalinclude:: tenants.py
   :linenos:


Creating a Query Filter
=======================

This example creates a query filter property to match fabricPathEpCont objects
whose nodeId property is 101.

.. code-block:: python

    >>> from cobra.mit.request import ClassQuery
    >>> 
    >>> from cobra.model.fabric import PathEpCont 
    >>> 
    >>> nodeId = 101
    >>> myClassQuery = ClassQuery('fabricPathEpCont')
    >>> myClassQuery.propFilter = 'eq(fabricPathEpCont.nodeId,
                                    "{0}")'.format(nodeId)
    >>> 

The basic filter syntax is 'condition(item1, "value")'.  To filter on the
property of a class, the first item of the filter is of the form
pkgClass.property.  The second item of the filter is the property value to
match. The quotes are necessary.


Accessing a Child MO
====================

This example shows how to access a child MO, such as a bridge-domain, which is
a child object of a tenant MO.

.. code-block:: python

    >>> from cobra.mit.request import DnQuery
    >>> 
    >>> dnQuery = DnQuery('uni/tn-common')
    >>> dnQuery.queryTarget = 'children' 
    >>> dnQuery.classFilter = 'fvBD' 
    >>>         
    >>> tenantMo = moDir.query(dnQuery)
    >>> 
    >>> for t in tenantMo:
    ...     print(t.dn)
    ... 
    uni/tn-common/BD-default
    uni/tn-common/BD-common-BD1-test
    uni/tn-common/BD-bd-commonShared
    >>>
