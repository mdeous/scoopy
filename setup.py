#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bootstrap distribute
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

from scoopy import NAME, VERSION, AUTHOR

DEPENDENCIES = open('pip-requirements.txt').read().split()
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
)
