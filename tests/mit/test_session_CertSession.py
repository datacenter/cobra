from builtins import str
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

import pytest

pytestmark = pytest.mark.skipif(pytest.config.getvalue('apic') == [],
                                reason="You must specify at least one --apic " +
                                       "option on the CLI")

from os.path import join, exists
from os import remove, rmdir
import tempfile
from cobra.mit.session import CertSession, LoginSession
from cobra.mit.request import ConfigRequest, DnQuery, CommitError
from cobra.mit.access import MoDirectory
pytest.importorskip("cobra.model")
from cobra.model.pol import Uni
from cobra.model.aaa import User, UserEp, UserCert, UserDomain, UserRole
from cobra.model.fv import Tenant, BD, Ap

class UserObject(object):
    def __init__(self, user="rouser"):
        self.session = None
        self.pkey = None
        self.user = user
        self.certDn = 'uni/userext/user-{0}/usercert-{1}Cert'.format(self.user,
                                                                     self.user)
        self.uni = Uni('')
        self.aaaUserEp = UserEp(self.uni)
        self.aaaUser = User(self.aaaUserEp, name=user)
        # Set the users up in the "all" user domain...
        self.aaaUserDomain = UserDomain(self.aaaUser, name='all')
        self.aaaUserCert = UserCert(self.aaaUser, name=self.user + "Cert",
                                    data="")
        # Read only user can only read things, read/write user has admin privs.
        if self.user == 'rouser':
            self.aaaUserRole = UserRole(self.aaaUserDomain, name='read-all', privType='readPriv')
        elif user == 'rwuser':
            self.aaaUserRole = UserRole(self.aaaUserDomain, name='admin', privType="writePriv")
        else:
            raise NotImplementedError("This user does not have a aaaUserRole " +
                                      "implemented")
        # End result is we should expect the read only user to see a failure
        # when they try to commit a change...


# Do tests for a read only user as well as a read/write (admin level) user.
#@pytest.fixture(scope="session", params=["rouser"])
@pytest.fixture(scope="session", params=["rouser", "rwuser"])
def userobject(request):
    param = request.param
    userobj = UserObject(user=param)
    return userobj


class CertSessionObject(object):
    def __init__(self, user="rouser"):
        self.key = None
        self.cert = None
        self.tmpfiles = []
        self.tmpdir = tempfile.mkdtemp()
        self.certfile = join(self.tmpdir, "cert.pem")
        self.payloadfile = join(self.tmpdir, "payload")
        self.pkeyfile = join(self.tmpdir, "pkey.pem")
        self.sigbinfile = self.pkeyfile + "_sig.bin"
        self.sigbasefile = self.pkeyfile + "_sig.base64"
        self.gen_x509_cert()

    def cleanup(self):
        """
        Clean up all the temporary files and directories
        """
        for fileName in self.tmpfiles:
            try:
                remove(fileName)
            except:
                pass
        try:
            rmdir(self.tmpdir)
        except:
            pass

    def gen_cert_openssl(self, sign_method='sha256', subject=None,
                         serial_num=1000, not_before=0,
                         not_after=3650*24*60*60):

        try:
            from OpenSSL import crypto
        except ImportError:
            raise

        def gen_pkey(obj, type, bitlen=1024):
            """
            Generate a key
            """
            key = crypto.PKey()
            key.generate_key(type, bitlen)
            obj.key = key

        cert = crypto.X509()
        if subject is None:
            subject = {
                'C':  'US',    'ST': 'CA',   'L':  'SJ',
                'O':  'INSBU', 'OU': 'Work','CN':  'Anyone',
            }
            cert.get_subject().C = subject['C']
            cert.get_subject().ST = subject['ST']
            cert.get_subject().L = subject['L']
            cert.get_subject().O = subject['O']
            cert.get_subject().OU = subject['OU']
            cert.get_subject().CN = subject['CN']
        else:
            cert.set_subject(subject)
        cert.set_serial_number(serial_num)
        cert.gmtime_adj_notBefore(not_before)
        cert.gmtime_adj_notAfter(not_after)
        cert.set_issuer(cert.get_subject())
        gen_pkey(self, crypto.TYPE_RSA)
        cert.set_pubkey(self.key)
        cert.sign(self.key, sign_method)
        self.cert = cert
        self.writeFile(fileDir=self.tmpdir, fileName=self.certfile,
                       fileData=crypto.dump_certificate(crypto.FILETYPE_PEM,
                                                        self.cert))
        self.tmpfiles.append(self.certfile)
        self.writeFile(fileDir=self.tmpdir, fileName=self.pkeyfile,
                       fileData=crypto.dump_privatekey(crypto.FILETYPE_PEM,
                                                       self.key))
        self.tmpfiles.append(self.pkeyfile)

    def gen_cert_subprocess(self):
        import subprocess
        def runCmd(cmd):
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, error = proc.communicate()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode,
                                                    " ".join(cmd),
                                                    out)
            return out

        cmd = ["openssl", "req", "-x509", "-nodes", "-days", "3650", "-subj",
               '/C=US/ST=California/L=SJ/O=INSBU/OU=Work/CN=Anyone',
               "-newkey", "rsa:1024", "-keyout", self.pkeyfile, "-out",
               self.certfile]
        out = runCmd(cmd)
        self.tmpfiles.append(self.pkeyfile)
        self.tmpfiles.append(self.certfile)


    def gen_x509_cert(self):
        """
        This is a simply a wrapper around the two methods we use to generate
        the keys and certificates.  One is using pyopenssl and the other is
        subprocess and openssl directly.  They both have their trade-offs.
        """
        try:
            self.gen_cert_openssl()
        except ImportError:
            self.gen_cert_subprocess()

    @staticmethod
    def writeFile(fileDir=None, fileName=None, fileData=None, mode="wt"):
        """
        Write data to a file
        """
        if fileName == None or fileDir == None or fileData == None:
            return
        with open(join(fileDir, fileName), mode) as f:
            f.write(fileData)

    @staticmethod
    def readFile(fileDir=None, fileName=None, mode="rt"):
        """
        Read a file and return the data
        """
        if fileName == None and fileDir == None:
            return
        with open(join(fileDir, fileName), mode) as f:
            fileData = f.read()
        return fileData


# This fixture sets up the certificate object which is a rather complicated and
# involved object.  I could have made these static files but I wanted to make
# sure I tested the method(s) that were being used to generate the keys used
# to generate the signature.
@pytest.fixture(scope="module")
def certobject(request):
    certobject = CertSessionObject()
    #def cleanup():
    #    certobject.cleanup()
    #request.addfinalizer(cleanup)
    return certobject




# For each apic setup a moDir object
@pytest.fixture(scope="module", params=pytest.config.getvalue('apic'))
def moDir(request):
    url, user, password, secure = request.param
    secure = False if secure == 'False' else True
    session = LoginSession(url, user, password,
                           secure=secure, requestFormat='json')
    md = MoDirectory(session)
    md.login()
    return md

# For each apic return a url and if the server cert should be verified by the
# client
@pytest.fixture(scope="module", params=pytest.config.getvalue('apic'))
def apics(request):
    url, user, password, secure = request.param
    return [url, secure]

# Only do the tests that pass, once one fails, skip the rest
@pytest.mark.incremental
class TestCertSession(object):

    def test_cert_setup(self, certobject):
        # Ensure that the setup fixture does its job
        # Private key is stored in this file
        assert exists(certobject.pkeyfile) == True
        # Cert is stored in this file
        assert exists(certobject.certfile) == True

    def test_post_cert_to_local_user(self, moDir, certobject, userobject):
        # Update the user object with the cert data
        userobject.aaaUserCert.data = certobject.readFile(
            fileName=certobject.certfile)
        # Commit the user to the APIC with the cert
        cr = ConfigRequest()
        cr.addMo(userobject.aaaUser)
        r = moDir.commit(cr)
        assert r.status_code == 200

    def test_get_tn(self, apics, certobject, userobject):
        apic = apics[0]
        secure = False if apics[1] == 'False' else True
        userobject.pkey = certobject.readFile(
            fileName=certobject.pkeyfile)
        session = CertSession(apic, userobject.certDn, userobject.pkey,
                              secure=secure)
        moDir = MoDirectory(session)
        dnQuery = DnQuery('uni/tn-common')
        #dnQuery.subtree = "full"
        tq = moDir.query(dnQuery)
        assert len(tq) == 1
        tq = tq[0]
        assert tq.parentDn == 'uni'
        assert str(tq.dn) == 'uni/tn-common'

    def test_post_tn(self, apics, certobject, userobject):
        apic = apics[0]
        secure = False if apics[1] == 'False' else True
        userobject.pkey = certobject.readFile(
            fileName=certobject.pkeyfile)
        session = CertSession(apic, userobject.certDn, userobject.pkey,
                              secure=secure)
        moDir = MoDirectory(session)
        uni = Uni('')
        fvTenant = Tenant(uni, name='t')
        fvBD = BD(fvTenant, 't-bd')
        fvAp = Ap(fvTenant, 't-app')
        cr = ConfigRequest()
        cr.subtree = 'full'
        cr.addMo(fvTenant)
        if userobject.user == 'rouser':
            with pytest.raises(CommitError) as excinfo:
                r = moDir.commit(cr)
            assert excinfo.value.reason == ('user rouser does not have ' +
                                            'domain access to config Mo, ' +
                                            'class fvTenant')
        elif userobject.user == 'rwuser':
            r = moDir.commit(cr)
        else:
            raise NotImplementedError

# leaving the users and the tenant for now
