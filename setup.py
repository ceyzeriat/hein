#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv, exit
import os, re


m = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hein", "_version.py")).read()
version = re.findall(r"__version__ *= *\"(.*?)\"", m)[0]

if "upl" in argv[1:]:
    import os
    os.system("python setup.py sdist")
    os.system("twine upload -r pypi ./dist/hein-{}.tar.gz".format(version))
    exit()

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup
    setup


setup(
    name = "hein",
    version = version,
    author = "Guillaume Schworer",
    author_email = "guillaume.schworer@gmail.com",
    packages = ["hein"],
    url = "https://github.com/ceyzeriat/hein/",
    license = "GNU General Public License v3 or later (GPLv3+)",
    description = "Advanced Subscriber-Publisher Socket Communication",
    long_description = open("README.rst").read() + "\n\n"
                    + "Changelog\n"
                    + "---------\n\n"
                    + open("HISTORY.rst").read(),
    package_data = {"": ["LICENSE", "AUTHORS.rst", "HISTORY.rst", "README.rst"]},
    include_package_data = True,
    install_requires = ['byt'],
    download_url = 'https://github.com/ceyzeriat/hein/tree/master/dist',
    keywords = ['socket', 'communication', 'publisher', 'transmitter', 'emitter', 'receiver', 'subscriber', 'process', 'inter', 'interprocess'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        'Intended Audience :: Education',
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation :: Sphinx",
    ],
)

