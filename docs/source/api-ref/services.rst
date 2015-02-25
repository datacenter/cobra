Services Module
===============
.. module:: services

This module provides an interface to uploading L4-7 device packages to the
controller. Refer to the **Developing L4-L7 Device Packages** document for more
information on creating device packages.

Example::

    session = cobra.mit.session.LoginSession('https://apic', 'admin',
                                             'password', secure=False)
    moDir = cobra.mit.access.MoDirectory(session)
    moDir.login()

    packageUpload = cobra.services.UploadPackage('asa-device-pkg.zip')
    response = moDir.commit(packageUpload)

The following sections describe the classes in the services module.

UploadPackage
-------------
Class for uploading L4-L7 device packages to APIC

.. autoclass:: cobra.services.UploadPackage
   :members:
   :special-members:
   :exclude-members: __weakref__
