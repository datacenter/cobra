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


from cobra.mit.request import AbstractRequest
import zipfile


class UploadPackage(AbstractRequest):

    """Upload L4-L7 device packages to APIC
    
    Attributes:
      data (str): A string containing the payload for this request in JSON
        format - readonly

      devicePackagePath (str): Path to the device package on the local
        file system. No Path verification is performed, so any errors
        accessing the specified file will be raised directly to the calling
        function.
        
        Note:
           If validation is requested, the device package contents are verified
           to contain a device specification XML/JSON document

      options (str): The HTTP request query string for this object - readonly

      id (None or int): An internal troubleshooting value useful for tracing
        the processing of a request within the cluster

      uriBase (str): The base URI used to build the URL for queries and
        requests
    """

    def __init__(self, devicePackagePath, validate=False):
        """Upload a device package to an APIC.
        
        :func:`cobra.mit.access.MoDirectory.commit` is required to commit the
        upload.

        Args:
          devicePackagePath (str): Path to the device package on the local
            file system
          validate (bool): If true, the device package will be validated
            locally before attempting to upload

        """
        super(UploadPackage, self).__init__()
        self.__validate = validate
        self.devicePackagePath = devicePackagePath
        self.uriBase = "/ppi/node/mo"

    def requestargs(self, session):
        """Get the request arguments for this object.

        Args:
          session (cobra.mit.session.AbstractSession): The session to be used
            to build the the requestarguments

        Returns:
          dict: A dictionary containing the arguments
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
        return open(self.__devicePackagePath, 'rb').read()

    def getUrl(self, session):
        """Get the URL for this request, includes all options as well.
        
        Args:
          session (cobra.mit.session.AbstractSession): The session to use for
            this query.

        Returns:
          str: A string containing the request url
        """
        return session.url + self.getUriPathAndOptions(session)

    @property
    def devicePackagePath(self):
        return self.__devicePackagePath

    @devicePackagePath.setter
    def devicePackagePath(self, devicePackagePath):
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
                                         'device specification '
                                         'document'.format(devicePackagePath))

        self.__devicePackagePath = devicePackagePath
