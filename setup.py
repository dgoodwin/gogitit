#!/usr/bin/env python
from setuptools import setup

setup(
    name='gogitit',
    version='0.3',
    packages=['gogitit'],
    include_package_data=True,
    install_requires=[
        'Click',
        'pyyaml',
        'GitPython',
        'nose',
    ],
    entry_points={
        'console_scripts': ['gogitit=gogitit.cli:main'],
    },
)
