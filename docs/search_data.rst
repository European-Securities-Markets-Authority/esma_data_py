Search MIFID Data
=================

These functions are used to search a list of documents belonging either to the ESMA register or the FCA (For the latter, the functionality is available only for the FIRDS dataset). The list of files that can be searched belongs to four datasets:

**FIRDS** (Financial Instruments Reference Data System): 
This dataset encompasses reference data for all financial instruments available on regulated markets across Europe. It includes essential details such as the ISIN (International Securities Identification Number), the instrument classification, issuer information, and trading market details.

**FITRS** (Financial Instruments Transparency System): 
This dataset provides aggregated data on trading volumes and transactions for various financial instruments. It covers transparency information like daily and monthly trading volumes, average trade sizes, and transaction numbers.

**SVCAP** (Single Volume Cap Mechanism):
This dataset is part of the volume cap introduced by the MiFIR review (Article 5 of MiFIR, as amended by Regulation (EU) 2024/791), which replaces DVCAP. It limits to 7% the share of trading under the reference price waiver in an equity or equity-like instrument, measured against the total trading volume in that instrument across the EU over the previous 12 months. When the cap is exceeded, trading venues must suspend the use of the waiver for that instrument. For each ISIN and 12-month reporting period, the results files (SVCRES) report the total EU trading volume and the percentage of trading under the waiver. ESMA also publishes suspension files (Excel format), which are also included in the files list returned. However, this package cannot download or parse them. To read them, download the file from its link and open it with standard Excel tools.

**DVCAP** (Double Volume Cap Mechanism) - *Discontinued*: 
This dataset has been discontinued by ESMA and replaced by SVCAP from October 2025. It was part of the regulatory measures to limit the impact of dark trading on price discovery and market integrity. It includes detailed records of trading volumes executed under waivers from pre-trade transparency requirements. DVCAP data shows the percentage of total trading volume executed in dark pools versus regulated markets. It specifically tracks the percentage of trading in a specific instrument that occurs in dark pools and compares it to a set cap, ensuring that dark trading does not exceed regulatory limits.

Search ESMA Data
----------------

.. autofunction:: esma_data_py.EsmaDataLoader.load_mifid_file_list

Search FCA Data
---------------

.. autofunction:: esma_data_py.EsmaDataLoader.load_fca_firds_file_list
