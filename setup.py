#!/usr/bin/env python

import setuptools
from screen_translator import __version__

setuptools.setup(
    name='screen_translator',
    version=__version__,
    author="Kings Lee",
    package_dir={"": "screen_translator/src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)