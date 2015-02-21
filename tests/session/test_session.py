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

from os.path import join, dirname, realpath
import pytest
from cobra.mit.session import LoginSession, CertSession

CERT_DIR = dirname(realpath(__file__))
KEY_FILE = 'akey.pem'
CERT_FILE = 'acert.pem'
CERT_USER = 'auser'
CERT_DN = 'uni/userext/user-{0}/usercert-{0}Cert'.format(CERT_USER)

# KEY_FILE is a text file
with open(join(CERT_DIR, KEY_FILE), "r") as file:
    KeyPEMdata = file.read()

@pytest.mark.mit_session_Success_LoginSession
class Test_mit_session_Success_LoginSession:
    # Test the properties get set properly on LoginSession instantiation
    @pytest.mark.parametrize("session, url, user, password, secure, timeout,"
                             "requestFormat", [
        (LoginSession('http://2.2.2.2:7777', 'c', 'd'),
             'http://2.2.2.2:7777', 'c', 'd', False, 90, 'xml'), # Test expected default
        (LoginSession('http://1.1.1.1:80', 'a', 'b', True, 180, requestFormat='json'),
             'http://1.1.1.1:80', 'a', 'b', True, 180, 'json'),
        (LoginSession('http://1.1.1.1:80', 'a', 'b', True, 180, requestFormat='xml'),
            'http://1.1.1.1:80', 'a', 'b', True, 180, 'xml'),
    ])
    def test_LoginSession_init(self, session, url, user, password, secure,
                                   timeout, requestFormat):
       assert session.url == url
       assert session.user == user
       assert session.password == password
       assert session.secure == secure
       assert session.timeout == timeout
       assert session.formatStr == requestFormat

@pytest.mark.mit_session_Raises_LoginSession
class Test_mit_session_Raises_LoginSession:
    # Test that LoginSession raises an exception when passed an invalid property
    @pytest.mark.parametrize("url, user, password, secure, timeout,"
                              "requestFormat", [
        ('http://1.1.1.1:80', 'a', 'b', True, 180, 'yaml'),
    ])
    def test_LoginSession_init_raises(self, url, user, password, secure,
                                      timeout, requestFormat):
        with pytest.raises(NotImplementedError):
            LoginSession(url, user, password, secure, timeout,
                         requestFormat=requestFormat)

@pytest.mark.mit_session_CertSession
class Test_mit_session_CertSession:
    def test_CertSession_init_xml(self):
        # Did not parametrize it  because doing so causes a huge amount of output
        # from the private key
        session = CertSession('http://5.5.5.5:8080', CERT_DN, KeyPEMdata, True,
                              270, requestFormat='xml')
        assert session.url == 'http://5.5.5.5:8080'
        assert session.certificateDn == CERT_DN
        assert session.privateKey == KeyPEMdata
        assert session.secure == True
        assert session.timeout == 270
        assert session.formatStr == 'xml'

    def test_CertSession_init_json_1(self):
        session = CertSession('http://1.1.1.1', CERT_DN, KeyPEMdata,
                              requestFormat='json')
        # Testing some defaults
        assert session.url == 'http://1.1.1.1'
        assert session.certificateDn == CERT_DN
        assert session.privateKey == KeyPEMdata
        assert session.secure == False
        assert session.timeout == 90 
        assert session.formatStr == 'json'

    def test_CertSession_init_json_2(self):
        session = CertSession('http://154.98.2.1:32184', CERT_DN, KeyPEMdata, True,
                              timeout=5)
        # Testing some defaults
        assert session.url == 'http://154.98.2.1:32184'
        assert session.certificateDn == CERT_DN
        assert session.privateKey == KeyPEMdata
        assert session.secure == True
        assert session.timeout == 5
        # Testing this default
        assert session.formatStr == 'xml'

    def test_CertSession_signature_inline(self):
        uri = '/api/mo/uni/infra.json'
        data = ('{"infraInfra": {"children": [{"fvnsVlanInstP": {"attributes' +
                '": {"status": "created,modified", "name": "hr-floor2", "all' +
                'ocMode": "dynamic"}, "children": [{"fvnsEncapBlk": {"attrib' +
                'utes": {"status": "created,modified", "to": "vlan-250", "fr' +
                'om": "vlan-201", "name": "encap"}}}]}}]}}')
        session = CertSession('https://1.1.1.1', CERT_DN, KeyPEMdata)
        signature = session._generateSignature(uri, data, forceManual=False)
        assert signature == ('  APIC-Request-Signature=EcFKou3x0jGSUqwAZqCR3' +
                             'OYlbiGX4GCe45Zjh4T/Q3tBElTwnMMhZH/agZHIdDJwUhv' +
                             'jHgaYHsSup9smMokM2LB0xavMeW37NvX7fndg3MHlUFMrl' +
                             'hOQ4aaoD02Ey4Ta+V/Iv/gcPxv3lfWCZZub+aIyJ9atLsE' +
                             'BHLYAOZtmupE=; APIC-Certificate-Algorithm=v1.0' +
                             '; APIC-Certificate-Fingerprint=fingerprint; AP' +
                             'IC-Certificate-DN=uni/userext/user-auser/userc' +
                             'ert-auserCert')

    def test_CertSession_signature_manual(self):
        uri = '/api/mo/uni/infra.json'
        data = ('{"infraInfra": {"children": [{"fvnsVlanInstP": {"attributes' +
                '": {"status": "created,modified", "name": "hr-floor2", "all' +
                'ocMode": "dynamic"}, "children": [{"fvnsEncapBlk": {"attrib' +
                'utes": {"status": "created,modified", "to": "vlan-250", "fr' +
                'om": "vlan-201", "name": "encap"}}}]}}]}}')
        session = CertSession('https://1.1.1.1', CERT_DN, KeyPEMdata)
        signature = session._generateSignature(uri, data, forceManual=True)
        assert signature == ('  APIC-Request-Signature=EcFKou3x0jGSUqwAZqCR3' +
                             'OYlbiGX4GCe45Zjh4T/Q3tBElTwnMMhZH/agZHIdDJwUhv' +
                             'jHgaYHsSup9smMokM2LB0xavMeW37NvX7fndg3MHlUFMrl' +
                             'hOQ4aaoD02Ey4Ta+V/Iv/gcPxv3lfWCZZub+aIyJ9atLsE' +
                             'BHLYAOZtmupE=; APIC-Certificate-Algorithm=v1.0' +
                             '; APIC-Certificate-Fingerprint=fingerprint; AP' +
                             'IC-Certificate-DN=uni/userext/user-auser/userc' +
                             'ert-auserCert')

@pytest.mark.mit_session_Raises_CertSession
class Test_mit_session_Raises_CertSession:
    # Test that CertSession raises an exception when passed an invalid property
    def test_CertSession_init_raises(self):
        with pytest.raises(NotImplementedError):
            CertSession('http://5.5.5.5:8080', CERT_DN, KeyPEMdata, True,
                              270, requestFormat='yaml')

