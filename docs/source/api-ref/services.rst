Services Module
===============
.. module:: services

This module provides an interface to uploading L4-7 device packages to the
controller. Refer to the **Developing L4-L7 Device Packages** document for more
information on creating device packages.

Example Usage:

.. code-block:: python

    >>> from cobra.mit.session import LoginSession
    >>> from cobra.mit.access import MoDirectory
    >>> from cobra.services import UploadPackage
    >>> 
    >>> session = LoginSession('https://10.10.10.100', 'user', 'password')
    >>> moDir = MoDirectory(session)
    >>> moDir.login()
    >>> 
    >>> packageUpload = UploadPackage('asa-device-pkg.zip')
    >>> response = moDir.commit(packageUpload)
    >>> 

The following sections describe the classes in the services module.

UploadPackage
-------------
Class for uploading L4-L7 device packages to APIC

.. autoclass:: cobra.services.UploadPackage
   :members:
   :special-members:
   :exclude-members: __weakref__
