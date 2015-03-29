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
 
from builtins import str
from builtins import object

import pytest
cobra = pytest.importorskip('cobra')
from cobra.mit.request import (AbstractRequest, AbstractQuery, LoginRequest,
                               RefreshRequest, ListDomainsRequest, DnQuery,
                               ClassQuery, TraceQuery, TagsRequest,
                               AliasRequest, ConfigRequest, MultiQuery,
                               TroubleshootingQuery, CommitError)
from cobra.mit.session import LoginSession
cobra.model = pytest.importorskip('cobra.model')
from cobra.model.pol import Uni
from cobra.model.fv import Tenant, BD
from cobra.model.fvns import VlanInstP
from cobra.model.fabric import LooseNode

@pytest.mark.mit_request_AbstractRequest
class Test_mit_request_AbstractRequest(object):

    def test_AbstractRequest_init(self):
        assert isinstance(AbstractRequest(), AbstractRequest)

    # options property needs its own test
    @pytest.mark.parametrize("prop,value", [
        ('id', '1234567890'),
        ('id', 'abcdefghijklmnopqrstuvwxyz0123456789'),
        ('uriBase', 'api'),
    ])
    def test_AbstractRequest_individual_properties(self, prop, value):
        ar = AbstractRequest()
        setattr(ar, prop, value)
        assert getattr(ar, prop) == value

    # Only the id is used for options for AbstractRequest
    @pytest.mark.parametrize("value,expected", [
        ('1234567890', '_dc=1234567890')
        ])
    def test_AbstractRequest_options_property(self, value, expected):
        ar = AbstractRequest()
        ar.id = value
        assert ar.options == expected

    @pytest.mark.parametrize("optionsDict,expected1,expected2", [
        (None, '', False),
        ({'_dc': 'only_dc_option'}, '_dc=only_dc_option', False),
        ({'option1': '1', 'option2': '2'}, 'option1=1&option2=2',
         'option2=2&option1=1'),
    ])
    def test_AbstractRequest_makeOptions(self, optionsDict, expected1,
                                         expected2):
        options = AbstractRequest.makeOptions(optionsDict)
        assert (options == expected1 or options == expected2)

    # Set dc to None to get no _dc option added
    # Set uriBase to None to get an empty string uriBase
    # These are important points for the expected value
    @pytest.mark.parametrize("sessionUrl,dc,uriBase,requestType", [
        ("http://1.1.1.1", '1', '/api', 'xml'),
        ("http://1.1.1.1", '1', '/api', 'json'),
        ("http://2.2.2.2", '2', '/api/class', 'xml'),
        ("http://2.2.2.2", '2', '/api/class', 'json'),
        ("http://3.3.3.3", '3', '/api/mo', 'xml'),
        ("http://3.3.3.3", '3', '/api/mo', 'json'),
        ("http://4.4.4.4", '4', '/aaaLoginRequest', 'xml'),
        ("http://4.4.4.4", '4', '/aaaLoginRequest', 'json'),
        ("http://5.5.5.5", '5', None, 'xml'),
        ("http://5.5.5.5", '5', None, 'json'),
        ("http://6.6.6.6", None, None, 'xml'),
        ("http://6.6.6.6", None, None, 'json'),
        ("http://7.7.7.7", None, 'hello', 'xml'),
        ("http://7.7.7.7", None, 'hello', 'json'),
    ])
    def test_AbstractRequest_getUriPathAndOptions(self, sessionUrl, dc,
                                                  uriBase, requestType):
        expected = '.' + requestType
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        ar = AbstractRequest()
        if dc is not None:
            ar.id =  dc
            expected += '?_dc=' + dc
        if uriBase is None:
            uriBase = ''
        ar.uriBase = uriBase
        expected = uriBase + expected
        assert ar.getUriPathAndOptions(session) == expected


@pytest.mark.mit_request_AbstractQuery
class Test_mit_request_AbstractQuery(object):

    def test_AbstractQuery_init(self):
        assert isinstance(AbstractQuery(), AbstractQuery)

    # expected is None means you expect the same value returned that was set
    @pytest.mark.parametrize("prop,value,expected", [
        ('id', '1234567890', None),
        ('id', 'abcdefghijklmnopqrstuvwxyz0123456789', None),
        ('uriBase', 'api', None),
        ('propInclude', '_all_', None),
        ('propInclude', 'naming-only', None),
        ('propInclude', 'config-explicit', None),
        ('propInclude', 'config-all', None),
        ('propInclude', 'config-only', None),
        ('propInclude', 'oper', None),
        ('subtreePropFilter', 'eq(prop.name, "spf")', None),
        ('subtreeClassFilter', ['class1', 'class2', 'class3'],
            'class1,class2,class3'), # test list
        ('subtreeClassFilter', 'class1,class2,class3', None), # test string
        ('subtreeInclude', 'audit-logs', None),
        ('subtreeInclude', 'event-logs', None),
        ('subtreeInclude', 'faults', None),
        ('subtreeInclude', 'fault-records', None),
        ('subtreeInclude', 'health', None),
        ('subtreeInclude', 'health-records', None),
        ('subtreeInclude', 'deployment-records', None),
        ('subtreeInclude', 'relations', None),
        ('subtreeInclude', 'stats', None),
        ('subtreeInclude', 'tasks', None),
        ('subtreeInclude', 'count', None),
        ('subtreeInclude', 'no-scoped', None),
        ('subtreeInclude', 'required', None),
        ('propFilter', 'ne(prop.name, "pf")', None),
        ('queryTarget', 'self', None),
        ('queryTarget', 'subtree', None),
        ('queryTarget', 'children', None),
        ('classFilter', 'class1,class2,class3', None), # test string
        ('classFilter', ['class1', 'class2', 'class3'],
            'class1,class2,class3'), # test list
        ('subtree', 'full', None),
        ('subtree', 'children', None),
        ('subtree', 'no', None),
        ('orderBy', ['sort1', 'sort2', 'sort3'],
            'sort1,sort2,sort3'),
        ('orderBy', 'sort1,sort2,sort3', 'sort1,sort2,sort3'),
        ('pageSize', 3, 3),
        ('pageSize', 100, 100),
        ('replica', 1, None),
        ('replica', 2, None),
        ('replica', 3, None),
    ])
    def test_AbstractQuery_individual_properties(self, prop, value, expected):
        aq = AbstractQuery()
        setattr(aq, prop, value)
        if expected is None:
            assert getattr(aq, prop) == value

    def test_AbstractQuery_options(self):
        aid = '1234567890'
        expectedOptions = ''
        aq = AbstractQuery()
        aq.id = aid
        expectedOptions += '_dc=' + aid
        assert aq.options == expectedOptions

    @pytest.mark.parametrize("prop,value,errorType", [
        ('propInclude', 'bogus', ValueError),
        ('subtreeInclude', 'bogus', ValueError),
        ('queryTarget', 'bogus', ValueError),
        ('subtree', 'bogus', ValueError),
        ('replica', 4, ValueError),
        ('replica', "1", ValueError),
        ('replica', 'bogus', ValueError),
    ])
    def test_AbstractQuery_not_allowed_values(self, prop, value, errorType):
        aq = AbstractQuery()
        with pytest.raises(errorType):
            setattr(aq, prop, value)

@pytest.mark.mit_request_LoginRequest
class Test_mit_request_LoginRequest(object):

    def test_LoginRequest_init(self):
        assert isinstance(LoginRequest('user', 'password'),
                          LoginRequest)

    @pytest.mark.parametrize("user,password, prop", [
        ('user1', '1234567890', 'user'),
        ('user2', 'abcdefghijklmnopqrstuvwxyz0123456789', 'password'),
    ])
    def test_LoginRequest_individual_properties(self, user, password, prop):
        lr = LoginRequest(user, password)
        if prop == 'user':
            assert lr.user == user
        elif prop == 'password':
            assert lr.password == password
        else:
            raise NotImplementedError("Unexpected property name")

    def test_LoginRequest_requestargs(self):
        expected = {
                       'headers': {
                           'Cookie': 'APIC-cookie=None'
                        },
                        'allow_redirects': False,
                        'data': '{"aaaUser": {"attributes": ' +
                                '{"name": "admin", "pwd": "password"}}}',
                        'timeout': 90,
                        'verify': False
                   }
        session = LoginSession('http://1.1.1.1', 'admin', 'password')
        lr = LoginRequest('admin', 'password')
        assert lr.requestargs(session) == expected

    @pytest.mark.parametrize("sessionUrl", [
        ("http://1.1.1.1"),
        ("http://2.2.2.2"),
        ("http://3.3.3.3"),
        ("http://4.4.4.4"),
    ])  
    def test_LoginRequest_getUrl(self, sessionUrl):
        session = LoginSession(sessionUrl, 'admin', 'password')
        expected = sessionUrl + '/api/aaaLogin.json'
        lr = LoginRequest('admin', 'password')
        assert lr.getUrl(session) == expected


@pytest.mark.mit_request_RefreshRequest
class Test_mit_request_RefreshRequest(object):

    def test_RefreshRequest_init(self):
        assert isinstance(RefreshRequest('cookie'), RefreshRequest)

    @pytest.mark.parametrize("cookie", [
        ('cookie1'),
        ('cookie2'),
    ])  
    def test_RefreshRequest_individual_properties(self, cookie):
        rr = RefreshRequest(cookie)
        assert rr.cookie == cookie

    @pytest.mark.parametrize("sessionUrl,cookie", [
        ("http://1.1.1.1", 'cookie1'),
        ("http://2.2.2.2", 'cookie2'),
        ("http://3.3.3.3", 'cookie3'),
        ("http://4.4.4.4", 'cookie4'),
    ])  
    def test_RefreshRequest_getUrl(self, sessionUrl, cookie):
        session = LoginSession(sessionUrl, 'admin', 'password')
        expected = sessionUrl + '/api/aaaRefresh.json'
        rr = RefreshRequest(cookie)
        assert rr.getUrl(session) == expected


@pytest.mark.mit_request_ListDomainsRequest
class Test_mit_request_ListDomainsRequest(object):

    def test_ListDomainsRequest_init(self):
        assert isinstance(ListDomainsRequest(), ListDomainsRequest)

    @pytest.mark.parametrize("sessionUrl", [
        ("http://1.1.1.1"),
        ("http://2.2.2.2"),
        ("http://3.3.3.3"),
        ("http://4.4.4.4"),
    ])  
    def test_ListDomainsRequest_getUrl(self, sessionUrl):
        session = LoginSession(sessionUrl, 'admin', 'password')
        expected = sessionUrl + '/api/aaaListDomains.json'
        ldr = ListDomainsRequest()
        assert ldr.getUrl(session) == expected


@pytest.mark.mit_request_DnQuery
class Test_mit_request_DnQuery(object):

    def test_DnQuery_init(self):
        assert isinstance(DnQuery('uni/tn-common'), DnQuery)

    def test_DnQuery_options(self):
        did = '1234567890'
        expectedOptions = ''
        dq = DnQuery('uni')
        dq.id = did
        expectedOptions += '_dc=' + did
        assert dq.options == expectedOptions

    def test_DnQuery_dnStr(self):
        dn = 'uni'
        dq = DnQuery(dn)
        assert dq.dnStr == dn

    @pytest.mark.parametrize("sessionUrl,dc,requestType", [
        ("http://1.1.1.1", '1', 'xml'),
        ("http://1.1.1.1", '1', 'json'),
        ("http://2.2.2.2", '2', 'xml'),
        ("http://2.2.2.2", '2', 'json'),
        ("http://3.3.3.3", '3', 'xml'),
        ("http://3.3.3.3", '3', 'json'),
        ("http://4.4.4.4", '4', 'xml'),
        ("http://4.4.4.4", '4', 'json'),
    ])
    def test_DnQuery_getUrl(self, sessionUrl, dc, requestType):
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        dn = 'uni'
        dq = DnQuery('uni')
        expected = sessionUrl + '/api/mo/' + dn + '.' + requestType
        dq.id = dc
        expected += '?_dc=' + dc
        assert dq.getUrl(session) == expected


@pytest.mark.mit_request_ClassQuery
class Test_mit_request_ClassQuery(object):

    def test_ClassQuery_init(self):
        assert isinstance(ClassQuery('fvTenant'), ClassQuery)

    def test_ClassQuery_options(self):
        cid = '1234567890'
        expectedOptions = ''
        aq = ClassQuery('fvTenant')
        aq.id = cid
        expectedOptions += '_dc=' + cid
        assert aq.options == expectedOptions

    def test_ClassQuery_className(self):
        klass = 'fvTenant'
        cq = ClassQuery(klass)
        assert cq.className == klass

    @pytest.mark.parametrize("sessionUrl,dc,requestType", [
        ("http://1.1.1.1", '1', 'xml'),
        ("http://1.1.1.1", '1', 'json'),
        ("http://2.2.2.2", '2', 'xml'),
        ("http://2.2.2.2", '2', 'json'),
        ("http://3.3.3.3", '3', 'xml'),
        ("http://3.3.3.3", '3', 'json'),
        ("http://4.4.4.4", '4', 'xml'),
        ("http://4.4.4.4", '4', 'json'),
    ])
    def test_ClassQuery_getUrl(self, sessionUrl, dc, requestType):
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        klass = 'fvTenant'
        cq = ClassQuery(klass)
        expected = sessionUrl + '/api/class/' + klass + '.' + requestType
        cq.id = dc
        expected += '?_dc=' + dc
        assert cq.getUrl(session) == expected


@pytest.mark.mit_request_TraceQuery
class Test_mit_request_TraceQuery(object):

    def test_TraceQuery_init(self):
        assert isinstance(TraceQuery('fabric', 'fvTenant'), TraceQuery)

    def test_TraceQuery_targetClass_read(self):
        dnStr = 'uni'
        klass = 'topSystem'
        tq = TraceQuery(dnStr, klass)
        assert tq.targetClass == klass

    def test_TraceQuery_targetClass_write(self):
        dnStr1 = 'uni'
        klass1 = 'topSystem'
        klass2 = 'polUni'
        tq = TraceQuery(dnStr1, klass1)
        tq.targetClass = klass2
        assert tq.targetClass == klass2

    def test_TraceQuery_dnStr_read(self):
        dnStr = 'uni'
        klass = 'topSystem'
        tq = TraceQuery(dnStr, klass)
        assert tq.dnStr == dnStr

    def test_TraceQuery_options(self):
        tid = '1234567890'
        klass = 'fvTenant'
        tq = TraceQuery('uni', 'fvTenant')
        expectedOptions = 'target-class=' + klass
        tq.id = tid
        expectedOptions += '&_dc=' + tid
        assert tq.options == expectedOptions

    @pytest.mark.parametrize("sessionUrl,dc,requestType", [
        ("http://1.1.1.1", '1', 'xml'),
        ("http://1.1.1.1", '1', 'json'),
        ("http://2.2.2.2", '2', 'xml'),
        ("http://2.2.2.2", '2', 'json'),
        ("http://3.3.3.3", '3', 'xml'),
        ("http://3.3.3.3", '3', 'json'),
        ("http://4.4.4.4", '4', 'xml'),
        ("http://4.4.4.4", '4', 'json'),
    ])
    def test_TraceQuery_getUrl(self, sessionUrl, dc, requestType):
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        dnStr = 'uni'
        klass = 'fvTenant'
        cq = TraceQuery(dnStr, klass)
        expected = sessionUrl + '/api/trace/' + dnStr + '.' + requestType
        expected += '?target-class=' + klass
        cq.id = dc
        expected += '&_dc=' + dc
        assert cq.getUrl(session) == expected


@pytest.mark.mit_request_TagsRequest
class Test_mit_request_TagsRequest(object):

    def test_TagsRequest_init(self):
        assert isinstance(TagsRequest('fvTenant'), TagsRequest)

    def test_TagsRequest_data(self):
        tr = TagsRequest('uni')
        assert tr.data == '{}'

    def test_TagsRequest_dnStr(self):
        dnStr = 'system'
        tr = TagsRequest(dnStr)
        assert tr.dnStr == dnStr

    @pytest.mark.parametrize("addOrRemove,dnStr,value,expected", [
        ('add', 'uni', u'tag1,tag2', 'tag1,tag2'),
        ('remove', 'uni', u'tag1,tag2', 'tag1,tag2'),
        ('add', 'uni', ['tag1', 'tag2'], 'tag1,tag2'),
        ('remove', 'uni', ['tag1', 'tag2'], 'tag1,tag2'),
    ])
    def test_TagsRequest_add_remove(self, addOrRemove, dnStr, value, expected):
        tr = TagsRequest(dnStr)
        setattr(tr, addOrRemove, value)
        assert getattr(tr, addOrRemove) == expected

    @pytest.mark.parametrize("addOrRemove,dnStr,value, errorType", [
        ('add', 'uni', None, ValueError),
        ('remove', 'uni', None, ValueError),
    ])
    def test_TagsRequest_add_remove_failed(self, addOrRemove, dnStr, value,
                                           errorType):
        tr = TagsRequest(dnStr)
        with pytest.raises(errorType):
            setattr(tr, addOrRemove, value)

    def test_TagsRequest_options(self):
        tid = '1234567890'
        dnStr = 'system'
        tr = TagsRequest(dnStr, add=u'tag1', remove=u'tag2')
        expectedOptions1 = 'add=tag1&remove=tag2'
        expectedOptions2 = 'remove=tag2&add=tag1'
        tr.id = tid
        expectedOptions1 += '&_dc=' + tid
        expectedOptions2 += '&_dc=' + tid
        assert (tr.options == expectedOptions1 or
                tr.options == expectedOptions2)

    def test_TagsRequest_requestargs(self):
        expected = {
                       'data': '{}',
                       'headers': {
                           'Cookie': 'APIC-cookie=None'
                       },
                       'timeout': 90,
                       'verify': False
                   }
        session = LoginSession('http://1.1.1.1', 'admin', 'password')
        dnStr = 'uni'
        tr = TagsRequest(dnStr)
        assert tr.requestargs(session) == expected

    @pytest.mark.parametrize("sessionUrl,dc,requestType", [
        ("http://1.1.1.1", '1', 'xml'),
        ("http://1.1.1.1", '1', 'json'),
        ("http://2.2.2.2", '2', 'xml'),
        ("http://2.2.2.2", '2', 'json'),
        ("http://3.3.3.3", '3', 'xml'),
        ("http://3.3.3.3", '3', 'json'),
        ("http://4.4.4.4", '4', 'xml'),
        ("http://4.4.4.4", '4', 'json'),
    ])
    def test_TagsRequest_getUrl(self, sessionUrl, dc, requestType):
        dnStr = 'uni'
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        tr = TagsRequest(dnStr)
        expectedUrl = sessionUrl + '/api/tag/mo/' + dnStr + '.' + requestType
        tr.add = [u'tag1', u'tag2']
        tr.remove = u'tag3'
        tr.id = dc
        expectedUrl1 = expectedUrl + '?add=tag1,tag2&remove=tag3&_dc=' + dc
        expectedUrl2 = expectedUrl + '?remove=tag3&add=tag1,tag2&_dc=' + dc
        assert (tr.getUrl(session) == expectedUrl1 or
                tr.getUrl(session) == expectedUrl2)

@pytest.mark.mit_request_AliasRequest
class Test_mit_request_AliasRequest(object):

    def test_AliasRequest_init(self):
        assert isinstance(AliasRequest('fvTenant'), AliasRequest)

    def test_AliasRequest_data(self):
        dnStr = 'uni'
        tr = AliasRequest(dnStr)
        assert tr.data == '{}'

    def test_AliasRequest_options(self):
        aid = '1234567890'
        dnStr = 'system'
        aliasStr = 'alias1'
        ar = AliasRequest(dnStr, alias=aliasStr)
        expectedOptions = 'set=' + aliasStr
        ar.id = aid
        expectedOptions += '&_dc=' + aid
        assert ar.options == expectedOptions

    def test_AliasRequest_dnStr(self):
        dnStr = 'uni/tn-common'
        aliasStr = 'alias1'
        ar = AliasRequest(dnStr, alias=aliasStr)
        assert ar.dnStr == dnStr

    def test_AliasRequest_alias(self):
        dnStr = 'uni/tn-mgmt'
        aliasStr = 'alias1'
        ar = AliasRequest(dnStr)
        ar.alias = aliasStr
        assert ar.alias == aliasStr

    def test_AliasRequest_requestargs(self):
        expected = {
                       'data': '{}',
                       'headers': {
                           'Cookie': 'APIC-cookie=None'
                       },
                       'timeout': 90,
                       'verify': False
                   }
        session = LoginSession('http://1.1.1.1', 'admin', 'password')
        dnStr = 'uni'
        aliasStr = 'alias1'
        tr = AliasRequest(dnStr, aliasStr)
        assert tr.requestargs(session) == expected

    @pytest.mark.parametrize("sessionUrl,dc,aliasStr,clear,requestType", [
        ("http://1.1.1.1", '1', 'alias1', False, 'xml'),
        ("http://1.1.1.1", '1', 'alias1', False, 'json'),
        ("http://2.2.2.2", '2', 'alias2', True, 'xml'),
        ("http://2.2.2.2", '2', 'alias2', True, 'json'),
    ])
    def test_AliasRequest_getUrl(self, sessionUrl, dc, aliasStr, clear,
                                 requestType):
        dnStr = 'uni'
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        ar = AliasRequest(dnStr)
        expectedUrl = sessionUrl + '/api/alias/mo/' + dnStr + '.' + requestType
        if clear:
            ar.alias = aliasStr
            ar.clear()
            expectedUrl += '?clear=yes'
        else:
            ar.alias = aliasStr
            expectedUrl += '?set=' + aliasStr
        ar.id = dc
        expectedUrl += '&_dc=' + dc
        assert ar.getUrl(session) == expectedUrl


@pytest.mark.mit_request_ConfigRequest
class Test_mit_request_ConfigRequest(object):

    def test_ConfigRequest_init(self):
        assert isinstance(ConfigRequest(), ConfigRequest)

    def test_ConfigRequest_options(self):
        cid = '1234567890'
        expectedOptions = ''
        cr =  ConfigRequest()
        cr.id = cid
        expectedOptions += '_dc=' + cid
        assert cr.options == expectedOptions

    def test_ConfigRequest_data(self):
        expected = ('{"fvTenant": {"attributes": {"name": "test", "status": ' +
                    '"created,modified"}}}')
        polUni = Uni('')
        fvTenant = Tenant(polUni, 'test')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        assert cr.data == expected

    def test_ConfigRequest_data_raises(self):
        cr = ConfigRequest()
        with pytest.raises(CommitError):
            abc = cr.data

    def test_ConfigRequest_xmldata(self):
        expected1 = ('<?xml version="1.0" encoding="UTF-8"?>\n' +
                    '<fvTenant name=\'test\' status=\'created,modified\'>' +
                    '</fvTenant>')
        expected2 = ('<?xml version="1.0" encoding="UTF-8"?>\n' +
                    '<fvTenant status=\'created,modified\' name=\'test\'>' +
                    '</fvTenant>')
        polUni = Uni('')
        fvTenant = Tenant(polUni, 'test')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        assert (cr.xmldata == expected1 or cr.xmldata == expected2)

    def test_ConfigRequest_xmldata_raises(self):
        cr = ConfigRequest()
        with pytest.raises(CommitError):
            abc = cr.xmldata

   # expected is None means you expect the same value returned that was set
    @pytest.mark.parametrize("value", [
        ('full'),
        ('modified'),
        ('no'),
    ])
    def test_ConfigRequest_subtree(self, value):
        cr = ConfigRequest()
        cr.subtree = value
        assert cr.subtree == value

    def test_ConfigRequest_subtree_raises(self):
        cr = ConfigRequest()
        with pytest.raises(ValueError):
            cr.subtree = 'children'

    def test_ConfigRequest_requestargs(self):
        expected1 = {
                       'data': '<?xml version="1.0" encoding="UTF-8"?>\n' +
                               '<fvTenant name=\'testing\' ' +
                               'status=\'created,modified\'></fvTenant>',
                       'headers': {
                           'Cookie': 'APIC-cookie=None'
                       },
                       'timeout': 90,
                       'verify': False
                   }
        expected2 = {
                       'data': '<?xml version="1.0" encoding="UTF-8"?>\n' +
                               '<fvTenant status=\'created,modified\' ' +
                               'name=\'testing\'></fvTenant>',
                       'headers': {
                           'Cookie': 'APIC-cookie=None'
                       },
                       'timeout': 90,
                       'verify': False
                   }
        polUni = Uni('')
        fvTenant = Tenant(polUni, 'testing')
        session = LoginSession('http://1.1.1.1', 'admin', 'password')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        assert (cr.requestargs(session) == expected1 or
                cr.requestargs(session) == expected2)

    # addMo is tested in test_ConfigRequest_requestargs but we still need
    # branch testing.  See test_ConfigRequest_addMo_raises_* methods
    #def test_ConfigRequest_addMo(self):

    def test_ConfigRequest_addMo_raises_no_context(self):
        polUni = Uni('')
        cr = ConfigRequest()
        with pytest.raises(ValueError):
            cr.addMo(polUni)

    def test_ConfigRequest_addMo_raises_not_allowed_context(self):
        fvTenant = Tenant('uni', 'testing')
        fvnsVlanInstP = VlanInstP('uni/infra', 'namespace1', 'dynamic')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        with pytest.raises(ValueError):
            cr.addMo(fvnsVlanInstP)

    def test_ConfigRequest_removeMo_and_hasMo_positive(self):
        fvTenant = Tenant('uni', 'testing')
        fvnsVlanInstP = VlanInstP('uni/infra', 'namespace1', 'dynamic')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        cr.removeMo(fvTenant)
        cr.addMo(fvnsVlanInstP)
        assert cr.hasMo(fvnsVlanInstP.dn)

    def test_ConfigRequest_removeMo_and_hasMo_negative(self):
        fvTenant = Tenant('uni', 'testing')
        fvnsVlanInstP = VlanInstP('uni/infra', 'namespace1', 'dynamic')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        cr.removeMo(fvTenant)
        cr.addMo(fvnsVlanInstP)
        assert not cr.hasMo(fvTenant.dn)

    def test_ConfigRequest_removeMo_no_configMos_left(self):
        fvTenant = Tenant('uni', 'testing')
        fvnsVlanInstP = VlanInstP('uni/infra', 'namespace1', 'dynamic')
        cr = ConfigRequest()
        cr.addMo(fvTenant)
        cr.removeMo(fvTenant)
        assert not cr.hasMo(fvTenant.dn)

    def test_ConfigRequest_removeMo_raises(self):
        fvTenant = Tenant('uni', 'testing')
        cr = ConfigRequest()
        with pytest.raises(KeyError):
            cr.removeMo(fvTenant)

    @pytest.mark.parametrize("mos, expected", [
        ([None], None),
        ([], LooseNode(u'topology', u"101")),
        ([BD(u'uni/tn-testing', u'test')], Tenant(u'uni', u'testing')),
    ])
    def test_ConfigRequest_getRootMo(self, mos, expected):
        cr = ConfigRequest()
        mos.append(expected)
        for mo in mos:
            if mo is not None:
                try:
                    cr.addMo(mo)
                except ValueError:
                    pass
        assert cr.getRootMo() == expected

    @pytest.mark.parametrize("sessionUrl,mo,dc,requestType", [
        ('http://1.1.1.1', Tenant('uni', 'testing'), None, 'xml'),
        ('http://1.1.1.1', Tenant('uni', 'testing'), None, 'json'),
        ('http://1.1.1.1', Tenant('uni', 'testing'), '1', 'xml'),
        ('http://1.1.1.1', Tenant('uni', 'testing'), '1', 'json'),
    ])
    def test_ConfigRequest_getUriPathAndOptions(self, sessionUrl, mo, dc,
                                                requestType):
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)

        cr = ConfigRequest()
        cr.addMo(mo)
        expected = '/api/mo/' + str(mo.dn) + '.' + requestType
        if dc is not None:
            cr.id =  dc
            expected += '?_dc=' + dc
        assert cr.getUriPathAndOptions(session) == expected


    @pytest.mark.parametrize("sessionUrl,mo,requestType", [
        ("http://1.1.1.1", Tenant('uni', 'testing'), 'xml'),
        ("http://1.1.1.1", Tenant('uni', 'testing'), 'json'),
        ("http://2.2.2.2", VlanInstP('uni/infra', 'namespace1', 'dynamic'),
            'xml'),
        ("http://2.2.2.2", VlanInstP('uni/infra', 'namespace1', 'dynamic'),
            'json'),
    ])
    def test_ConfigRequest_getUrl(self, sessionUrl, mo, requestType):
        session = LoginSession(sessionUrl, 'admin', 'password',
                               requestFormat=requestType)
        expected = sessionUrl + '/api/mo/' + str(mo.dn) + '.' + requestType
        cr = ConfigRequest()
        cr.addMo(mo)
        assert cr.getUrl(session) == expected

@pytest.mark.mit_request_MultiQuery
class Test_mit_request_MultiQuery(object):

    def test_MultiQuery_init(self):
        assert isinstance(MultiQuery('fvTenant'), MultiQuery)

@pytest.mark.mit_request_TroubleshootingQuery
class Test_mit_request_TroubleshootingQuery(object):

    def test_TroubleshootingQuery_init(self):
        assert isinstance(TroubleshootingQuery('fvTenant'), TroubleshootingQuery)