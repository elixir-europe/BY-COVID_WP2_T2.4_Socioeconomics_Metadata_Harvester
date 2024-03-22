#!/usr/bin/env python3
# Author(s): Markus Tuominen
# Copyright 2022 Finnish Social Science Data Archive FSD / University of Tampere
# Licensed under the EUPL. See LICENSE.txt for full license.

import setuptools


with open('README.rst', 'r', encoding='UTF-8') as fh:
    long_description = fh.read()


with open('VERSION', 'r', encoding='UTF-8') as fh:
    version = fh.readline().strip()


setuptools.setup(
    name='by-covid-xml-transformer',
    version=version,
    url='',
    description='Harvest and transform metadata',
    long_description=long_description,
    long_description_content_type='text/rst',
    license='EUPL v1.2',
    author='Markus Tuominen',
    author_email='markus.tuominen@tuni.fi',
    packages=setuptools.find_packages(),
    install_requires=[
        ''
    ],
    entry_points={'console_scripts': [
        ''
    ]}
)
