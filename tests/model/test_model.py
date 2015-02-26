from future import standard_library
standard_library.install_aliases()
from builtins import object
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

#!/usr/bin/env python
import pytest
import logging
import inspect
import pkgutil
import http.client

cobra.model = pytest.importorskip("cobra.model")
import cobra.mit.access
import cobra.mit.session

pytestmark = pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                                reason="You must specify at least one --apic " +
                                       "option on the CLI")
slow = pytest.mark.slow

http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(params=pytest.config.getvalue('apic'))
def moDir(request):
    url, user, password, secure = request.param
    secure = False if secure == 'False' else True
    session = cobra.mit.session.LoginSession(url, user, password,
                                             secure=secure)
    md = cobra.mit.access.MoDirectory(session)
    md.login()
    return md


def classlist():
    modlist = []
    cobrapackages = ['cobra.model.' + modname for importer, modname,
                     ispkg in pkgutil.iter_modules(cobra.model.__path__) if not ispkg]
    for package in cobrapackages:
        __import__(package)
        for key, value in inspect.getmembers(eval(package), inspect.isclass):
            obj = eval(package + '.' + key)
            if hasattr(obj, 'meta'):
                cls = value.__module__.split('.')[-1] + key
                modlist.append(cls)
    return modlist


def pytest_generate_tests(metafunc):
    if 'cobraclass' in metafunc.fixturenames:
        metafunc.parametrize('cobraclass', classlist())


class Test_cobra_model(object):

    @slow
    def test_class_loader(self, moDir, cobraclass):
        moDir.lookupByClass(cobraclass)
