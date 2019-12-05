.. _Installing the Cisco APIC Python SDK:

************************************
Installing the Cisco APIC Python SDK
************************************

Installation Requirements:
--------------------------

The Cisco APIC Python SDK ("cobra") comes in two installable .whl files that
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

In this document, the **acicobra** package is also referred to as **the SDK**.

Both packages are required. You can download the two .whl files from a
running instance of APIC at this URL:

* http[s]://<APIC address>/cobra/_downloads/

The /cobra/_downloads directory contains the two .whl files along with the .egg files. The egg files are only for backward compatibility and users should migrate to .whl files. The actual
filenames may contain extra information such as the APIC and Python versions, as shown in this example:

    .. code-block:: shell

       Index of cobra/_downloads

           Parent Directory
           acicobra-4.2_2j-py2.py3-none-any.whl
           acimodel-4.2_2j-py2.py3-none-any.whl

In this example, each .whl filename references the APIC version 4.2(2j) from
which it was created and the Python version py2 and py3 with which it is compatible. The whl files are platform independent.

Download both files from APIC to a convenient directory on your host computer.
We recommend placing the files in a directory with no other files.

Before installing the SDK, ensure that you have the following packages
installed:

* Python 2.7 or Python3.6 - For more information, see https://www.python.org/.
* pip - For more information, see https://pypi.python.org/pypi/pip.
* virtualenv - We recommend installing the Python SDK within a virtual
  environment using virtualenv.  A virtual environment allows isolation of
  the Cobra Python environment from the system Python environment or from
  multiple Cobra versions.For more information, see
  https://pypi.python.org/pypi/virtualenv.

**Note:** SSL support for connecting to the APIC and fabric nodes using HTTPS
is present by default in the normal installation. If you intend to use the
CertSession class with pyopenssl, see *Installing pyopenssl*.

**Note:** The model package depends on the SDK package; be sure to install
the SDK package first.


Installing the SDK on Unix and Linux:
-------------------------------------

Follow these steps to install the SDK on Unix and Linux:

1. Uninstall previous SDK versions:

    .. code-block:: shell

       pip uninstall acicobra

    If no previous versions are installed, skip this step.

2. (Optional)Create and activate a new virtual environment in which to run the SDK.
    Refer to the documentation for virtualenv or similar virtual environment tools for your operating system.
    If you create a virtual environment for the SDK, perform the remaining steps in the virtual environment.

3. Copy the .whl files to your development system.

4. Install the whl file using the following command:

   From a local directory (relative or absolute):

    .. code-block:: shell

        pip install *directory/path*/acicobra

    In the following example, the .whl file is in a directory named
    cobra-whls that is a sub-directory of the current directory:

    .. code-block:: shell

        $ pip install ./cobra-whls/acicobra-4.2_2j-py2.py3-none-any.whl

    **Note:** To install the package directly into the user-site-packages
    directory, use the **pip install --user** option:

    .. code-block:: shell

        pip install --user *directory/path*/acicobra

    **Note:** If you intend to use the CertSession class with pyopenssl, see *Installing pyopenssl*.

Installing the SDK on Windows:
------------------------------

Follow these steps to install the SDK on Windows:

1. Uninstall previous SDK versions (can be skipped if previous versions have
   not been installed):

    .. code-block:: shell

       pip uninstall acicobra

    If no previous versions are installed, skip this step.

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

        .. code-block:: shell

           set OPENSSL_CONF=C:\OpenSSL-Win32\bin\openssl.cfg

    - For 64-bit Windows

        .. code-block:: shell

           set OPENSSL_CONF=C:\OpenSSL-Win64\bin\openssl.cfg

3. Install the latest Python 2.7 version from https://www.python.org/downloads/.

4. Add the following to your Windows path:

    .. code-block:: shell

       ;C:\Python27;C:\Python27\Scripts

5. Download and run https://bootstrap.pypa.io/get-pip.py to install pip and
   setuptools.

6. Run the following commands to install virtual environment tools:

    .. code-block:: shell

       pip install virtualenv
       pip install virtualenv-clone
       pip install virtualenvwrapper-win

7. Create and activate a new virtual environment.

    .. code-block:: shell

       mkvirtualenv acienv

   **Note:** Virtual environments using virtualenvwrapper-win are created in
   `%USERPROFILE%\Envs` by default.

8. Upgrade pip in the virtual environment.

    .. code-block:: shell

	   c:\users\username\Envs\acienv
	   python -m pip install --upgrade pip

9. Install the APIC Python SDK (Cobra) using the following command.

    From a local directory (relative or absolute):

    .. code-block:: shell

        pip install \*directory\path*\acicobra

    In the following example, the .whl file is in a directory named
    cobra-whls that is a sub-directory of the current directory:

    .. code-block:: shell

        > pip install cobra-whls\acicobra-4.2_2j-py2.py3-none-any.whl

    **Note:** To install the package directly into the user-site-packages
    directory, use the **pip install --user** option.

    **Note:** If you intend to use the CertSession class with pyopenssl, see *Installing pyopenssl*.

Installing the model package on any platform
--------------------------------------------

The model package  depends on the SDK package. Install the SDK package
prior to installing the model package.  If you uninstall the SDK package
and then try to import the model package, the APIC displays an **ImportError**
for the module **mit.meta**.

Installation of the model package can be accomplished via pip:

    .. code-block:: shell

       pip install *directory/path*/acimodel-*version*-py2.7.whl

In the following example, the .whl file is in a directory named
cobra-whls that is a sub-directory of the current directory:

    .. code-block:: shell

       pip install ./cobra-whls/acimodel-4.2_2j-py2.py3-none-any.whl

**Note:** The .whl file name might be different depending on whether the
file is downloaded from the APIC or from Cisco.com.

**Note:** If you uninstall the SDK package and then try to import the
model package, the APIC displays an ImportError for the module mit.meta.

********************************************************
Viewing the status of the SDK and model packages install
********************************************************

To view which version of the SDK and which dependancies have been installed use
pip as follows:

    .. code-block:: shell

       pip freeze

Once you know the name of a package you can also use the following to show the
packages dependancies:

    .. code-block:: shell

       pip show <packagename>

For example:

    .. code-block:: shell

       $ pip show acimodel
       ---
       Name: acimodel
       Version: 4.2_2j
       Location: /local/lib/python2.7/site-packages/acimodel-4.2_2j-py2.py3-none-any.whl
       Requires: acicobra

When you install the SDK without SSL support it will depend on the following
modules:

1. requests
2. future

When you install the SDK with SSL support it will depend on the following
modules:

1. requests
2. future
3. pyOpenSSL

These dependancies may have their own dependancies and may require a compiler
depending on your platform and method of installation.


**************************************
Uninstalling the Cisco APIC Python SDK
**************************************

To uninstall the Python SDK and/or model, use pip as follows:

    .. code-block:: shell

       pip uninstall acicobra
       pip uninstall acimodel

**Note:** If you used sudo to install the Python SDK and/or model, use **sudo
pip uninstall acicobra** to uninstall the SDK and **sudo pip uninstall
acimodel** to unistall the model package.

**Note:** Uninstalling one of the packages and not the other may leave your
environment in a state where it will throw import errors when trying to import
various parts of the cobra namespace.  The packages should be installed
together and uninstalled together.

********************
Installing pyopenssl
********************

SSL support for connecting to the APIC and fabric nodes using HTTPS is present
by default in the normal installation. Installing pyopenssl is necessary only
if you intend to use the CertSession class with pyopenssl. Note that CertSession
works with native OS calls to openssl.

Installations with SSL can require a compiler.

Installing pyopenssl
---------------------

In *Installing the SDK on Unix and Linux*, substitute the following procedure for the step where the SDK .whl file is installed.
If you have created a virtual environment for the SDK, enter the command in the virtual environment.

1. Upgrade pip.

    .. code-block:: shell

        python -m pip install --upgrade pip


2. Install pyopenssl with wheel.

    .. code-block:: shell

          pip install --use-wheel pyopenssl

    **Note:** This package installs pyopenssl, cryptography, cffi, pycparser and six.

3. Install the SDK .whl file using the following command:

    From a local directory (relative or absolute) you must use the --find-links option and the [ssl] option:

    .. code-block:: shell

        pip install \*directory\path*\acicobra

    In the following example, the .whl file is in a directory named cobra-whls that is a sub-directory of the current directory:

    .. code-block:: shell

        > pip install ./cobra-whls/acicobra-4.2_2j-py2.py3-none-any.whl

