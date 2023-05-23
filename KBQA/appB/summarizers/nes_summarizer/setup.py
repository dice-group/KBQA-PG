"""Defines setuptools metadata."""

import setuptools

setuptools.setup(
    name="nes_summarizer",
    version="0.3",
    packages=setuptools.find_packages(),
    install_requires=["rdflib==6.0.2", "requests==2.31.0"],
    python_requires=">=3.8",
)
