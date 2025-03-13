Get data
===========

This section contains functions to retrieve specific datasets related to financial instruments transparency and regulation:

**FITRS**:
Fetches the most recent aggregated trading data for various financial instruments, covering trading volumes, average trade sizes, and transaction numbers under the Financial Instruments Transparency System (FITRS).

**SSR**:
Retrieves data on shares that are exempt from Short Selling Regulations (SSR), providing insights into the list of securities that are excluded from SSR restrictions.

Get last available FITRS data
-------------------------

.. autofunction::  esma_data_py.EsmaDataLoader.load_latest_files

Get SSR (Short Selling Regulation) exempted shares data
------------------------

.. autofunction:: esma_data_py.EsmaDataLoader.load_ssr_exempted_shares

