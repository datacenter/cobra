********************************************************************
Understanding the Cisco Application Policy Infrastructure Controller
********************************************************************

Understanding the Cisco Application Policy Infrastructure Controller
====================================================================
The Cisco Application Policy Infrastructure Controller (APIC) is a key
component of an Application Centric Infrastructure (ACI), which delivers a
distributed, scalable, multi-tenant infrastructure with external end-point
connectivity controlled and grouped via application centric policies. The APIC
is the key architectural component that is the unified point of automation,
management, monitoring and programmability for the Application Centric
Infrastructure. The APIC supports the deployment, management and monitoring of
any application anywhere, with a unified operations model for physical and
virtual components of the infrastructure.

The APIC programmatically automates network provisioning and control based on
the application requirements and policies. It is the central control engine for
the broader cloud network, simplifying management while allowing tremendous
flexibility in how application networks are defined and automated.

ACI Policy Theory
------------------
The ACI policy model is an object-oriented model based on promise theory.
Promise theory is based on scalable control of intelligent objects rather than
more traditional imperative models, which can be thought of as a top-down
management system. In this system, the central manager must be aware of both
the configuration commands of underlying objects and the current state of those
objects.
Promise theory, in contrast, relies on the underlying objects to handle
configuration state changes initiated by the control system itself as "desired
state changes." The objects are then responsible for passing exceptions or
faults back to the control system. This approach reduces the burden and
complexity of the control system and allows greater scale. This system scales
further by allowing the methods of underlying objects to request state changes
from one another and from lower-level objects.

Within this theoretical model, ACI builds an object model for the deployment of
applications, with the applications as the central focus. Traditionally,
applications have been restricted by the capabilities of the network and by
requirements to prevent misuse of the constructs to implement policy. Concepts
such as addressing, VLAN, and security have been tied together, limiting the
scale and mobility of the application. As applications are being redesigned for
mobility and web scale, this traditional approach hinders rapid and consistent
deployment.
The ACI policy model does not dictate anything about the structure of the
underlying network. However, as dictated by promise theory, it requires some
edge element, called an iLeaf, to manage connections to various devices.

Object Model
------------------
At the top level, the ACI object model is built on a group of one or more
tenants, allowing the network infrastructure administration and data flows to
be segregated. Tenants can be used for customers, business units, or groups,
depending on organizational needs. For instance, an enterprise may use one
tenant for the entire organization, and a cloud provider may have customers
that use one or more tenants to represent their organizations.
Tenants can be further divided into contexts, which directly relate to Virtual
Routing and Forwarding (VRF) instances, or separate IP spaces. Each tenant can
have one or more contexts, depending on the business needs of that tenant.
Contexts provide a way to further separate the organizational and forwarding
requirements for a given tenant. Because contexts use separate forwarding
instances, IP addressing can be duplicated in separate contexts for
multitenancy.

Within the context, the model provides a series of objects that define the
application. These objects are endpoints (EP) and endpoint groups (EPGs) and
the policies that define their relationship. Note that policies in this case
are more than just a set of access control lists (ACLs) and include a
collection of inbound and outbound filters, traffic quality settings, marking
rules, and redirection rules. The combination of EPGs and the policies that
define their interaction is an Application Network Profile in the ACI model.

Understanding the Management Information Tree
---------------------------------------------
The Management Information Tree (MIT) consists of hierarchically organized MOs
that allow you to manage the APIC. Each node in this tree is an MO and each has
a unique distinguished name (DN) that identifies the MO and its place in the
tree. Each MO is modeled as a Linux directory that contains all properties in
an MO file and all child MOs as subdirectories.

Understanding Managed Objects
-----------------------------
The APIC system configuration and state are modeled as a collection of managed
objects (MOs), which are abstract representations of a physical or logical
entity that contain a set of configurations and properties. For example,
servers, chassis, I/O cards, and processors are physical entities represented
as MOs; resource pools, user roles, service profiles, and policies are logical
entities represented as MOs. Configuration of the system involves creating MOs,
associating them with other MOs, and modifying their properties.

At runtime all MOs are organized in a tree structure called the Management
Information Tree, providing structured and consistent access to all MOs in the
system.

Endpoint Groups
------------------
EPGs are a collection of similar endpoints representing an application tier or
set of services. They provide a logical grouping of objects that require
similar policy. For example, an EPG could be the group of components that make
up an application's web tier. Endpoints are defined using the network interface
card (NIC), virtual NIC (vNIC), IP address, or Domain Name System (DNS) name,
with extensibility to support future methods of identifying application
components.

EPGs are also used to represent entities such as outside networks, network
services, security devices, and network storage. EPGs are collections of one or
more endpoints that provide a similar function. They are a logical grouping
with a variety of use options, depending on the application deployment model in
use.

Endpoint Group Relationships
----------------------------
EPGs are designed for flexibility, allowing their use to be tailored to one or
more deployment models that the customer can choose. The EPGs are then used to
define the elements to which policy is applied. Within the network fabric,
policy is applied between EPGs, therefore defining the way that EPGs
communicate with one another. This approach is designed to be extensible in the
future to policy application within the EPGs.

Here are some examples of EPG use:

* EPG defined by traditional network VLANs: All endpoints connected to a given
  VLAN placed in an EPG
* EPG defined by Virtual Extensible LAN (VXLAN): Same as for VLANs except using
  VXLAN
* EPG mapped to a VMware port group
* EPG defined by IP or subnet: for example, 172.168.10.10 or 172.168.10
* EPG defined by DNS names or DNS ranges: for instance, example.foo.com or
  \*.web.foo.com

The use of EPGs is both flexible and extensible. The model is intended to
provide tools to build an application network model that maps to the actual
environment's deployment model. The definition of endpoints also is extensible,
providing support for future product enhancements and industry requirements.
The EPG model offers a number of management advantages. It offers a single
object with uniform policy to higher-level automation and orchestration tools.
Tools need not operate on individual endpoints to modify policies.
Additionally, it helps ensure consistency across endpoints in the same group
regardless of their placement in the network.

Policy Enforcement
------------------
The relationship between EPGs and policies can be thought of as a matrix with
one axis representing the source EPG (sEPG) and the other representing the
destination EPG (dEPG.) One or more policies will be placed at the intersection
of the appropriate sEPGs and dEPGs. The matrix will be sparsely populated in
most cases because many EPGs have no need to communicate with one another.

Policies are divided by filters for quality of service (QoS), access control,
service insertion, etc. Filters are specific rules for the policy between two
EPGs. Filters consist of inbound and outbound rules: permit, deny, redirect,
log, copy, and mark. Policies allow wildcard functions in the definitions.
Policy enforcement typically uses a most-specific-match-first approach.

Application Network Profiles
----------------------------
An Application Network Profile is a collection of EPGs, their connections, and
the policies that define those connections. Application Network Profiles are
the logical representation of an application and its interdependencies in the
network fabric.
Application Network Profiles are designed to be modeled in a logical way that
matches the way that applications are designed and deployed. The configuration
and enforcement of policies and connectivity is handled by the system rather
than manually by an administrator.

These general steps are required to create an Application Network Profile:

#. Create EPGs (as discussed earlier).
#. Create policies that define connectivity with these rules:

   * Permit
   * Deny
   * Log
   * Mark
   * Redirect
   * Copy

#. Create connection points between EPGs using policy constructs known as
   contracts.

Contracts
------------------
Contracts define inbound and outbound permit, deny, and QoS rules and policies
such as redirect. Contracts allow both simple and complex definition of the way
that an EPG communicates with other EPGs, depending on the requirements of the
environment. Although contracts are enforced between EPGs, they are connected
to EPGs using provider-consumer relationships. Essentially, one EPG provides a
contract, and other EPGs consume that contract.

The provider-consumer model is useful for a number of purposes. It offers a
natural way to attach a "shield" or "membrane" to an application tier that
dictates the way that the tier interacts with other parts of an application.
For example, a web server may offer HTTP and HTTPS, so the web server can be
wrapped in a contract that allows only these services. Additionally, the
contract provider-consumer model promotes security by allowing simple,
consistent policy updates to a single policy object rather than to multiple
links that a contract may represent. Contracts also offer simplicity by
allowing policies to be defined once and reused many times.

Application Network Profile
----------------------------
The three tiers of a web application defined by EPG connectivity and the
contracts constitute an Application Network Profile. Contracts also provide
reusability and policy consistency for services that typically communicate with
multiple EPGs.

Configuration Options
----------------------
The Cisco Application Policy Infrastructure Controller (APIC) supports multiple
configuration methods, including a GUI, a REST API, a Python API,
Bash scripting, and a command-line interface.

Understanding Python
---------------------
Python is a powerful programming language that allows you to quickly build
applications to help support your network. For more information, see
'http:www.python.org <http://www.python.org>'

Understanding the Python API
-----------------------------
The Python API provides a Python programming interface to the underlying REST
API, allowing you to develop your own applications to control the APIC and the
network fabric, enabling greater flexibility in infrastructure automation,
management, monitoring and programmability.

The Python API supports Python versions 2.7 and 3.4.

Understanding the REST API
--------------------------
The APIC REST API is a programmatic interface to the APIC that uses a
Representational State Transfer (REST) architecture. The API accepts and
returns HTTP or HTTPS messages that contain JavaScript Object Notation (JSON)
or Extensible Markup Language (XML) documents. You can use any programming
language to generate the messages and the JSON or XML documents that contain
the API methods or managed object (MO) descriptions.

For more information about the APIC REST API, see the *APIC REST API User Guide*.
