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


"""
This module provides an interface to uploading L4-7 device packages to the 
controller. Refer to the "Developing L4-L7 Device Packages" document for more
information on creating device packages

Example::

    moDir = cobra.mit.access.MoDirectory(
        cobra.mit.session.LoginSession('https://apic', 'admin', 'password'))
    moDir.login()

    packageUpload = cobra.services.UploadPackage('asa-device-pkg.zip')
    r = moDir.commit(packageUpload)

"""

from cobra.mit.request import AbstractRequest
import zipfile


class UploadPackage(AbstractRequest):

    """
    Class for uploading L4-L7 device packages to APIC
    """

    def __init__(self, devicePackagePath, validate=False):
        """
        Create an UploadPackage object that can be passed to MoDirectory.commit

        :param devicePackagePath: Path to the device package on the local file
            system
        :type devicePackagePath: str

        :param validate: If true, the device package will be validated locally
            before attempting to upload
        :type validate: bool

        """
        super(UploadPackage, self).__init__()
        self.__validate = validate
        self.devicePackagePath = devicePackagePath
        self.uriBase = "/ppi/node/mo"

    def requestargs(self, session):
        """
        Returns the POST arguments for this request

        :param session: session object for which the request will be sent
        :type session: cobra.mit.session.AbstractSession

        :returns: requests style kwargs that can be passed to request.post()
        :rtype: dict
        """
        uriPathandOptions = self.getUriPathAndOptions(session)
        headers = session.getHeaders(uriPathandOptions, self.data)
        kwargs = {
            'headers': headers,
            'verify': session.secure,
            'files': {
                'file': self.data
            }
        }
        return kwargs

    @property
    def data(self):
        """
        Returns the data this request should post

        :returns: string containing contents of device package
        :rtype: str
        """
        return open(self.__devicePackagePath, 'rb').read()

    def getUrl(self, session):
        """
        Returns the URI this request will access

        :param session: session object for which the request will be sent
        :type session: cobra.mit.session.AbstractSession
        """
        return session.url + self.getUriPathAndOptions(session)

    # property setters / getters for this class

    @property
    def devicePackagePath(self):
        """
        Returns the currently configured path to the device package

        :returns: Path to the device package on the local file system
        :rtype: str
        """
        return self.__devicePackagePath

    @devicePackagePath.setter
    def devicePackagePath(self, devicePackagePath):
        """
        Sets the device package path for this request and if validation is
        requested, will ensure that the device package contains the
        device specification XML/JSON document

        :param devicePackagePath: Path to the device package on the local
            file system. No path verification is performed, so any errors
            accessing the specified file will be raised directly to the calling
            function.
        :type devicePackagePath: str
        """
        if self.__validate:
            # Device package spec will look at the first .xml document and use
            # that as the device specification, so it must contain at least
            # one .xml document
            with zipfile.ZipFile(devicePackagePath, 'r') as devpkg:
                packagefiles = devpkg.namelist()
                for _ in packagefiles:
                    if _.endswith('.xml'):
                        break
                else:
                    raise AttributeError('Device package {0} missing required '
                                         'device specification document'.format(
                                             devicePackagePath))

        self.__devicePackagePath = devicePackagePath
