Codec Module
=================
.. module:: codec

The codec module allows conversion from either an ACI Managed object to
XML/JSON strings or XML/JSON strings to ACI managed objects.

MoCodec
-------

This is an abstract class used as a base class for the other protocol specific
codecs.

.. autoclass:: cobra.mit.codec.MoCodec
   :members:
   :special-members:
   :exclude-members: __weakref__

XMLMoCodec
----------

The XMLMoCodec can convert from ACI managed objects to XML strings or from XML
strings to ACI managed objects.

.. autoclass:: cobra.mit.codec.XMLMoCodec
   :members:
   :special-members:


JSONMoCodec
-----------

The JSONMoCodec can convert from ACI managed objects to JSON strings or from
JSON strings to ACI managed objects.

.. autoclass:: cobra.mit.codec.JSONMoCodec
   :members:
   :special-members:
