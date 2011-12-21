#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from scoopy import NAME, VERSION, AUTHOR

README = open('README.md').read().strip()
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries :: Python Modules',
]
DEPENDENCIES = [
    'distribute',
    'oauth2',
]
try:
    import json
except ImportError:
    DEPENDENCIES.append('simplejson')

setup(
    name = NAME,
    version = VERSION,
    description = 'A python library to access the Scoop.it API',
    long_description = README,
    author = AUTHOR,
    author_email = 'mattoufootu@gmail.com',
    url = 'https://github.com/mattoufoutu/scoopy',
    install_requires = DEPENDENCIES,
    license = 'GPL',
    classifiers = CLASSIFIERS,
    packages = ['scoopy'],
    package_data = {'scoopy': ['tests/data/*.json']},
    test_suite = 'scoopy.tests',
)
