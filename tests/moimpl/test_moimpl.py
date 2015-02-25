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
from cobra.internal.base.moimpl import MoStatus, BaseMo

@pytest.mark.internal_base_moimpl_MoStatus
class Test_internal_base_moimpl_MoStatus:
    # Test the expected MoStatus flags
    @pytest.mark.parametrize("status,value", [
        (MoStatus.CLEAR, 1),
        (MoStatus.CREATED, 2),
        (MoStatus.MODIFIED, 4),
        (MoStatus.DELETED, 8),
    ])
    def test_MoStat_flags(self, status, value):
        assert status == value

    # Test MoStatus.fromString() method, seems to be broken though
    @pytest.mark.xfail(reason='MoStatus.fromString is broken and not used, ' +
                              'should it be removed?')
    @pytest.mark.parametrize("statusStr,obj,created,modified,deleted", [
        ("",                 MoStatus, False, False, False),
        ("created",          MoStatus, True,  False, False),
        ("modified",         MoStatus, False, True,  False),
        ("deleted",          MoStatus, False, False, True),
        ("created,modified", MoStatus, True,  True,  False),
        ("created,deleted",  MoStatus, True,  False, True),
        ("modified,deleted", MoStatus, False, True,  True),
    ])
    def test_MoStatus_fromString(self, statusStr, obj, created, modified,
                                deleted):
        mostat = MoStatus.fromString(statusStr)
        assert isinstance(mostat, obj)
        assert mostat.created == created
        assert mostat.modified == modified
        assert mostat.deleted == deleted

    # Test MoStatus onBit
    @pytest.mark.parametrize("init,onBits,onBitsExpected", [
        (0, MoStatus.CREATED, "created"),
        (0, MoStatus.MODIFIED, "modified"),
        (0, MoStatus.DELETED, "deleted"),
        (0, MoStatus.CREATED | MoStatus.MODIFIED, "created,modified"),
        (0, MoStatus.CREATED | MoStatus.DELETED, "deleted"),
    ])
    def test_MoStatus_onBit(self, init, onBits, onBitsExpected):
        status = MoStatus(init)
        status.onBit(onBits)
        assert str(status) == onBitsExpected

    @pytest.mark.parametrize("init,offBits,offBitsExpected", [
        (MoStatus.CREATED, MoStatus.CREATED, ""),
        (MoStatus.CREATED | MoStatus.MODIFIED, MoStatus.CREATED, "modified"),
        (MoStatus.CREATED | MoStatus.MODIFIED | MoStatus.DELETED,
             MoStatus.DELETED, "created,modified"),
        (MoStatus.CREATED | MoStatus.MODIFIED | MoStatus.DELETED,
             MoStatus.MODIFIED, "deleted"),
        (MoStatus.CREATED | MoStatus.MODIFIED | MoStatus.DELETED,
             MoStatus.CREATED, "deleted"),
    ])
    def test_MoStatus_offBit(self, init, offBits, offBitsExpected):
        status = MoStatus(init)
        status.offBit(offBits)
        assert str(status) == offBitsExpected

    @pytest.mark.parametrize("init,prop,expected", [
        (MoStatus.CREATED, "created", True),
        (MoStatus.CREATED, "modified", False),
        (MoStatus.CREATED, "deleted", False),
        (MoStatus.MODIFIED, "created", False),
        (MoStatus.MODIFIED, "modified", True),
        (MoStatus.MODIFIED, "deleted", False),
        (MoStatus.DELETED, "created", False),
        (MoStatus.DELETED, "modified", False),
        (MoStatus.DELETED, "deleted", True),
        (MoStatus.CREATED | MoStatus.MODIFIED, "created", True),
        (MoStatus.CREATED | MoStatus.MODIFIED, "modified", True),
        (MoStatus.CREATED | MoStatus.MODIFIED, "deleted", False),
        (MoStatus.CREATED | MoStatus.DELETED, "created", True),
        (MoStatus.CREATED | MoStatus.DELETED, "modified", False),
        (MoStatus.CREATED | MoStatus.DELETED, "deleted", True),
        (MoStatus.MODIFIED | MoStatus.DELETED, "created", False),
        (MoStatus.MODIFIED | MoStatus.DELETED, "modified", True),
        (MoStatus.MODIFIED | MoStatus.DELETED, "deleted", True),
    ])
    def test_MoStatus_props(self, init, prop, expected):
        status = MoStatus(init)
        assert eval("status." + prop) == expected

    def test_MoStatus_clear(self):
        status = MoStatus(MoStatus.CREATED | MoStatus.MODIFIED)
        status.clear()
        assert status.created == False
        assert status.deleted == False
        assert status.modified == False

    @pytest.mark.xfail(reason="__cmp__ is not implemented properly on " +
                              "MoStatus, skip it")
    def test_MoStatus_cmp(self):
        status1 = MoStatus(MoStatus.CREATED)
        status2 = MoStatus(MoStatus.CREATED)
        assert status1 == status2

@pytest.mark.internal_base_moimpl_MoBase
class Test_internal_base_moimpl_MoBase:

    # Must be called with some other class, otherwise it raises a
    # NotImplementedError
    def test_baseMo_init_raises(self):
        with pytest.raises(NotImplementedError):
            BaseMo('uni', True)
