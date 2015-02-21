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
import os
import pytest
import time
import logging
import logging.handlers
import responses
import httplib
import json

from cobra.internal.codec.jsoncodec import fromJSONStr, toJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr
from string import Template
# import cobra.services
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.mit.request
import cobra.mit.session
import cobra.mit.access
import cobra.model.fv
import cobra.model.pol
import cobra.model.infra

httplib.HTTPConnection.debuglevel = 1

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.handlers.RotatingFileHandler(
    '{0}.log'.format(os.path.splitext(__file__)[0]), maxBytes=1000000)

logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s %(message)s')
fh.setFormatter(formatter)


@pytest.fixture
def getResponseMock(tenantname, apic):

    tenantname = tenantname[0]
    url, user, password, secure = apic

    TOKENS = {
        'fakeToken': 'MockedTokenValue'
    }

    HEADERS = {
        'Content-Type': 'application/json',
        'Set-Cookie': TOKENS['fakeToken']
    }

    CONTENT = {
        'aaaLogin': json.dumps(
            {
                'imdata': [
                    {
                        'aaaLogin': {
                            'attributes': {
                                'token': TOKENS['fakeToken']
                            }
                        }
                    }
                ]
            }
        ),
        'tenant': json.dumps(
            {
                'imdata': [
                    {
                        'fvTenant': {
                            'attributes': {
                                'dn': 'uni/tn-{0}'.format(tenantname),
                                'name': tenantname,
                            },
                            'children': [
                                json.loads(
                                    toJSONStr(cobra.model.fv.BD(
                                        'uni/tn-{0}'.format(tenantname), 'b'))),
                                json.loads(
                                    toJSONStr(cobra.model.fv.Ap(
                                        'uni/tn-{0}'.format(tenantname), 'a')))
                            ]
                        }
                    }
                ]
            }
        ),
        'tenants': json.dumps(
            {
                'imdata': [
                    {
                        'fvTenant': {
                            'attributes': {
                                'dn': 'uni/tn-{0}'.format(tenants),
                                'name': tenants,
                            },
                            'children': []
                        }
                    } for tenants in ['common', 'mgmt', 'infra']
                ]
            }
        ),
    }

    # This is a list of tuples, because we need to call responses.add in a
    # specific order
    URLMAP = [
        ('{0}/api/aaaLogin.json'.format(url), {
            'args': [responses.POST],
            'kwargs': {
                'body': CONTENT['aaaLogin'],
                'adding_headers': HEADERS
            }
        }),
        ('{0}/api/mo/uni/tn-{1}.json'.format(url, tenantname), {
            'args': [responses.GET],
            'kwargs': {
                'body': CONTENT['tenant'],
                'adding_headers': HEADERS
            }
        }),
        ('{0}/api/mo/uni/tn-{1}.json'.format(url, tenantname), {
            'args': [responses.POST],
            'kwargs': {
                'body': CONTENT['tenant'],
                'adding_headers': HEADERS
            }
        }),
        ('{0}/api/class/fvTenant.json?query-target-filter=eq(fvTenant.name, "{1}")'.format(url, tenantname), {
            'args': [responses.GET],
            'kwargs': {
                'body': CONTENT['tenant'],
                'adding_headers': HEADERS,
                'match_querystring': True
            }
        }),
        ('{0}/api/class/fvTenant.json'.format(url), {
            'args': [responses.GET],
            'kwargs': {
                'body': CONTENT['tenants'],
                'adding_headers': HEADERS,
                'match_querystring': True
            }
        }),
    ]

    logger.debug('getResponseMock creating responses')
    r = responses.RequestsMock()
    for url, parms in URLMAP:
        logger.debug('adding URL {0}'.format(url))
        args = parms.get('args') + [url]
        r.add(*args, **parms.get('kwargs'))

    return r


@pytest.fixture
def moDir(getResponseMock, apic):
    if apic[0] == 'http://mock':
        getResponseMock.start()
    logger.debug('moDir fixture login')
    url, user, password, secure = apic

    secure = False if secure == 'False' else True
    session = cobra.mit.session.LoginSession(url, user, password,
                                             secure=secure,
                                             requestFormat='json')
    md = cobra.mit.access.MoDirectory(session)
    md.login()
    logger.debug('login token {0}'.format(md._accessImpl._session._cookie))
    if apic[0] == 'http://mock':
        getResponseMock.stop()
    return md


class Test_rest_login:

    def test_login_positive(self, apic, getResponseMock):
        """
        verify that the login function works
        """
        if apic[0] == 'http://mock':
            getResponseMock.start()
        url, user, password, secure = apic

        secure = False if secure == 'False' else True
        session = cobra.mit.session.LoginSession(url, user, password,
                                                 secure=secure,
                                                 requestFormat='json')
        moDir = cobra.mit.access.MoDirectory(session)
        moDir.login()

        logger.debug(
            'login token {0}'.format(moDir._accessImpl._session._cookie))
        assert moDir._accessImpl._session._cookie
        if apic[0] == 'http://mock':
            getResponseMock.stop()


class Test_rest_configrequest:

    def test_createtenant(self, moDir, apic, tenantname, getResponseMock):
        """
        create a tenant and commit it
        """
        tenantname = tenantname[0]
        if apic[0] == 'http://mock':
            getResponseMock.start()

        dcid = str(time.time()).replace('.', '')

        polUni = cobra.model.pol.Uni('')
        tenant = cobra.model.fv.Tenant(polUni, tenantname)
        bd = cobra.model.fv.BD(tenant, 'b')
        ap = cobra.model.fv.Ap(tenant, 'a')

        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(tenant)
        configRequest.subtree = 'full'
        configRequest.id = dcid

        r = moDir.commit(configRequest)
        logger.debug('commit response {0}'.format(r.content))
        assert r.status_code == 200

        mos = fromJSONStr(r.content)
        mo = mos[0]
        logger.debug('r.content: {0}'.format(r.content))
        assert len(mos) > 0
        assert str(mo.dn) == str(tenant.dn)
        assert len(list(mo.children)) >= 2  # expect at least fvBD and fvAp
        assert str(mo.BD['b'].dn) == 'uni/tn-{0}/BD-b'.format(tenantname)
        assert str(mo.ap['a'].dn) == 'uni/tn-{0}/ap-a'.format(tenantname)
        if apic[0] == 'http://mock':
            getResponseMock.stop()


    def test_lookupByDn_createdtenant(self, moDir, apic, tenantname, getResponseMock):

        tenantname = tenantname[0]
        if apic[0] == 'http://mock':
            getResponseMock.start()
        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname))
        assert tenant
        if apic[0] == 'http://mock':
            getResponseMock.stop()

    def test_lookupByClass_filter_createdtenant(self, moDir, apic, tenantname, getResponseMock):
        """
        check that lookupByClass is able to lookup tenant and only one
        item is returned
        """
        tenantname = tenantname[0]
        if apic[0] == 'http://mock':
            getResponseMock.start()
        Tn = moDir.lookupByClass(
            'fvTenant', propFilter='eq(fvTenant.name, "{0}")'.format(tenantname))
        assert len(Tn) == 1
        Tn = Tn[0]
        assert Tn.dn == 'uni/tn-{0}'.format(tenantname)

        if apic[0] == 'http://mock':
            getResponseMock.stop()

    def test_deletetenant(self, moDir, apic, tenantname, getResponseMock):

        tenantname = tenantname[0]
        if apic[0] == 'http://mock':
            getResponseMock.start()
        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname))

        tenant.delete()
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(tenant)

        logger.debug('commit body {0}'.format(toXMLStr(tenant)))

        r = moDir.commit(configRequest)
        assert r.status_code == 200

        if apic[0] == 'http://mock':
            getResponseMock.reset()
            getResponseMock.add(responses.GET,
                                '{0}/api/mo/uni/tn-{1}.json'.format(
                                    apic[0], tenantname
                                ),
                                body=json.dumps({'imdata': []})
                                )

        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname))
        assert not tenant

        if apic[0] == 'http://mock':
            getResponseMock.stop()


class Test_rest_classquery:

    def test_classquery_normal(self, moDir, apic, getResponseMock):
        """
        check that a class query with no special  properties succeeds
        we should get at least three tenants (infra, mgmt, common)
        """
        if apic[0] == 'http://mock':
            getResponseMock.start()
        classQuery = cobra.mit.request.ClassQuery('fvTenant')
        commonTn = moDir.query(classQuery)

        def findtn(tnlist, tnname):
            for tn in tnlist:
                if tn.name == tnname:
                    return True
            return False

        assert findtn(commonTn, 'common')
        assert findtn(commonTn, 'infra')
        assert findtn(commonTn, 'mgmt')
        if apic[0] == 'http://mock':
            getResponseMock.stop()
