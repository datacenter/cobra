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

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

sys.path.append(vmanPath)
import vman
vman.VERSION_FILE = os.path.join(gitRoot, 'build/pkg/VERSION.yml')
version = vman.Version()
versionStr = version.stringify(openDelim='-', closeDelim='')

setup(
    name='acicobra',
    version=versionStr,
    description='Access API for the Management Information Tree',
    author='Cisco Systems',
    author_email='gurssing@cisco.com',
    url='',
    packages=find_packages(exclude=['model', 'zen', 'zen.formatter*', 'examples']),
    namespace_packages = ['cobra'],
    long_description="""\
        Access API for the Management Information Tree.
        """,
    classifiers=[
        "License :: Cisco Systems Inc. (Copyright 2013 - 2014)",
        "Programming Language :: Python",
        "Development Status :: 0 - Pre-alpha",
        "Intended Audience :: Developers",
        "Topic :: Data Center",
    ],
    keywords='data center networking configuration management',
    license='Cisco Systems Inc. (Copyright 2013 - 2014)',
    install_requires=[
        'setuptools',
        'requests',
    ],
    extras_require={
        'ssl': ['pyOpenSSL',],
    },
    tests_require = ['pytest', 'responses'],
    cmdclass = {'test': PyTest},
)
