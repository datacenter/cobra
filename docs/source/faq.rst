.. _FAQ:


**************************
Frequently Asked Questions
**************************

The following sections provide troubleshooting tips for common problems when
using the APIC Python API.

Authentication Error
====================

Ensure that you have the correct login credentials and that you have created a
MoDirectory MO.

Inactive Configuration
======================

If you have modified the APIC configuration and the new configuration is not
active, ensure that you have committed the new configuration using the
**MoDirectory.commit** function.

Keyword Error
=============

To use a reserved keyword, from the API, include the _ suffix. In the following
example, from is translated to from\_::

    def __init__(self, parentMoOrDn, from_, to, **creationProps):
        namingVals = [from_, to]
        Mo.__init__(self, parentMoOrDn, *namingVals, **creationProps)

Name Error
==========

If you see a NameError for a module, such as cobra or access, ensure that you
have included an import statement in your code such as::

	import cobra
	from cobra.mit import access

Python Path Errors
==================

Ensure that your PYTHONPATH variable is set to the correct location. For more
information, refer to http://www.python.org.
You can use the **sys.path.append** python function or set PYTHONPATH
environment variable to append a directory to your Python path.

Python Version Error
====================

The APIC Python API supports Python version 2.7.5 and later 2.7 versions;
other versions of Python are not currently supported.

WindowsError
============

If you see a **WindowsError: [Error 2] The system cannot find the file
specified,** when trying to use the CertSession class, it generally means that
you do not have openssl installed on Windows.  Please see :doc:`Installing the
Cisco APIC Python SDK <install>`

ImportError for cobra.mit.meta.ClassMeta
========================================

If you see an **ImportError: No module named mit.meta** when trying to import
something from the cobra.model namepsace, ensure that you have the acicobra
package installed. Please see :doc:`Installing the Cisco APIC Python SDK
<install>`

ImportError for cobra.model.\*
==============================

If you see an **ImportError: No module named model.** when importing anything
from the cobra.model namespace, ensure that you have the acimodel package
installed.  Please see :doc:`Installing the Cisco APIC Python SDK <install>`
