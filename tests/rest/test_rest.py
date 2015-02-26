from __future__ import print_function
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
import httplib
import os
import pytest
import random
import string
import time
import xml.etree.ElementTree as ET
import logging
import requests

from cobra.internal.codec.jsoncodec import toJSONStr, fromJSONStr
from cobra.internal.codec.xmlcodec import toXMLStr, fromXMLStr

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
cobra.model.fv = pytest.importorskip("cobra.model.fv")
import cobra.model.pol
import cobra.model.infra
import cobra.services

pytestmark = pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                                reason="You must specify at least one --apic " +
                                       "option on the CLI")
slow = pytest.mark.slow

httplib.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)

fakeDevicePackageZip = 'Archive.zip'
realDevicePackageZip = 'asa-device-pkg.zip'


@pytest.fixture(params=pytest.config.getvalue('apic'))
def moDir(request):
    url, user, password, secure = request.param
    secure = False if secure == 'False' else True
    session = cobra.mit.session.LoginSession(url, user, password,
                                             secure=secure)
    md = cobra.mit.access.MoDirectory(session)
    md.login()
    return md


class Test_rest_configrequest:

    def test_createtenant(self, moDir, tenantname):
        """
        create a tenant and commit it
        """
        dcid = str(time.time()).replace('.', '')

        polUni = cobra.model.pol.Uni('')
        tenant = cobra.model.fv.Tenant(polUni, tenantname[0])

        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(tenant)
        configRequest.subtree = 'full'
        configRequest.id = dcid

        r = moDir.commit(configRequest)
        assert r.status_code == requests.codes.ok

        if moDir._accessImpl._session.formatType == cobra.mit.session.AbstractSession.XML_FORMAT:
            mos = fromXMLStr(r.content)
        else:
            mos = fromJSONStr(r.content)

        mo = mos[0]
        assert len(mos) > 0
        assert mo.dn == tenant.dn
        assert len(list(mo.children)) >= 1

    def test_lookupcreatedtenant(self, moDir, tenantname):

        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname[0]))
        assert tenant

    def test_deletetenant(self, moDir, tenantname):
        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname[0]))

        tenant.delete()
        configRequest = cobra.mit.request.ConfigRequest()
        configRequest.addMo(tenant)

        r = moDir.commit(configRequest)
        assert r.status_code == 200

        tenant = moDir.lookupByDn('uni/tn-{0}'.format(tenantname[0]))
        assert not tenant


class Test_rest_classquery:

    def test_classquery_shorthand_filter(self, moDir):
        """
        check that lookupByClass is able to lookup tenant common and only one
        item is returned
        """
        commonTn = moDir.lookupByClass(
            'fvTenant', propFilter='eq(fvTenant.name, "common")')
        assert len(commonTn) == 1
        commonTn = commonTn[0]
        assert commonTn.dn == 'uni/tn-common'

    def test_classquery_normal(self, moDir):
        """
        check that a class query with no special  properties succeeds
        we should get at least three tenants (infra, mgmt, common)
        """
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

    def test_classquery_filter(self, moDir):
        """
        check that a class query with a property filter works
        """
        classQuery = cobra.mit.request.ClassQuery('fvTenant')
        classQuery.propFilter = 'eq(fvTenant.name, "common")'
        commonTn = moDir.query(classQuery)
        commonTn = commonTn[0]
        assert commonTn.dn == 'uni/tn-common'

    def test_classquery_subtree(self, moDir):
        """
        check that a class query with a subtree response
        """
        classQuery = cobra.mit.request.ClassQuery('fvTenant')
        classQuery.subtree = 'full'
        classQuery.propFilter = 'eq(fvTenant.name, "common")'
        commonTn = moDir.query(classQuery)
        commonTn = commonTn[0]
        assert commonTn.dn == 'uni/tn-common'
        # expect at least 3 child objects
        assert len(list(commonTn.children)) >= 3
        assert commonTn.BD['default'].dn == 'uni/tn-common/BD-default'

    @pytest.mark.parametrize("cls,subtree", [
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('fvTenant', 'full')),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('infraInfra', 'no')),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('fvAEPg', 'full')),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('infraFuncP', 'full')),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('fabricNode', 'no')),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")(('topSystem', 'full')),
    ])
    def test_classquery_many(self, moDir, cls, subtree):
        classQuery = cobra.mit.request.ClassQuery(cls)
        classQuery.subtree = subtree
        # classQuery.propFilter='eq(fvTenant.name, "common")'
        mos = moDir.query(classQuery)
        assert len(mos) > 0

    def test_classquery_verifyxml(self, moDir):
        """
        verify that the XML returned by lookupByClass is valid
        """
        commonTn = moDir.lookupByClass(
            'fvTenant', propFilter='eq(fvTenant.name, "common")')
        commonTn = commonTn[0]
        xml = ET.fromstring(toXMLStr(commonTn))
        assert xml.tag == 'fvTenant'

    def test_classquery_negative(self, moDir):
        """
        generate a random tenant name and ensure that we dont find a match for it
        """
        tenantName = ''.join(random.choice(string.lowercase)
                             for i in range(64))
        tenant = moDir.lookupByClass(
            'fvTenant', propFilter='eq(fvTenant.name, "{0}")'.format(tenantName))
        assert len(tenant) == 0


class Test_rest_dnquery:

    def test_dnquery_normal(self, moDir, dn):

        dnQuery = cobra.mit.request.DnQuery(dn)
        dnQuery.subtree = 'full'

        commonTn = moDir.query(dnQuery)
        assert len(commonTn) == 1
        commonTn = commonTn[0]
        assert commonTn.dn == dn
        # expect at least 3 child objects
        assert len(list(commonTn.children)) >= 3
        assert commonTn.BD['default'].dn == 'uni/tn-common/BD-default'

    def test_dnquery_shorthand(self, moDir, dn):
        commonTn = moDir.lookupByDn(dn)
        assert commonTn.dn == dn


class Test_rest_login:

    def test_login_positive(self, apic):
        """
        verify that the login function works
        """
        url, user, password, secure = apic
        secure = False if secure == 'False' else True
        session = cobra.mit.session.LoginSession(url, user, password,
                                                 secure=secure)
        moDir = cobra.mit.access.MoDirectory(session)
        moDir.login()
        assert moDir._accessImpl._session

    def test_login_negative(self, apic):
        """
        verify that the invalid logins throw an exception
        """
        url, user, password, secure = apic
        secure = False if secure == 'False' else True
        session = cobra.mit.session.LoginSession(url, user, 'wrongpassword',
                                                 secure=secure)
        moDir = cobra.mit.access.MoDirectory(session)
        with pytest.raises(cobra.mit.session.LoginError):
            moDir.login()

    @slow
    def test_login_timeout(self, apic):
        """
        verify that the session times out properly
        """
        url, user, password, secure = apic
        secure = False if secure == 'False' else True
        session = cobra.mit.session.LoginSession(url, user, password,
                                                 secure=secure)
        moDir = cobra.mit.access.MoDirectory(session)
        moDir.login()
        start = time.time()

        pki = moDir.lookupByDn('uni/userext/pkiext/webtokendata')
        refreshTime = pki.webtokenTimeoutSeconds
        sleepTime = float(refreshTime) - (time.time() - start)
        sleepTime += 1.0  # one second buffer, for good measure

        time.sleep(sleepTime)

        with pytest.raises(cobra.mit.request.QueryError):
            moDir.lookupByClass('pkiWebTokenData')

    def test_login_get_timeout(self, apic):
        """
        verify that the session times out properly
        """
        url, user, password, secure = apic
        secure = False if secure == 'False' else True
        session = cobra.mit.session.LoginSession(url, user, password,
                                                 secure=secure)
        moDir = cobra.mit.access.MoDirectory(session)
        moDir.login()

        assert moDir._accessImpl._session.refreshTime > int(time.time())
        assert moDir._accessImpl._session.refreshTimeoutSeconds > 0


class Test_rest_tracequery:

    @pytest.mark.parametrize("cls", [
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")('fvEpP'),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")('vlanCktEp'),
        pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                           reason="no --apic")('actrlRule'),
    ])
    def test_tracequery(self, moDir, cls):
        """
        Query every leaf in the fabric for some concrete objects and try to
        find at least one response. If we don't get that, we fail
        """
        traceResponse = 0
        nodes = moDir.lookupByClass(
            'fabricNode', propFilter='eq(fabricNode.role,"leaf"')
        assert len(nodes) > 0

        for node in nodes:
            a = cobra.mit.request.TraceQuery(node.dn, cls)
            print(a.getUrl(moDir._accessImpl._session))
            mos = moDir.query(a)
            for mo in mos:
                print(mo.dn)
            traceResponse += len(mos)
        assert traceResponse > 0


class Test_services_devicepackage:

    fakePackage = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               fakeDevicePackageZip)
    realPackage = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               realDevicePackageZip)

    def test_packagevalidate(self):
        """
        Make sure that invalid device packages throw an exception when validation
        is enabled
        """
        with pytest.raises(AttributeError):
            cobra.services.UploadPackage(self.fakePackage, validate=True)

    def test_packagedonotvalidate(self):
        """
        Make sure that if validation is not enabled, no exception is thrown
        """
        packageUpload = cobra.services.UploadPackage(self.fakePackage)
        assert packageUpload.devicePackagePath == self.fakePackage

    def test_uploadpackage(self, moDir):
        """
        ensure that the device package upload returns a 200
        """
        packageUpload = cobra.services.UploadPackage(self.realPackage,
                                                     validate=True)
        r = moDir.commit(packageUpload)
        assert r.status_code == 200

    def test_validateupload(self, moDir):
        """
        make sure that the uploaded device package is found
        """
        uni = cobra.model.pol.Uni('')
        infra = cobra.model.infra.Infra(uni)
        vnsQuery = cobra.mit.request.DnQuery(infra.dn)
        vnsQuery.propFilter = 'eq(vnsMDev.vendor,"CISCO")'
        vnsQuery.queryTarget = 'subtree'
        vnsQuery.classFilter = 'vnsMDev'
        packages = moDir.query(vnsQuery)
        assert len(packages) > 0
        package = packages[0]
        assert package.vendor == 'CISCO'
        assert package.model == 'ASA'
        # for package in packages:
        #   print '\n'.join(['%s:\t%s' % (k,getattr(package,k)) for k in package.meta.props.names])
        #   print package.dn
