Session Module
=================
.. module:: session

The session module handles tasks that are associated with opening a session
to an APIC or Fabric Node.

The session module contains two classes to open sessions with the APIC or Fabric
Nodes:

1. LoginSession - uses a username and password to login
2. CertSession - uses a private key to generate signatures for every
   transaction, the user needs to have a X.509 certificate associated with
   their local user.

The LoginSession is the most robust method allowing access to both the APIC's
and the Fabric Nodes (switches) and can support all methods of RBAC.  The
CertSession method of generating signatures is limited to only communicating
with the APIC and can not support any form of RBAC.  One other limitation of
CertSession type of sesions is there is no support for eventchannel
notifications.

To make changes to the APIC configuration using the Python API, you must use a
user with write privileges.  When using a LoginSession, once a user is
authenticated, the API returns a data structure that includes a session timeout
period in seconds and a token that represents the session. The token is also
returned as a cookie in the HTTP response header. To maintain your session, you
must send login refresh messages to the API within the session timeout period.
The token changes each time that the session is refreshed.

The following sections describe the classes in the session module.

AbstractSession
---------------

Class that abstracts sessions.  This is used by LoginSession and CertSession
and should not be instantiated directly.  Instead use one of the other
session classes.

.. autoclass:: cobra.mit.session.AbstractSession
   :members:
   :special-members:
   :exclude-members: __weakref__

LoginError
----------

Class that handles errors during the login process.

.. autoclass:: cobra.mit.session.LoginError
   :members:
   :special-members:

LoginSession
------------

Class that creates a login session with a username and password.

Example of using a LoginSession:

.. code-block:: python

   from cobra.mit.access import MoDirectory
   from cobra.mit.access import LoginSession

   session = LoginSession('https://10.10.10.100', 'user', 'password')
   moDir = MoDirectory(session)
   allTenants = moDir.lookupByClass('fvTenant')
   print(allTenants)

.. autoclass:: cobra.mit.session.LoginSession
   :members:
   :special-members:

CertSession
-----------
Class that creates a unique token per URI path based on a signature created
by a SSL.  Locally this uses a private key to create that signature.  On the
APIC you have to already have provided a certificate with the users public key
via the aaaUserCert class.  This uses PyOpenSSL if it is available (install
Cobra with the [ssl] option).  If PyOpenSSL is not available this will try to
fallback to openssl using subprocess and temporary files that should work for
most platforms.

Steps to utilize CertSession
++++++++++++++++++++++++++++

1. Create a local user on the APIC with a X.509 certificate in PEM format
2. Instantiate a CertSession class with the users certificate Dn and the private
   key
3. Make POST/GET requests using the Python SDK

Step 1: Create a local user with X.509 Certificate
""""""""""""""""""""""""""""""""""""""""""""""""""

The following is an example of how to use the Python SDK to configure a local
user with a X.509 certificate.  This is a required step and can be completed
using the GUI, the REST API or the Python SDK.  Once the local user exists and
has a X.509 certificate attached to the local user, then the CertSession class
can be used for that user.

.. code-block:: python

    >>> # Generation of a certificate and private key using the subprocess module to
    ... # make direct calls to openssl at the shell level.  This assumes that
    ... # openssl is installed on the system.
    ...
    >>>
    >>> from subprocess import Popen, CalledProcessError, PIPE
    >>> 
    >>> from cobra.mit.session import LoginSession
    >>> from cobra.mit.access import MoDirectory
    >>> from cobra.mit.request import ConfigRequest
    >>> 
    >>> from cobra.model.pol import Uni as PolUni
    >>> from cobra.model.aaa import UserEp as AaaUserEp
    >>> from cobra.model.aaa import User as AaaUser
    >>> from cobra.model.aaa import UserDomain as AaaUserDomain
    >>> from cobra.model.aaa import UserRole as AaaUserRole
    >>> from cobra.model.aaa import UserCert as AaaUserCert
    >>> 
    >>> certUser = 'myuser'
    >>> pKeyFile = 'myuser.key'
    >>> certFile = 'myuser.cert'
    >>>
    >>> # Generate the certificate in the current directory
    ...
    >>> cmd = ['openssl', 'req', '-new', '-newkey', 'rsa:1024', '-days', '36500',
    ...        '-nodes', '-x509', '-keyout', pKeyFile, '-out', certFile, 
    ...        '-subj', '/CN=APIC/O=Cisco/C=US']      
    >>> proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    >>> out, error = proc.communicate()
    >>>
    >>> # If an error occurs, fail
    ...
    >>> if proc.returncode != 0:
    ...     print('Output: {0}, Error {1}'.format(out, error))
    ...     raise CalledProcessError(proc.returncode, ' '.join(cmd))
    ...
    >>>
    >>> # At this point pKeyFile and certFile exist as files in the local directory.
    ... # pKeyFile will be used when we want to generate signatures.  certFile is
    ... # contains the X.509 certificate (with public key) that needs to be pushed
    ... # to the APIC for a local user.
    ...
    >>>
    >>> with open(certFile, 'r') as file:
    ...     PEMdata = file.read()
    ... 
    >>>
    >>> # Generate a local user to commit to the APIC
    ...
    >>> polUni = PolUni('')
    >>> aaaUserEp = AaaUserEp(polUni)
    >>> aaaUser = AaaUser(aaaUserEp, certUser)
    >>> aaaUserDomain = AaaUserDomain(aaaUser, name='all')
    >>>
    >>> # Other aaaUserRoles maybe needed to give the user other privileges
    ...
    >>> aaaUserRole = AaaUserRole(aaaUserDomain, name='read-all',
    ...                           privType='readPriv')
    >>>
    >>> # Attach the certificate to that user
    ...
    >>> aaaUserCert = AaaUserCert(aaaUser, certUser + '-cert')
    >>>
    >>> # Using the data read in from the certificate file
    ...
    >>> aaaUserCert.data = PEMdata
    >>>
    >>> # Push the new local user to the APIC
    ...
    >>> session = LoginSession('https://10.10.10.100', 'user', 'password')
    >>> moDir = MoDirectory(session)
    >>> moDir.login()
    >>>   
    >>> cr = ConfigRequest()
    >>> cr.addMo(aaaUser)
    >>> moDir.commit(cr)
    <Response [200]>
    >>>

Steps 2 and 3: Instantiate and use a CertSession class
""""""""""""""""""""""""""""""""""""""""""""""""""""""

This step requires you know two pieces of information:

1. The users certificate distinguished name (Dn)
2. The private key that was created at the time of the certificate

The private key should be kept secret to ensure the highest levels of security
for this type of session.

The certificate Dn will be in the form of:

    uni/userext/user-<userid>/usercert-<certName>

You can also use a aaaUserCert managed object to get this Dn - as in the example
below.  The following example shows how to query the APIC for all tentants using
a CertSession:

.. code-block:: python

    >>> from cobra.mit.session import CertSession
    >>> from cobra.mit.access import MoDirectory
    >>> 
    >>> from cobra.model.pol import Uni as PolUni
    >>> from cobra.model.aaa import UserEp as AaaUserEp
    >>> from cobra.model.aaa import User as AaaUser
    >>> from cobra.model.aaa import UserCert as AaaUserCert
    >>> 
    >>> certUser = 'myuser'
    >>> pKeyFile = 'myuser.key'
    >>> 
    >>> # Generate a local user object that mactches the one on the APIC
    ... # This is only being used to get the Dn of the user's certificate
    ... 
    >>> polUni = PolUni('')
    >>> aaaUserEp = AaaUserEp(polUni)
    >>> aaaUser = AaaUser(aaaUserEp, certUser)
    >>> 
    >>> # Attach the certificate to that user
    ... 
    >>> aaaUserCert = AaaUserCert(aaaUser, certUser + '-cert')
    >>> 
    >>> # Read in the private key data from a file in the local directory 
    ... 
    >>> with open(pKeyFile, 'r') as file:
    ...     pKey = file.read()
    ... 
    >>> 
    >>> # Instantiate a CertSession using the Dn and private key
    ... 
    >>> session = CertSession('https://10.10.10.100', aaaUserCert.dn, pKey)
    >>> moDir = MoDirectory(session)
    >>> 
    >>> # No login is required for certificate based sessions
    ... 
    >>> allTenants = moDir.lookupByClass('fvTenant')
    >>> for tenant in allTenants:
    ...     print(tenant.name)
    ... 
    Red
    Blue
    Zach
    Purple
    Mike
    Green
    Sand
    >>> 

.. autoclass:: cobra.mit.session.CertSession
   :members:
   :special-members:
