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

import json

import pytest
cobra = pytest.importorskip('cobra')
from cobra.mit.mo import Mo
from cobra.internal.codec.jsoncodec import toJSONStr

cobra.model = pytest.importorskip('cobra.model')
from cobra.model.top import Root


@pytest.mark.mit_mo_str
class Test_mit_mo_str(object):

    def test_Mo_str(self):
        jsonDict = {
            'topRoot': {
                'attributes': {
                    'dn': '',
                    'rn': '',
                    'status': 'created,modified'
                }
            }
        }
        jsonStr = json.dumps(jsonDict, indent=2, sort_keys=True)
        assert jsonStr == str(Root(''))
