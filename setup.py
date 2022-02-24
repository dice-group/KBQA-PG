"""Run this module to add the KBQA as root package to the path variable."""
from setuptools import find_packages
from setuptools import setup

setup(name="kbqa-pg", packages=find_packages(exclude=["KBQA.kbqa.*"]))
