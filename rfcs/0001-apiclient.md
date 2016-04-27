- Title: APIC API Client
- Author: Ravi Chamarthy
- E-mail: rchamarthy
- Status: Open

# Overview

Over the past few years, certain patterns and anit-patterns have emerged in
building usable API clients for APIC REST API. This document attempts to capture
the patterns to apply and avoid few pitfalls while building client bindings for
the APIC.

APIC REST API is defined in a model that is language agnostic. This model
provides constructs that define a Managed Object (Mo), and its properties.
Properties are of specific types with a set of constraints attached to them. Mos
can contain other Mos or refer to other Mos thus forming a tree structure we can
Management Information Tree (MIT). Model defines the structure of the MIT via
containment and naming rules. This information is referred to as the meta that
defines the object model for the APIC API.

# Motivation

* Document the patterns known to have worked well for APIC client bindings
* Document known issues and pitfalls

This document aims to serve as a starting point for language binding developers
that develop client bindings for the APIC in various programming languages.

# Patterns

## Decouple Meta from Runtime

MIT Meta provides information about the Mos that are being exchanged between the
APIC and the client program. This meta can be used to perform various client
side validations and map XML/Json into native language types.

This meta is guaranteed to be backward compatible but Mos, types and properties
can be added in newer versions in a backward compatible way. The application
must continue to run with newer versions of meta without any changes unless they
want to use this new information presented.

The pattern to use is for the client to maintain a list of meta files per
version on the client side. On each login compare the APIC version with locally
available meta and use it for the session. This will allow the client
application to work against multiple APIC versions. If the meta is not available
locally then explicitly download the meta from the target APIC. This can be done
during the login mechanism of the runtime or provide an appropriate error and
have the application download the meta explicitly.

For statically typed languages this may involve generation of code and libraries.
The language binding must provide the tools required to do this with complete
documentation of the recommended work flow.

## MIT Structure

The language binding must provide an abstract MIT construct that mimics the
capabilities of the APIC MIT. This structure is used to construct a client side
MIT and manipulate. This allows for client applications to structure themselves
as applications that manipulate MIT and propagate the changes to the APIC in a
transaction.

MIT operations:

* Create an Mo
* Delete an Mo
* Update an Mo
* Iterate over child Mos
* Iterate over child Mos of a particular type
* Query the local MIT structure for Mos
* Query filters like Class and property filters
* Clone operations for subtrees

## Hide DN and RN Format

Dn and Rn are key concepts to uniquely address Mos in a MIT. Exposing the string
form of the Dn/Rn to the application results in tight coupling with the Dn/Rn
string format and can lead to code that manipulates these strings to be
sprinkled around the application. Hide the strings and expose and interface to
intuitively construct Dn/Rn by using Classes, Containment rules and naming
properties.

## Separate Query Options from Response Options

REST API provides a rich set of query options and response options. Query
options control the selection of the target list of Mos where are the response
options control the information that needs to be included with the selected Mos.
In the core REST API these options can be mixed arbitrarily impacting the
usability of the API.

The runtime should separate query options explicitly from the response options
to avoid confusion on the behavior of the options and simplify the queries.

