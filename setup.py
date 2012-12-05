#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
head2cydef - Convert C header files to Cython definition files.

:copyright:
    lion krischer (krischer@geophysik.uni-muenchen.de), 2012
:license:
    gnu lesser general public license, version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from __future__ import with_statement

import inspect
import os
from setuptools import setup

LOCAL_PATH = os.path.abspath(os.path.split(inspect.getfile(
                             inspect.currentframe()))[0])
DOCSTRING = __doc__.split("\n")

NAME = "head2cydef"
AUTHOR = "Lion Krischer"
AUTHOR_EMAIL = "krischer@geophysik.uni-muenchen.de"
URL = "None so far..."
LICENSE = "GNU General Public License, version 3 (GPLv3)"
KEYWORDS = ["cython"]
INSTALL_REQUIRES = ["clang", "colorama"]


def getVersion():
    """
    Get the current version of the module.
    """
    version_file = os.path.join(LOCAL_PATH, "head2cydef", "VERSION.txt")
    with open(version_file) as f:
        version = f.read().strip()
    return version


def setupPackage():
    # setup package
    setup(
        name=NAME,
        version=getVersion(),
        description=DOCSTRING[1],
        long_description="\n".join(DOCSTRING[3:]),
        url=URL,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        platforms="OS Independent",
        keywords=KEYWORDS,
        packages=["head2cydef"],
        package_dir={"head2cydef": "head2cydef"},
        zip_safe=False,
        install_requires=INSTALL_REQUIRES,
    )


if __name__ == "__main__":
    setupPackage()
