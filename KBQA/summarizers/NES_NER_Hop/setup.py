"""Defines setuptools metadata."""

import setuptools

setuptools.setup(
    name="NES_NER_Hop",
    packages=setuptools.find_packages(),
    install_requires=["rdflib==6.0.2", "requests==2.26.0"],
    python_requires=">=3.8",
)
