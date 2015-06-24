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
import random
import string
import time

cobra = pytest.importorskip('cobra')
import cobra.eventchannel
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session

cobra.model = pytest.importorskip('cobra.model')
import cobra.model.fv
import cobra.model.infra
import cobra.model.pol


def pytest_generate_tests(metafunc):

    def createtenant(moDir, tenant=None):
        topMo = cobra.model.pol.Uni('')
        fvTenant = cobra.model.fv.Tenant(topMo, name=tenant, descr=''.join(
            random.choice(string.lowercase) for i in range(16)))
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(fvTenant)
        moDir.commit(configRequest)

    def deletetenant(moDir, tenant=None):
        topMo = cobra.model.pol.Uni('')
        fvTenant = cobra.model.fv.Tenant(topMo, name=tenant)
        fvTenant.delete()
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(fvTenant)
        moDir.commit(configRequest)

    def createepg(moDir, tenant=None):
        topMo = cobra.model.pol.Uni('')
        fvTenant = cobra.model.fv.Tenant(topMo, name=tenant, descr=''.join(
            random.choice(string.lowercase) for i in range(16)))
        fvAp = cobra.model.fv.Ap(fvTenant, name='test')
        fvAEPg = cobra.model.fv.AEPg(fvAp, name='test', descr=''.join(
            random.choice(string.lowercase) for i in range(16)))
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(fvTenant)
        moDir.commit(configRequest)

    def deleteepg(moDir, tenant=None):
        topMo = cobra.model.pol.Uni('')
        fvTenant = cobra.model.fv.Tenant(topMo, name=tenant)
        fvTenant.delete()
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(fvTenant)
        moDir.commit(configRequest)

    if 'queries' in metafunc.fixturenames:
        metafunc.parametrize(
            'queries',
            [
                (
                    # query to subscribe to
                    cobra.mit.request.ClassQuery('fvTenant'),
                    # bring up method
                    createtenant,
                    # tear down method
                    deletetenant,
                    'uni/tn-eventchannel1',                     # dn
                    {'tenant': 'eventchannel1'}                 # kwargs
                ),
                (
                    cobra.mit.request.ClassQuery('fvAEPg'),
                    createepg,
                    deleteepg,
                    'uni/tn-eventchannel1/ap-test/epg-test',
                    {'tenant': 'eventchannel1'}
                ),
            ]
        )


@pytest.fixture(params=['xml', 'json'])
def sessiontuple(apic, request):
    if apic[0] == 'http://mock':
        pytest.skip('No mock support for event channel yet')

    url, user, password, secure = apic
    secure = False if secure == 'False' else True
    loginSession = cobra.mit.session.LoginSession(url, user, password,
                                                  secure=secure,
                                                  requestFormat=request.param)
    moDir = cobra.mit.access.MoDirectory(loginSession)
    moDir.login()
    return moDir, loginSession


@pytest.mark.eventchannel
class Test_eventchannel:

    def test_subscribe(self, sessiontuple, apic, queries):

        if apic[0] == 'http://mock':
            pytest.skip('No mock support for event channel yet')

        moDir, ls = sessiontuple
        query, bringup, teardown, dn, kwargs = queries
        ec = cobra.eventchannel.EventChannel(ls)
        subscription = ec.subscribe(query)
        assert subscription.subid != 0

    def test_refresh(self, sessiontuple, apic, queries):

        if apic[0] == 'http://mock':
            pytest.skip('No mock support for event channel yet')

        moDir, ls = sessiontuple
        query, bringup, teardown, dn, kwargs = queries
        ec = cobra.eventchannel.EventChannel(ls)
        subscription = ec.subscribe(query)
        assert subscription.subid != 0

        subscription.refresh()

    def test_receive_event(self, sessiontuple, apic, queries):

        if apic[0] == 'http://mock':
            pytest.skip('No mock support for event channel yet')

        moDir, ls = sessiontuple
        query, bringup, teardown, dn, kwargs = queries

        ec = cobra.eventchannel.EventChannel(ls)
        subscription = ec.subscribe(query)
        assert subscription.subid != 0

        subscription.refresh()

        time.sleep(3)

        bringup(moDir, **kwargs)

        found = False

        events = ec.retrieveEvents()

        for moevent in events:

            if moevent.dn == dn:
                found = True

        assert found

    def test_cleanup(self, sessiontuple, apic, queries):

        if apic[0] == 'http://mock':
            pytest.skip('No mock support for event channel yet')

        moDir, ls = sessiontuple
        query, bringup, teardown, dn, kwargs = queries
        teardown(moDir, **kwargs)
