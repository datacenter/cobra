.. _Installing the Cisco APIC Python SDK:

************************************
Installing the Cisco APIC Python SDK
************************************

Installation Requirements:
--------------------------

The Cisco APIC Python SDK ("cobra") comes in two installable .egg files that
are part of the **cobra** namespace, they operate as one **virtual**
namespace.  Those installable packages are:

1. **acicobra** - This is the SDK and includes the following namespaces:

   - **cobra**
   - **cobra.mit**
   - **cobra.internal**

2. **acimodel** - This includes the Python packages that model the Cisco ACI
   Management Information Tree and includes the following namespaces:

   - **cobra**
   - **cobra.model**

Both packages are required. In this document, the **acicobra** package is
simply referred to as **the SDK**.

You can download the two .egg files from a running instance of APIC at these URLs:

* http[s]://<APIC address>/cobra/_downloads/acicobrasdk.egg
* http[s]://<APIC address>/cobra/_downloads/acicobramodel.egg

Before installing the SDK, ensure that you have the following packages
installed:

* Python 2.7 - For more information, see https://www.python.org/.
* easy_install - For more information about easy_install, see
  https://pypi.python.org/pypi/setuptools.
* pip - For more information, see https://pypi.python.org/pypi/pip.
* virtualenv - We recommend installing the Python SDK within a virtual
  environment using virtualenv.  For more information, see
  https://pypi.python.org/pypi/virtualenv.


**Note:** Installation of the SDK with SSL support on Unix/Linux and MacOSX
requires a compiler.  Windows users can install the compiled shared objects
for the SDK dependancies using wheel packages.

**Note:** The model package depends on the SDK package; be sure to install
the SDK package first.


Installing the SDK on Unix and Linux:
-------------------------------------

Follow these steps to install the SDK on Unix and Linux:

1. Uninstall previous SDK versions:

    .. code-block:: none

       pip uninstall acicobra

2. Copy the .egg file to your development system.
3. Install the egg file - any installation with SSL support may require a
   compiler - using **one** of the following commands:

   a) Without ssl support from a local directory (relative or absolute):

       .. code-block:: none

          easy_install -Z --find-links *directory/path* acicobra

   b) With ssl support from a local directory (relative or absolute):

       .. code-block:: none

          easy_install -Z --find-links *directory/path* acicobra[ssl]

   **Note:** To install the package directly into the user-site-packages
   directory, use the **easy_install --user -Z ...** command.

Installing the SDK on Windows:
------------------------------

Follow these steps to install the SDK on Windows:

1. Uninstall previous SDK versions (can be skipped if previous versions have
   not been installed):

    .. code-block:: none

       pip uninstall acicobra

2. (Optional - if you want SSL support) Install OpenSSL for Windows:

   a) Install the latest Visual C++ Redistributables package from
      http://slproweb.com/products/Win32OpenSSL.html.

   b) Install the latest Win32 or Win64 Open SSL Light version from
      http://slproweb.com/products/Win32OpenSSL.html

   c) Add either C:\OpenSSL-Win32\bin or C:\OpenSSL-Win64\bin to your Windows
      path file.

   d) Open a command window and enter one of the following commands to add an
      OpenSSL path depending on which platform you have:

    - For 32-bit Windows:

        .. code-block:: none

           set OPENSSL_CONF=C:\OpenSSL-Win32\bin\openssl.cfg

    - For 64-bit Windows

        .. code-block:: none

           set OPENSSL_CONF=C:\OpenSSL-Win64\bin\openssl.cfg

3. Install the latest Python 2.7 version from https://www.python.org/downloads/.

4. Add the following to your Windows path:

    .. code-block:: none

       ;C:\Python27;C:\Python27\Scripts

5. Download and run https://bootstrap.pypa.io/get-pip.py to install pip and
   setuptools.

6. Run the following commands to install virtual environment tools:

    .. code-block:: none

       pip install virtualenv
       pip install virtualenv-clone
       pip install virtualenvwrapper-win

7. Create and activate a new virtual environment.

    .. code-block:: none

       mkvirtualenv egg123

   **Note:** Virtual environments using virtualenvwrapper-win are created in
   `%USERPROFILE%\Envs` by default.

8. Upgrade pip in the virtual environment.

    .. code-block:: none

	   c:\users\username\Envs\egg123
	   python -m pip install --upgrade pip

9. Install pyopenssl with wheel.

    .. code-block:: none

	   pip install --use-wheel pyopenssl

    **Note:** This package installs pyopenssl, cryptography, cffi, pycparser and
    six.

10. Install the APIC Python SDK (Cobra) using **one** of the following commands.

    a) Without ssl support from a local directory (relative or absolute):

        .. code-block:: none

           easy_install -Z --find-links *directory\path* acicobra

    b) With ssl support from a local directory (relative or absolute):

        .. code-block:: none

           easy_install -Z --find-links *directory\path* acicobra[ssl]

   **Note:** To install the package directly into the user-site-packages
   directory, use the **easy_install --user -Z ...** command.

Installing the model package on any platform
--------------------------------------------

The model package  depends on the SDK package. Install the SDK package
prior to installing the model package.  If you uninstall the SDK package 
and then try to import the model package, the APIC displays an **ImportError** 
for the module **mit.meta**.

Installation of the model package can be accomplished via easy_install:

    .. code-block:: none

       easy_install -Z *directory/path*/acimodel-*version*-py2.7.egg

**Note:** The egg file name will be different depending on whether the 
file is downloaded from the APIC or from Cisco.com.


********************************************************
Viewing the status of the SDK and model packages install
********************************************************

To view which version of the SDK and which dependancies have been installed use
pip as follows:

    .. code-block:: none

       pip freeze

Once you know the name of a package you can also use the following to show the
packages dependancies:

    .. code-block:: none

       pip show <packagename>

For example:

    .. code-block:: none

       $ pip show acimodel
       ---
       Name: acimodel
       Version: 1.0.1-219
       Location: /local/lib/python2.7/site-packages/acimodel-1.0.1_219-py2.7.egg
       Requires: acicobra

When you install the SDK without SSL support it will depend only on the
requests module.

When you install the SDK with SSL support it will depend on the following
modules:

1. requests
2. pyOpenSSL

These dependancies may have their own dependancies and may require a compiler
depending on your platform and method of installation.


**************************************
Uninstalling the Cisco APIC Python SDK
**************************************

To uninstall the Python SDK and/or model, use pip as follows:

    .. code-block:: none

       pip uninstall acicobra
       pip uninstall acimodel

**Note:** If you used sudo to install the Python SDK and/or model, use **sudo
pip uninstall acicobra** to uninstall the SDK and **sudo pip uninstall
acimodel** to unistall the model package.

**Note:** Uninstalling one of the packages and not the other may leave your
environment in a state where it will throw import errors when trying to import
various parts of the cobra namespace.  The packages should be installed
together and uninstalled together.
