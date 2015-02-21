.. _Tools for API Development:

*************************
Tools for API Development
*************************

To create API commands and perform API functions, you must determine which MOs and properties are related to your task, and you must compose data structures that specify settings and actions on those MOs and properties. Several resources are available for that purpose. 

APIC Management Information Model Reference
===========================================

The *Cisco APIC Management Information Model Reference* is a Web-based tool that lists all object classes and their properties. The reference also provides the hierarchical structure, showing the ancestors and descendants of each object, and provides the form of the distinguished name (DN) for an MO of a class.

API Inspector
=============

The API Inspector is a built-in tool of the APIC graphical user interface (GUI) that allows you to capture internal REST API messaging as you perform tasks in the APIC GUI. The captured messages show the MOs being accessed and the JSON data exchanges of the REST API calls. You can use this data when designing Python API calls to perform similar functions.

You can find instructions for using the API Inspector in the *Cisco APIC REST API User Guide*.

Browsing the Management Information Tree With the CLI
=====================================================

The APIC command-line interface (CLI) represents the management information tree (MIT) in a hierarchy of directories, with each directory representing a managed object (MO).  You can browse the directory structure by doing the following:

1. Open an SSH session to the APIC to reach the CLI
2. Go to the directory /mit

For more information on the APIC CLI, see the *Cisco APIC Command Reference*.

Managed Object Browser (Visore)
===============================

The Managed Object Browser, or Visore, is a utility built into the APIC that provides a graphical view of the managed objects (MOs) using a browser. The Visore utility uses the APIC REST API query methods to browse MOs active in the Application Centric Infrastructure Fabric, allowing you to see the query that was used to obtain the information. The Visore utility cannot be used to perform configuration operations.

You can find instructions for using the Managed Object Browser in the *Cisco APIC REST API User Guide*.

APIC Getting Started Guide
==========================

The *Cisco APIC Getting Started Guide* contains many detailed examples of APIC configuration tasks using the APIC GUI, CLI, and REST API.

