# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The session module for the ACI Python SDK (cobra)."""

from builtins import str     # pylint:disable=redefined-builtin
from builtins import object  # pylint:disable=redefined-builtin

try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign

    INLINE_SIGNATURE = True
except ImportError:
    INLINE_SIGNATURE = False

# Always import these just for tests
import os
import tempfile
import subprocess
# This is used for inline signatures only
import base64
import time
import math
import json

from .codec import XMLMoCodec, JSONMoCodec
from cobra.internal.rest.accessimpl import RestAccess
from cobra.mit.request import LoginRequest, RefreshRequest, RestError


class AbstractSession(object):
    """Abstract session class

    Other sessions classes should derive from this class.

    Attributes:
      secure (bool): Only used for https. If True the remote server will be
        verified for authenticity.  If False the remote server will not be
        verified for authenticity - readonly

      timeout (int): Request timeout - readonly

      url (str): The APIC or fabric node URL - readonly

      formatType (str): The format type for the request - readonly

      formatStr (str): The format string for the request, either xml or json
        - readonly
    """
    XML_FORMAT, JSON_FORMAT = 0, 1

    def __init__(self, controllerUrl, secure, timeout, requestFormat):
        """Initialize an AbstractSession instance

        Args:
          controllerURL (str): The URL to reach the controller or fabric node
          secure (bool): Only used for https. If True the remote server will be
            verified for authenticity.  If False the remote server will not be
            verified for authenticity.
          timeout (int): Request timeout
          requestFormat (str): The format to send the request in.
            Valid values are xml or json.

        Raises:
          NotImplementedError: If the requestFormat is not valid
        """
        if requestFormat not in {'xml', 'json'}:
            raise NotImplementedError("requestFormat should be one of: %s" %
                                      {'xml', 'json'})
        self.__secure = secure
        self.__timeout = timeout
        self.__controllerUrl = controllerUrl
        if requestFormat == 'xml':
            self.__format = AbstractSession.XML_FORMAT
            self.__codec = XMLMoCodec()
        elif requestFormat == 'json':
            self.__format = AbstractSession.JSON_FORMAT
            self.__codec = JSONMoCodec()
        self._accessimpl = RestAccess(self)

    @property
    def secure(self):
        """Get the secure value.

        Returns:
          bool: True if the certificate for remote device should be verified,
            False otherwise.
        """
        return self.__secure

    @property
    def timeout(self):
        """Get the request timeout value.

        Returns:
          int: The time a request is allowed to take before an error is raised.
        """
        return self.__timeout

    @property
    def url(self):
        """Get the URL for the remote system.

        Returns:
          str: The URl for the remote system.
        """
        return self.__controllerUrl

    @url.setter
    def url(self, url):
        """Set the URL for the remote system.

        This is primarily used to handle redirects.

        Args:
          url (str): The URL to use for the controller.
        """
        self.__controllerUrl = url

    @property
    def formatType(self):
        """Get the format type for this session.

        Returns:
          int: The format type represented as an integer
        """
        return self.__format

    @property
    def formatStr(self):
        """Get the format string for this session.

        Returns:
          str: The formatType represented as a string.  Currently this is
            either 'xml' or 'json'.
        """
        return 'xml' if self.__format == AbstractSession.XML_FORMAT else 'json'

    @property
    def codec(self):
        """Get the codec being used for this session.

        Returns:
          cobra.mit.codec.AbstractCodec: The codec being used for this session.
        """
        return self.__codec

    def login(self):
        """Login to the remote server.

        A generic login method that should be overridden by classes that derive
        from this class
        """
        pass

    def logout(self):
        """Logout from the remote server.

        A generic logout method that should be overridden by classes that
        derive from this class
        """
        pass

    def refresh(self):
        """Refresh the session to the remote server.

        A generic refresh method that should be overridden by classes that
        derive from this class
        """
        pass

    def get(self, queryObject):
        """Perform a query using the specified queryObject.

        Args:
          queryObject(cobra.mit.request.AbstractQuery): The query object to
            use for the query.

        Returns:
          cobra.mit.mo.Mo: The query response parsed into a managed object
        """
        return self._accessimpl.get(queryObject)

    def post(self, requestObject):
        """Perform a request using the specified requestObject.

        Args:
          requestObject(cobra.mit.request.AbstractRequest): The request object
            to use for the request.

        Returns:
          requests.response: The raw requests response.
        """
        return self._accessimpl.post(requestObject)


class LoginError(Exception):
    """Represents exceptions that occur during logging in

    These exceptions usually involve a timeout or invalid authentication
    parameters
    """

    def __init__(self, errorCode, reasonStr):
        """Initialize a LoginError instance

        Args:
          errorCode (int): The error code for the exception
          reasonStr (str): A string indicating why the exception occurred
        """
        super(LoginError, self).__init__(reasonStr)
        self.error = errorCode
        self.reason = reasonStr

    def __str__(self):
        return self.reason


class LoginSession(AbstractSession):
    """A login session with a username and password

    Note:
      The username and password are stored in memory.

    Attributes:
      user (str): The username to use for this session - readonly

      password (str): The password to use for this session - readonly

      cookie (str or None): The authentication cookie string for this session

      challenge (str or None): The authentication challenge string for this
        session

      version (str or None): The APIC software version returned once
        successfully logged in - readonly

      refreshTime (str or None): The relative login refresh time. The session
        must be refreshed by this time or it times out - readonly

      refreshTimeoutSeconds (str or None): The number of seconds for which this
        session is valid - readonly

      secure (bool): Only used for https. If True the remote server will be
        verified for authenticity.  If False the remote server will not be
        verified for authenticity - readonly

      timeout (int): Request timeout - readonly

      url (str): The APIC or fabric node URL - readonly

      formattype (str): The format type for the request - readonly

      formatStr (str): The format string for the request, either xml or json
        - readonly
    """

    # pylint:disable=too-many-arguments
    def __init__(self, controllerUrl, user, password, secure=False, timeout=90,
                 requestFormat='xml'):
        """Initialize a LoginSession instance

        Args:
          controllerURL (str): The URL to reach the controller or fabric node
          user (str): The username to use to authenticate
          password (str): The password to use to authenticate
          secure (bool): Only used for https. If True the remote server will be
            verified for authenticity.  If False the remote server will not be
            verified for authenticity.
          timeout (int): Request timeout
          requestFormat (str): The format to send the request in.
            Valid values are xml or json.
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
        """Get the username being used for this session.

        This can not be changed.  If you need to change the session username,
        instantiate a new session object.

        Returns:
          str: The username for this session.
        """
        return self._user

    @property
    def password(self):
        """Get the password being used for this session.

        This can not be changed. if you need to change the session password,
        instantiate a new session object.

        Returns:
          str: The session password.
        """
        return self._password

    @property
    def cookie(self):
        """Get the session cookie value.

        Returns:
          str: The value of the session cookie.
        """
        return self._cookie

    @cookie.setter
    def cookie(self, cookie):
        """Set the cookie for the session.

        Args:
          cookie (str): The value to set the cookie to.
        """
        self._cookie = cookie

    @property
    def challenge(self):
        """Get the challenge key value.

        Returns:
          str: The challeng key value.
        """
        return self._challenge

    @challenge.setter
    def challenge(self, challenge):
        """Set the challenge key.

        Args:
          challenge (str): The value to set the challenge key to.
        """
        self._challenge = challenge

    @property
    def version(self):
        """Get the version.

        Returns:
          str: The version returned by the login request.
        """
        return self._version

    @property
    def refreshTime(self):
        """Get the refresh time.

        Returns:
          int: The refresh time returned by the login request.
        """
        return self._refreshTime

    @property
    def refreshTimeoutSeconds(self):
        """Get the refresh timeout in seconds.

        Returns:
          int: The refresh timeout in seconds returned by the login request.
        """
        return self._refreshTimeoutSeconds

    # pylint:disable=unused-argument
    def getHeaders(self, uriPathAndOptions, data):
        """Get the HTTP headers for a given URI path and options string

        Args:
          uriPathAndOptions (str): The full URI path including the
            options string
          data (str): The payload

        Returns:
          dict: The headers for this session class
        """
        headers = {'Cookie': 'APIC-cookie=%s' % self.cookie}
        if self._challenge:
            headers['APIC-challenge'] = self._challenge
        return headers

    def login(self):
        """Login in to the remote server (APIC or Fabric Node)

        Raises:
          LoginError: If there was an error during login or the response could
            not be parsed.
        """
        loginRequest = LoginRequest(self.user, self.password)
        try:
            rsp = self._accessimpl.post(loginRequest)
        except RestError as ex:
            self._parseResponse(ex.reason)
        self._parseResponse(rsp)

    def logout(self):
        """Logout of the remote server (APIC or Fabric Node)

        Currently this method does nothing
        """
        pass

    def refresh(self):
        """Refresh a session with the remote server (APIC or Fabric Node)

        Raises:
          LoginError: If there was an error when refreshing the session or
            the response could not be parsed.
        """
        refreshRequest = RefreshRequest(self.cookie)
        rsp = self._accessimpl.get(refreshRequest)
        self._parseResponse(rsp)

    def _parseResponse(self, rsp):
        """Parse a response to a LoginRequest or a RefreshRequest.

        Args:
          rsp (str): the response, currently only JSON is supported.

        Raises:
          LoginError: If there was no data found in the response, or the
            response could not be parsed.
        """
        rspDict = json.loads(rsp)
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
            refreshTimeoutSeconds = \
                firstRecord['aaaLogin']['attributes']['refreshTimeoutSeconds']
            version = firstRecord['aaaLogin']['attributes']['version']
            self._cookie = cookie
            self._version = version
            self._refreshTime = (int(refreshTimeoutSeconds) +
                                 math.trunc(time.time()))
            self._refreshTimeoutSeconds = int(refreshTimeoutSeconds)
        else:
            raise LoginError(0, 'Bad Response: ' + str(rsp.text))


class CertSession(AbstractSession):
    """A session using a certificate dn and private key to generate signatures

    Attributes:
      certificateDn (str): The distingushed name (Dn) for the users X.509
        certificate - readonly

      privateKey (str): The private key to use when calculating signatures.
        Must be paired with the private key in the X.509 certificate - readonly

      cookie (str or None): The authentication cookie string for this session

      challenge (str or None): The authentication challenge string for this
        session

      version (str or None): The APIC software version returned once
        successfully logged in - readonly

      refreshTime (str or None): The relative login refresh time. The session
        must be refreshed by this time or it times out - readonly

      refreshTimeoutSeconds (str or None): The number of seconds for which this
        session is valid - readonly

      secure (bool): Only used for https. If True the remote server will be
        verified for authenticity.  If False the remote server will not be
        verified for authenticity - readonly

      timeout (int): Request timeout - readonly

      url (str): The APIC or fabric node URL - readonly

      formattype (str): The format type for the request - readonly

      formatStr (str): The format string for the request, either xml or json
        - readonly
    """

    # pylint:disable=too-many-arguments
    def __init__(self, controllerUrl, certificateDn, privateKey, secure=False,
                 timeout=90, requestFormat='xml'):
        """Initialize a CertSession instance

        Args:
          controllerURL (str): The URL to reach the controller or fabric node
          certificateDn (str): The distinguished name of the users certificate
          privateKey (str): The private key to be used to calculate a signature
          secure (bool): Only used for https. If True the remote server will be
            verified for authenticity.  If False the remote server will not be
            verified for authenticity.
          timeout (int): Request timeout
          requestFormat (str): The format to send the request in.
            Valid values are xml or json.
        """
        super(CertSession, self).__init__(controllerUrl, secure, timeout,
                                          requestFormat)
        self.__certificateDn = certificateDn
        self.__privateKey = privateKey

    @property
    def certificateDn(self):
        """Get the certificateDn for the user for this session.

        Returns:
          str: The certifcate Dn for this session.
        """
        return self.__certificateDn

    @property
    def privateKey(self):
        """Get the private key for this session.

        Returns:
          str: The private key as a string.
        """
        return self.__privateKey

    def getHeaders(self, uriPathAndOptions, data):
        """Get the HTTP headers for a given URI path and options string

        Args:
          uriPathAndOptions (str): The full URI path including the
            options string
          data (str): The payload

        Returns:
          dict: The headers for this session class
        """
        cookie = self._generateSignature(uriPathAndOptions, data)
        return {'Cookie': cookie}

    def login(self):
        """login method has no relevancy for this class but is included for
        consistency.
        """
        pass

    def logout(self):
        """logout method has no relevancy for this class but is included for
        consistency.
        """
        pass

    def refresh(self):
        """refreshSession method has no relevancy for this class but is
        included for consistency.
        """
        pass

    @staticmethod
    def runCmd(cmd):
        """Convenience method to run a command using subprocess

        Args:
          cmd (str): The command to run

        Returns:
          str: The output from the command

        Raises:
          subprocess.CalledProcessError: If an non-zero return code is sent by
            the process

        """
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, error = proc.communicate()  # pylint:disable=unused-variable
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode,
                                                " ".join(cmd),
                                                out)
        return out

    @staticmethod
    def writeFile(fileName=None, mode="w", fileData=None):
        """Convenience method to write data to a file

        Args:
          fileName (str): The file to write to, default = None
          mode (str): The write mode, default = "w"
          fileData (varies): The data to write to the file
        """
        if fileName is None:
            return
        if fileData is None:
            fileData = ""
        with open(fileName, mode) as aFile:
            aFile.write(fileData)

    @staticmethod
    def readFile(fileName=None, mode="r"):
        """Convenience method to read some data from a file

        Args:
          fileName (str): The file to read from, default = None
          mode (str): The read mode, default = "r", Windows may require "rb"

        Returns:
          str: The data read from the file
        """
        if fileName is None:
            return ""
        with open(fileName, mode) as aFile:
            fileData = aFile.read()
        return fileData

    # this should probably be refactored at some point.
    # pylint:disable=too-many-locals
    def _generateSignature(self, uri, data, forceManual=False):
        """Generate a signature over the uri and data.

        This signature is used to authenticate with the APIC and must be
        calculated for each transaction because the signature is calculated
        using the uri and data if any.

        Args:
          uri (str): The string that represents the URI for the transaction.
            The uri is everything from api to the end of the options.
          data (str): The payload for the request that will be sent.
          forceManual (bool): If True, the signature will be calculated using
            subprocess to execute openssl commands, otherwise pyOpenSSL is
            used.

        Returns:
          str: A string containing the cookie that should be used in the
            request.
        """
        # One global that is not changing in the rest of the file is ok
        global INLINE_SIGNATURE  # pylint:disable=global-statement
        # Added for easier testing of each signature generation method
        if forceManual:
            INLINE_SIGNATURE = False

        privateKeyStr = str(self.privateKey)
        certDn = str(self.certificateDn)

        if uri.endswith('?'):
            uri = uri[:-1]
        uri = uri.replace('//', '/')

        if INLINE_SIGNATURE:
            if data is None:
                payLoad = 'GET' + uri
            else:
                payLoad = 'POST' + uri + data

            pkey = load_privatekey(FILETYPE_PEM, privateKeyStr)

            signedDigest = sign(pkey, payLoad.encode(), 'sha256')
            signature = base64.b64encode(signedDigest).decode()
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
                self.writeFile(payloadFile, mode="wt",
                               fileData='POST' + uri + data)
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
                except:  # pylint:disable=bare-except
                    pass
                try:
                    os.rmdir(tempDir)
                except:  # pylint:disable=bare-except
                    pass

        cookieFmt = ("  APIC-Request-Signature=%s;" +
                     " APIC-Certificate-Algorithm=v1.0;" +
                     " APIC-Certificate-Fingerprint=fingerprint;" +
                     " APIC-Certificate-DN=%s")
        return cookieFmt % (signature, certDn)
