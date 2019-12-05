# Copyright (c) '2015' Cisco Systems, Inc. All Rights Reserved

import sys
if sys.version_info[0] == 3:
    from builtins import str
from builtins import object

import importlib


class ClassLoader(object):
    @classmethod
    def loadClass(cls, fqClassName):
        fqClassName = str(fqClassName)
        moduleName, className = fqClassName.rsplit('.', 1)
        module = importlib.import_module(moduleName)
        return getattr(module, className)
