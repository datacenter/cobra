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

"""The codec module for the MIT from the ACI Python SDK (cobra)."""

from cobra.internal.codec.xmlcodec import (parseXMLError, fromXMLStr,
                                           fromXMLStream, toXMLStr)
from cobra.internal.codec.jsoncodec import (parseJSONError, fromJSONStr,
                                            toJSONStr)


class MoCodec(object):

    """A generic codec class for Mo's.

    All codecs that can convert to and from Mo must implement this class
    """

    def __init__(self):
        """Instantiate a MoCodec instance."""
        pass

    def fromStr(self, moStr):
        """Implement this method to convert an moStr into Mo.

        Args:
          moStr (str): mo in string format.

        Raises:
          NotImplementedError: This method should be overriden by classes that
            derive from this class.
        """
        raise NotImplementedError('not implemented')

    def fromStream(self, moStream):
        """Implement this method to convert an moStr into Mo.

        Args:
          moStream (str): mo in string format read from the stream.

        Raises:
          NotImplementedError: This method should be overriden by classes that
            derive from this class.
        """
        raise NotImplementedError('not implemented')

    def toStr(self, mo, includeAllProps=False, prettyPrint=False,
              excludeChildren=False):
        """Convert mo into it's string format.

        Args:
          mo (cobra.mit.mo.Mo): mo to be converted.
          includeAllProps (bool, optional): True if Dn and Rn are required to
            be included in to output.  The default is False.
          prettyPrint (bool, optional): True if output needs to be human
            readable.  The default is False.
          excludeChildren (bool, optional): True if child mo objects need not
            be included in the output.  The default is False.

        Raises:
          NotImplementedError: This method should be overriden by classes that
            derive from this class.
        """
        raise NotImplementedError('not implemented')

    def error(self, errorStr, errorClass, httpCode=None):
        """Parse the error string and raise an exception.

        The exception that will be raised should be defined by the error class.

        Args:
            errorStr (str): formatted error string to be parsed.
            errorClass (class): class instance to be raised for this error.
            httpCode (int, optional): optional http code to be included in the
              error.  The default is None.

        Raises:
          NotImplementedError: This method should be overriden by classes that
            derive from this class.
        """
        raise NotImplementedError('not implemented')


class XMLMoCodec(MoCodec):

    """A XML codec to convert Mo to and from XML format."""

    def __init__(self):
        """Initialize a instance of XMLMoCodec."""
        super(XMLMoCodec, self).__init__()

    def fromStr(self, moStr):
        """Convert an xml formatted string into a mo.

        Args:
          moStr (str): mo in xml format

        Returns:
          list: A list of managed objects converted from the xml
        """
        return fromXMLStr(moStr)

    def fromStream(self, moStream):
        """Convert an xml stream into a mo.

        Args:
          moStream (str): mo in xml format read from the stream.

        Returns:
          list: A list of managed objects converted from the xml.
        """
        return fromXMLStream(moStream)

    def toStr(self, mo, includeAllProps=False, prettyPrint=False,
              excludeChildren=False):
        """Convert the mo into xml format.

        Args:
          mo (cobra.mit.mo.Mo): mo to be converted.
          includeAllProps (bool, optional): True if Dn and Rn are required to
            be included in to output.  The default is False.
          prettyPrint (bool, optional): True if output needs to be human
            readable.  The default is False.
          excludeChildren (bool, optional): True if child mo objects need not
            be included in the output.  The default is False.

        Returns:
          str: string representing the mo in xml format
        """
        return toXMLStr(mo, includeAllProps, prettyPrint, excludeChildren)

    def error(self, errorStr, errorClass, httpCode=None):
        """Parse the xml error string and raise an exception.

        The exception that will be raised should be defined by the error class.

        Args:
          errorStr (str): xml formatted error string to be parsed.
          errorClass (class): class instance to be raised for this error.
          httpCode (int, optional): optional http code to be included in the
            error.  The default is None.
        """
        parseXMLError(errorStr, errorClass, httpCode)


class JSONMoCodec(MoCodec):

    """A JSON codec to convert Mo to and from XML format."""

    def __init__(self):
        """Instantiate a JSONMoCodec instance."""
        super(JSONMoCodec, self).__init__()

    def fromStr(self, moStr):
        """Convert an json formatted string into mo.

        Args:
          moStr (str): mo in json format.

        Returns:
          list: A list of managed objects converted from the json.
        """
        return fromJSONStr(moStr)

    def fromStream(self, moStream):
        """Convert an json stream into mo.

        Args:
          moStream (str): mo in json format read from the stream.

        Returns:
          list: A list of managed objects converted from the json.
        """
        jsonStr = moStream.read()
        return self.fromStr(jsonStr)

    def toStr(self, mo, includeAllProps=False, prettyPrint=False,
              excludeChildren=False):
        """Convert mo into json format.

        Args:
          mo (cobra.mit.mo.Mo): mo to be converted.
          includeAllProps (bool, optional): True if Dn and Rn are required to
            be included in to output.  The default is False.
          prettyPrint (bool, optional): True if output needs to be human
            readable.  The default is False.
          excludeChildren (bool, optional): True if child mo objects need not
            be included in the output.  The default is False.

        Returns:
          str: string representing the mo in json format
        """
        return toJSONStr(mo, includeAllProps, prettyPrint, excludeChildren)

    def error(self, errorStr, errorClass, httpCode=None):
        """Raise an exception based based on the received errorStr.

        Parse the json error string and raise an exception defined by the error
        class

        Args:
          errorStr (str): json formatted error string to be parsed.
          errorClass (class): class instance to be raised for this error.
          httpCode (int, optional): optional http code to be included in the
            error.  The default is None.
        """
        parseJSONError(errorStr, errorClass, httpCode)
