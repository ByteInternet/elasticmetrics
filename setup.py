#!/usr/bin/env python
"""
elasticmetrics
--------------

ElasticSearch metrics
"""
import os
import os.path
from setuptools import setup, find_packages
from elasticmetrics import __version__

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Networking :: Monitoring"
]

long_description = __doc__
with open(os.path.join(os.path.dirname(__file__), "README.rst")) as fh:
    long_description = fh.read()

setup_params = dict(
    name="elasticmetrics",
    packages=find_packages(exclude=['tests']),
    version=__version__,
    description="ElasticSearch metrics",
    long_description=long_description,
    author="Farzad Ghanei",
    author_email="farzad.ghanei@byte.nl",
    url="https://github.com/ByteInternet/elasticmetrics",
    license="MIT",
    classifiers=classifiers,
    keywords="elasticsearch metrics",
    test_suite="tests",
    zip_safe=True
)

setup_params["extras_require"] = {"dev": ["pytest", "mock", "pycodestyle"]}


if __name__ == "__main__":
    setup(**setup_params)
