import unittest
import os
import pandas as pd
import sys
import functools

from esma_data_py.esma_data_loader import EsmaDataLoader
from esma_data_py.utils.utils import Utils


class EdlTests(unittest.TestCase):

    version = (sys.version_info[0] == 3) & (sys.version_info[1] == 10)
    version = True

    if version == True:
    
        def test_load_latest_files(self):
            edl = EsmaDataLoader()
            test  = edl.load_latest_files()
            self.assertTrue(isinstance(test, pd.DataFrame))

        def test_load_fca(self):
            edl = EsmaDataLoader()
            test = edl.load_fca_firds_file_list()   
            self.assertTrue(isinstance(test, pd.DataFrame))

        def test_load_mifid(self):
            edl = EsmaDataLoader()
            test = edl.load_mifid_file_list()
            self.assertTrue(isinstance(test, pd.DataFrame))

        def test_download_file(self):
            u = Utils()
            _test = u.download_and_parse_file('https://fitrs.esma.europa.eu/fitrs/FULECR_20250308_E_1of1.zip', save=True)
            cached_test = u.download_and_parse_file('https://fitrs.esma.europa.eu/fitrs/FULECR_20250308_E_1of1.zip')
            self.assertTrue(isinstance(cached_test, pd.DataFrame))

        def test_wrong_cfi(self):
            edl = EsmaDataLoader()
            test = edl.load_latest_files(cfi='TEST')
            self.assertTrue(test is None)

        def test_wrong_dataset(self):
            edl = EsmaDataLoader()
            test = edl.load_mifid_file_list(datasets=['TEST'])
            self.assertTrue(test is None)

        def test_latest_files_wrong_isin(self):
            edl = EsmaDataLoader()
            test = edl.load_latest_files(isin=['TEST'])
            self.assertTrue(isinstance(test, pd.DataFrame))

                        
if __name__ == '__main__':
    unittest.main()
