# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import sys



def pytest_addoption(parser):
    parser.addoption("--apic", nargs=4, action="append", metavar=('url',
                     'user', 'passwd', 'secure'),
                     help="The URL to the APIC or switch, username, " +
                     "password, secure (True/False)",
                     default=[['http://mock', 'admin', 'password', False]])
    parser.addoption("--tenantname", nargs=1, action="append",
                     metavar=('tenantname'), help="The name of a tenant",
                     type=str, default=[])
    parser.addoption("--dn", nargs=1, action="append", metavar=('Dn'),
                     help="A dn to query, default is uni/tn-common",
                     type=str, default=[])
#    parser.addoption("--fakepackage", nargs=1, action="append",
#                     metavar=('fpack'), help="A fake device package to test" +
#                         " with", type=str, default=[])
#    parser.addoption("--realpackage", nargs=1, action="append",
#                      metavar=('rpack'), help="A real device package to test" +
#                          " with", type=str, default=[])

def pytest_generate_tests(metafunc):

    if 'apic' in metafunc.fixturenames:
        if metafunc.config.getvalue("apic") != []:
            apics = [x for x in metafunc.config.getvalue("apic")]
            metafunc.parametrize("apic", apics)
    if 'tenantname' in metafunc.fixturenames:
        if metafunc.config.getvalue("tenantname") != []:
            tenantnames = metafunc.config.getvalue("tenantname")
            metafunc.parametrize("tenantname", [x for x in tenantnames])
        else:
            metafunc.parametrize("tenantname", ["test"])
    if 'dn' in metafunc.fixturenames:
        if metafunc.config.getvalue("dn") != []:
            dns = metafunc.config.getvalue("dn")
            metafunc.parametrize("dn", [x for x in dns])
        else:
            metafunc.parametrize("dn", ["uni/tn-common"])
#    if 'fakepackage' in metafunc.fixturenames:
#        if metafunc.config.getvalue("fakepackage") != []:
#            fpacks = metafunc.config.getvalue("fakepackage")
#            metafunc.parametrize("fakepackage", [x for x in fpacks])
#        else:
#            metafunc.parametrize("fakepackage", ["Archive.zip"])
#    if 'realpackage' in metafunc.fixturenames:
#        if metafunc.config.getvalue("realpackage") != []:
#            rpacks = metafunc.config.getvalue("realpackage")
#            metafunc.parametrize("realpackage", [x for x in rpacks])
#        else:
#            metafunc.parametrize("realpackage", ["asa-device-pkg.zip"])

# Incremental is useful for functional tests that have to be done in a certain
# order.
#
# Implicit is useful for forcing one test to run or another test to run but
# not both.  The way it is currently designed is to run the initial test but
# if the initial test is skipped run the second test.
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item
    elif "implicit" in item.keywords:
        if not call.excinfo and item.name == 'test_cert_create_pyopenssl':
            parent = item.parent
            parent._previouspassed = item
            return
        elif not call.excinfo:
            # Other test with a different name passed
            return
        elif call.excinfo.errisinstance(pytest.skip.Exception):
            parent = item.parent
            parent._previousskipped = item
            del parent._previouspassed


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" %previousfailed.name)
    elif "implicit" in item.keywords:
        previouspassed = getattr(item.parent, "_previouspassed", None)
        previousskipped = getattr(item.parent, "_previousskipped", None)
        if previousskipped is not None:
            return
        elif previouspassed is not None:
            pytest.skip("Previous test passed, skipping")

