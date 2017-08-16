#!/usr/bin/env python
from setuptools import setup

setup(
    name='gogitit',
    version='0.1',
    packages=['gogitit'],
    include_package_data=True,
    install_requires=[
        'Click',
        'pyyaml',
        'GitPython',
    ],
    entry_points={
        'console_scripts': ['gogitit=gogitit.cli:main'],
    },
)
