# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = "esma_data_py",
    version="0.0.1",
    author = "Hadrien Leclerc, Yassine Aoukaili",
    author_email="hadrien.leclerc@esma.europa.eu",
    description = "Tools to easily download ESMA financial data",
    long_description=long_description,
    
    packages=setuptools.find_packages(),
    license="EUROPEAN UNION PUBLIC LICENCE v. 1.2",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved",
        "Operating System :: OS Independent"
        ],
    license_files=("LICENSE.md",),
    install_requires=[
        "pandas>=2.0.0",
        "tqdm>=4.65.0",
        "requests>=2.31.0",
        ],
    python_requires=">=3.7",
    test_suite="",
    tests_require=[]
    
)
