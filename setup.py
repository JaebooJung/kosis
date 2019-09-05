# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="kosis",
    packages=find_packages(),
    version="0.0.1",
    author="KIM, Doh-hyoung",
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        "lxml",
        "pandas",
        "requests",
        "xmltodict",
    ],
)
