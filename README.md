Cobra [![Build Status](https://api.shippable.com/projects/54ea96315ab6cc13528d52b3/badge?branchName=master)](https://app.shippable.com/projects/54ea96315ab6cc13528d52b3/builds/latest) [![Documentation Status](https://readthedocs.org/projects/cobra/badge/?version=latest)](https://readthedocs.org/projects/cobra/?badge=latest)
=====

Cobra is the officially supported python bindings for [Cisco APIC REST API][apihome].
It provides a pythonic library that allows developers to quickly develop and test applications to program the Cisco ACI through the APIC.

[apihome]: http://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/1-x/api/rest/b_APIC_RESTful_API_User_Guide.html
[modelhome]: https://developer.cisco.com/site/apic-dc/documents/mim-ref/
[acimodel]: https://github.com/datacenter/acimodel
[issues]: https://github.com/datacenter/cobra/issues

> Life is really simple, but we insist on making it complicated.
>
> *- Confucius*


### Design Goals ###

**Simple.** Pythonic, well documented, easy to develop and test applications.

**Complete.** Covers the entire APIC REST API.

**Robust.** Integrate with [ACI Model][acimodel] for client side validation and testing.

**Light.** Keep the code lean, making it easier to test, optimize and use.


### Features ###

* Programattic interface to ACI model through simple python classes
* Works with multiple versions of ACI model
* Provides unit testing capability against a mock APIC Server
* Python 2.7, Python 3.3/3.4 and PyPy support
* 20% speed boost when Cython is available

### Benefits ###

* Stable production ready code supported by the ACI team
* Full feature coverage with examples
* Tools for unit testing and debugging


### Install ###


```bash
$ pip install --upgrade cython acicobra
```

**Installing on OS X Mavericks with Xcode 5.1**

Xcode Command Line Tools are required to compile Cython. Install them with
this command:

```bash
$ xcode-select --install
```

The Xcode 5.1 CLang compiler treats unrecognized command-line options as
errors; this can cause problems under Python 2.6, for example:

```bash
clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]
```

You can work around errors caused by unused arguments by setting some
environment variables:

```bash
$ export CFLAGS=-Qunused-arguments
$ export CPPFLAGS=-Qunused-arguments
$ pip install cython acicobra
```

### Documentation ###

We have started documenting the library at http://cobra.readthedocs.org and we would of course greatly appreciate pull requests to help imporve the documentation.

The docstrings in the Cobra code base are quite extensive, and we recommend keeping a REPL running while learning the library so that you can query the various modules and classes as you have questions.

Please file issues [here][issues]. Please mail your questions to the cobra support team at acicobra@external.cisco.com.


### Contributing ###

ACI datacenter team officially supports and maintains the cobra API. Pull requests are always welcome.

Before submitting a pull request, please ensure you have added/updated the appropriate tests (and that all existing tests still pass with your changes), and that your coding style follows PEP 8 and doesn't cause pyflakes to complain.

Commit messages should be formatted using [AngularJS conventions][ajs] (one-liners are OK for now but body and footer may be required as the project matures).

Comments follow [Google's style guide][goog-style-comments].

[ajs]: http://goo.gl/QpbS7
[goog-style-comments]: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Comments


### Authors and Contributors ###

Ravi Chamarthy (@rchamarthy) initially developed the cobra API as a common library for ACI developers. It is heavily used for testing, CLI and scripting of APIC. 
Mike Timm (@mtimm) and Paul Lesiak (@paullesiak) are the primary contributors who spent numerous hours writing tests, documentation, examples and developed key features to help cobra shape up!

Mike Shields (@mbshields) owns the documentation efforts.

Sai Ram Goli (@ilog) and Praveen Kumar (@kprav33n) provided valuble design insights during the inception of cobra.


### License ###

Copyright 2015 Cisco Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

