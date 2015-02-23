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


try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
    inlineSignature = True
except ImportError:
    inlineSignature = False

# Always import these just for tests
import os
import tempfile
import subprocess
# This is used for inline signatures only
import base64
import time
import math

class AbstractSession(object):
    XML_FORMAT, JSON_FORMAT = 0, 1

    def __init__(self, controllerUrl, secure, timeout, requestFormat):
        if requestFormat not in {'xml', 'json'}:
            raise NotImplementedError("requestFormat should be one of: %s" %
                                                             {'xml', 'json'})
        self.__secure = secure
        self.__timeout = timeout
        self.__controllerUrl = controllerUrl
        if requestFormat == 'xml':
            self.__format = AbstractSession.XML_FORMAT
        elif requestFormat == 'json':
            self.__format = AbstractSession.JSON_FORMAT

    @property
    def secure(self):
        """
        verifies server authenticity
        """
        return self.__secure

    @property
    def timeout(self):
        """
        communication timeout for the connection
        """
        return self.__timeout

    @property
    def url(self):
        return self.__controllerUrl

    @property
    def formatType(self):
        return self.__format

    @property
    def formatStr(self):
        return 'xml' if self.__format == AbstractSession.XML_FORMAT else 'json'

    def login(self):
        pass

    def logout(self):
        pass

    def refresh(self):
        pass


class LoginError(Exception):

    def __init__(self, errorCode, reasonStr):
        self.error = errorCode
        self.reason = reasonStr

    def __str__(self):
        return self.reason


class LoginSession(AbstractSession):

    """
    The LoginSession class creates a login session with a username and password
    """

    def __init__(self, controllerUrl, user, password, secure=False, timeout=90,
                 requestFormat='xml'):
        """
        Args:
            user (str): Username
            password (str): Password
        """
        super(LoginSession, self).__init__(controllerUrl, secure, timeout,
                                           requestFormat)
        self._user = user
        self._password = password
        self._cookie = None
        self._challenge = None
        self._version = None
        self._refreshTime = None
        self._refreshTimeoutSeconds = None

    @property
    def user(self):
        """
        Returns the username.
        """
        return self._user

    @property
    def password(self):
        """
        Returns the password.
        """
        return self._password

    @property
    def cookie(self):
        """
        Authentication cookie for this session
        """
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
        self._cookie = cookie

    @property
    def challenge(self):
        """
        Authentication challenge for this session
        """
        return self._challenge

    @challenge.setter
    def challenge(self, challenge):
        self._challenge = challenge

    @property
    def version(self):
        """
        Returns APIC version received from aaaLogin
        """
        return self._version

    @property
    def refreshTime(self):
        """
        Returns the relative login refresh time. The session must be
        refreshed by this time or it times out
        """
        return self._refreshTime

    @property
    def refreshTimeoutSeconds(self):
        """
        Returns the number of seconds for which this LoginSession is
        valid
        """
        return self._refreshTimeoutSeconds

    def getHeaders(self, uriPathAndOptions, data):
        headers = {'Cookie': 'APIC-cookie=%s' % self.cookie}
        if self._challenge:
            headers['APIC-challenge'] = self._challenge
        return headers

    def _parseResponse(self, rsp):
        rspDict = rsp.json()
        data = rspDict.get('imdata', None)
        if not data:
            raise LoginError(0, 'Bad Response: ' + str(rsp.text))

        firstRecord = data[0]
        if 'error' in firstRecord:
            errorDict = firstRecord['error']
            reasonStr = errorDict['attributes']['text']
            errorCode = errorDict['attributes']['code']
            raise LoginError(errorCode, reasonStr)
        elif 'aaaLogin' in firstRecord:
            cookie = firstRecord['aaaLogin']['attributes']['token']
            refreshTimeoutSeconds = firstRecord['aaaLogin']['attributes']['refreshTimeoutSeconds']
            version = firstRecord['aaaLogin']['attributes']['version']
            self._cookie = cookie
            self._version = version
            self._refreshTime = int(refreshTimeoutSeconds) + math.trunc(time.time())
            self._refreshTimeoutSeconds = int(refreshTimeoutSeconds)
        else:
            raise LoginError(0, 'Bad Response: ' + str(rsp.text))


class CertSession(AbstractSession):

    """
    The CertSession class creates a login session using a certificate dn and
    private key
    """

    def __init__(self, controllerUrl, certificateDn, privateKey, secure=False,
                 timeout=90, requestFormat='xml'):
        """
        Args:
            cert (str): Certificate String
        """
        super(CertSession, self).__init__(controllerUrl, secure, timeout,
                                          requestFormat)
        self.__certificateDn = certificateDn
        self.__privateKey = privateKey

    @property
    def certificateDn(self):
        """
        Returns the certificate dn.
        """
        return self.__certificateDn

    @property
    def privateKey(self):
        """
        Returns the private key.
        """
        return self.__privateKey

    def getHeaders(self, uriPathAndOptions, data):
        cookie = self._generateSignature(uriPathAndOptions, data)
        return {'Cookie': cookie}

    @staticmethod
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

    @staticmethod
    def writeFile(fileName=None, mode="w", fileData=None):
        if fileName is None:
            return
        if fileData is None:
            fileData = ""
        with open(fileName, mode) as aFile:
            aFile.write(fileData)

    @staticmethod
    def readFile(fileName=None, mode="r"):
        if fileName is None:
            return ""
        with open(fileName, mode) as aFile:
            fileData = aFile.read()
        return fileData

    def _generateSignature(self, uri, data, forceManual=False):
        # One global that is not changing in the rest of the file is ok
        global inlineSignature
        # Added for easier testing of each signature generation method
        if forceManual:
            inlineSignature = False

        privateKeyStr = str(self.privateKey)
        certDn = str(self.certificateDn)

        if uri.endswith('?'):
            uri = uri[:-1]
        uri = uri.replace('//', '/')

        if inlineSignature:
            if data is None:
                payLoad = 'GET' + uri
            else:
                payLoad = 'POST' + uri + data

            pkey = load_privatekey(FILETYPE_PEM, privateKeyStr)
            signedDigest = sign(pkey, payLoad, 'sha256')
            signature = base64.b64encode(signedDigest)
        else:
            tmpFiles = []
            tempDir = tempfile.mkdtemp()
            payloadFile = os.path.join(tempDir, "payload")
            keyFile = os.path.join(tempDir, "pkey")
            sigBinFile = keyFile + "_sig.bin"
            sigBaseFile = keyFile + "_sig.base64"

            if data is None:
                self.writeFile(payloadFile, mode="wt", fileData='GET' + uri)
            else:
                self.writeFile(payloadFile, mode="wt", fileData='POST' + uri + data)
            tmpFiles.append(payloadFile)

            self.writeFile(fileName=keyFile, mode="w", fileData=privateKeyStr)
            tmpFiles.append(keyFile)

            cmd = ["openssl", "dgst", "-sha256", "-sign", keyFile, payloadFile]
            cmd_out = self.runCmd(cmd)
            self.writeFile(fileName=sigBinFile, mode="wb", fileData=cmd_out)
            tmpFiles.append(sigBinFile)

            cmd = ["openssl", "base64", "-in", keyFile + "_sig.bin", "-e",
                   "-out", sigBaseFile]
            self.runCmd(cmd)
            tmpFiles.append(sigBaseFile)

            sigBase64 = self.readFile(fileName=sigBaseFile)
            signature = "".join(sigBase64.splitlines())

            for fileName in tmpFiles:
                try:
                    os.remove(fileName)
                except:
                    pass
                try:
                    os.rmdir(tempDir)
                except:
                    pass

        cookieFmt = ("  APIC-Request-Signature=%s;" +
                     " APIC-Certificate-Algorithm=v1.0;" +
                     " APIC-Certificate-Fingerprint=fingerprint;" +
                     " APIC-Certificate-DN=%s")
        return cookieFmt % (signature, certDn)
