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
        self.test_args = ['--junitxml=unittests.xml']
        self.test_suite = True

    def run_tests(self):
        #import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

install_requires = ['requests']

# Doc build instructions:
# Clone the repo
# cd into the main repo directory
# install with the [docs] extra as an editable install:  pip install -e .[docs]
# cd into the docs directory
# do a make html
# Built docs are in docs/build/html
docs_requires = install_requires + ['sphinx<1.3', 'sphinxcontrib-napoleon']

tests_requires = install_requires + ['pytest', 'responses']

setup(
    name='acicobra',
    version='0.1',
    description='Rest API client for the Cisco ACI',
    author='Cisco Systems Inc',
    author_email='acicobra@external.cisco.com',
    url='https://github.com/datacenter/cobra',
    packages=find_packages(exclude=['examples']),
    namespace_packages = ['cobra'],
    long_description="""\
        Access API for the Management Information Tree.
        """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Data Center',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='data center networking configuration management',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    install_requires=install_requires,
    extras_require={
        'ssl': ['pyOpenSSL',],
        'docs': docs_requires,
    },
    tests_require=tests_requires,
    cmdclass = {'test': PyTest},
)
