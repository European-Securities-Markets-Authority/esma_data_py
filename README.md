# esma_data_py

[[Build Status](https://github.com/hadrilec/esma_data_py/actions/workflows/pkgTests.yml/badge.svg)]
(https://github.com/hadrilec/esma_data_py/actions)

![Codecov test coverage](https://app.codecov.io/gh/hadrilec/esma_data_py/branch/master/graph/badge.svg?token=TO96FMWRHK)
[Codecov Coverage Link](https://codecov.io/gh/hadrilec/esma_data_py?branch=master)

![Documentation Status](https://readthedocs.org/projects/esma-data-py/badge/?version=latest)
[Documentation Link](https://pynsee.readthedocs.io/en/latest/?badge=latest)

![Python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)
[Python Versions Link](https://www.python.org/)

![Code formatting](https://img.shields.io/badge/code%20style-black-000000.svg)
[Code Formatting Link](https://pypi.org/project/black/)

![License](https://img.shields.io/badge/license-EUPL-blue)
[License Link](https://img.shields.io/badge/license-EUPL-blue)

<br />

The *esma_data_py* package provides a robust toolkit designed to streamline the process of searching for and downloading data from the ESMA (European Securities and Markets Authority) register. At the core of this package is *EsmaDataLoader*, an engine that simplifies the process of accessing and downloading regulatory data. This Python package facilitates easy access to reliable and up-to-date information, supporting financial analysts, researchers, and developers who need data from ESMA.

This package is a contribution to reproducible research and public data transparency.

## Key features

* **MIFID Data**: You can use the `load_mifid_file_list` method to fetch a list of MIFID files from specified ESMA databases filtering by creation or publication date.
* **FIRDS Data**: You can retrieve data both with the `load_latest_files`, applying filters by instrument type and optionally by CFI codes and ISINs, or with the `load_fca_firds_file_list` by retrieving a list of FCA files.
* **SSR Data**: You can retrieve SSR data with the `load_ssr_exempted_shares` method, optionally filtering the results to include only records relevant to the current date.

## Getting Started

To get started with *esma_data_py*, you can install the package directly from GitHub:

#### Install the package directly from the GitHub repository
```
pip install git+https://github.com/European-Securities-Markets-Authority/esma_data_py.git
```

## Documentation

Detailed documentation for all relevant functions and modules is available in the docs directory of this repository, which includes guides and examples to help you integrate `esma_data_py` into your projects effectively.  
Doc: [http://esma-data-py.readthedocs.io/](http://esma-data-py.readthedocs.io/)

## Support

Feel free to open an issue with any questions about this package using the [GitHub repository issues](https://github.com/hadrilec/esma_data_py/issues).

## Contributing

All contributions, whatever their forms, are welcome.

