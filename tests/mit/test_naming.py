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
 
from builtins import object

import pytest
cobra = pytest.importorskip('cobra')
from cobra.mit.naming import Dn, Rn

cobra.model = pytest.importorskip('cobra.model')
from cobra.model.top import Root


@pytest.mark.mit_naming_Dn
class Test_mit_naming_Dn(object):
    def test_Dn_appendRn(self):
        topRootDn = Dn()
        topRootRn = Rn(Root.meta)
        topRootDn.appendRn(topRootRn)


@pytest.mark.mit_naming_Rn
class Test_mit_naming_Rn(object):
    pass
