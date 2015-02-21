Session Module
=================
.. module:: session

The session module handles tasks that are associated with opening a session
to configure the APIC.

To make changes to the APIC configuration using the Python API, you must first
log in with the name and password of a configured user with write privileges.
When a login message is accepted, the API returns a data structure that
includes a session timeout period in seconds and a token that represents the
session. The token is also returned as a cookie in the HTTP response header. To
maintain your session, you must send login refresh messages to the API if no
other messages are sent for a period longer than the session timeout period.
The token changes each time that the session is refreshed.

The following sections describe the classes in the session module.

AbstractSession
---------------
Class that abstracts sessions

.. autoclass:: cobra.mit.session.AbstractSession
    :members:
    :special-members:

LoginSession
------------
Class that creates a login session with a username and password.

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

.. autoclass:: cobra.mit.session.CertSession
    :members:
    :special-members:
