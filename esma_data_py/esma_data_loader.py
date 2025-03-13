from datetime import datetime
from typing import List, Optional
import requests
import tempfile
import pandas as pd
import os
from tqdm import tqdm
import esma_data_py.utils.utils as u


class EsmaDataLoader:

    """
    A class for loading and processing data from ESMA (European Securities and Markets Authority) sources. 
    The methods in this class are designed to interact with ESMA's web services and APIs, download files, 
    process and parse the data into pandas dataframes.
    """

    def __init__(self, 
                 creation_date_from: str = '2017-01-01',
                 creation_date_to: Optional[str] = None, 
                 limit: str = '10000'):

        """
        Initializes the EsmaDataLoader with the specified parameters for filtering data.

        Args:
            creation_date_from (str): The start date for filtering data by creation or publication date. Should be in 'YYYY-MM-DD' format. Defaults to '2017-01-01'.
           
            creation_date_to (str, optional): The end date for filtering data. Should be in 'YYYY-MM-DD' format. If None, defaults to today's date.
           
            limit (str): The maximum number of records to fetch per request. Defaults to '10000'.

        Attributes:
            creation_date_from (str): The start date for filtering files.
            creation_date_to (str): The end date for filtering files.
            limit (str): The maximum number of records to fetch.
            query_url (u.QueryUrl): The object that constructs URLs for API queries.
        
        Examples:
            >>> loader = EsmaDataLoader(creation_date_from='2020-01-01', creation_date_to='2020-12-31', limit='5000')
            >>> loader = EsmaDataLoader()  # Default values
        """

        self.creation_date_from = creation_date_from
        self.creation_date_to = creation_date_to
        self.limit = limit

        if not self.creation_date_to:
            self.creation_date_to = str(datetime.today().strftime("%Y-%m-%d"))

        self.query_url = u.QueryUrl()
        self.__utils = u.Utils()
        self.__logger = self.__utils.set_logger(name='EsmaDataLoader')


    def load_mifid_file_list(self, datasets: List[str] = ['dvcap', 'fitrs', 'firds']):

        """
        Fetches a list of MIFID files from specified ESMA databases filtered by creation or publication dates.

        Args:
        db_list (list or str): List of database names to fetch files from. Valid databases are 'fitrs', 'firds', and 'dvcap'. Defaults to ['fitrs', 'firds', 'dvcap']. If a single string is provided, it is converted into a list.

        Returns:
        pd.DataFrame: A DataFrame aggregating the records from all specified databases, containing file details.

        Examples:
        >>> # Fetch MIFID files from 'fitrs' and 'firds' databases from January 1, 2017 to the current date
        >>> files_df = EsmaDataLoader().load_mifid_file_list()
        """

        try:
            datasets = [u.Dataset(dataset).value for dataset in datasets]
        except ValueError as ve:
            self.__logger.error(f'Error: {ve}') 

        files_dfs = []
        self.__logger.info(f'Loading {len(datasets)} datasets')
        
        for dataset in datasets:

            self.__logger.info(f'Loading {dataset} dataset')
            files_dfs.append(self.__get_files_single_df_mifid(dataset))

        self.__logger.info(f'Process done!')
        return pd.concat(files_dfs)
    

    def load_fca_firds_file_list(self):

        """
        Retrieves a list of FCA FIRDS files from the specified API based on the given parameters.

        Returns:
        pd.DataFrame: A DataFrame containing the records of files fetched based on the specified filters.

        Examples:
        >>> firds_files = EsmaDataLoader().load_fca_firds_file_list()
        """

        query_fca_firds = self.query_url.fca_firds.format(creation_date_from=self.creation_date_from, 
                                                      creation_date_to=self.creation_date_to, 
                                                      limit=self.limit)
        
        self.__logger.info(f'Requesting FCA FIRDS files')
        request = requests.get(query_fca_firds)

        if request.status_code == 200:
            self.__logger.info(f'Request successful, parsing response')
            root = request.json()
            list_of_dicts = [dd["_source"] for dd in root["hits"]["hits"]]
        else:
            self.__logger.error(f'Request failed, status code {request.status_code}')

        files = pd.DataFrame.from_records(list_of_dicts)
        self.__logger.info(f'Process done!')

        return files  


    def load_latest_files(self, 
                          file_type: str = 'Full', 
                          vcap: bool = False,
                          isin: Optional[List[str]] = [], 
                          cfi: str = 'E', 
                          eqt=True,
                          save_locally: bool = False,
                          update: bool = False):

        """
        Retrieves the latest full files from the 'fitrs' dataset, filtered by instrument type and optionally by CFI codes and ISINs.

        Args:
            isin (str or list of str, optional): ISIN(s) to filter the files. If provided, only files containing these ISINs are included.

            cfi (str or list of str, optional): CFI code(s) to further filter the files. Must be one of 'C', 'D', 'E', 'F', 'H', 'I', 'J', 'O', 'R', 'S'.

            eqt (bool): Determines if only equity instruments ('True') or non-equity instruments ('False') should be considered. Defaults to True.

        Returns:
            pd.DataFrame: A DataFrame containing the concatenated data from all files that meet the specified criteria.

        Examples:
            >>> # Example to get the latest full files for equity instruments with specific CFI codes:
            >>> files_df = EsmaDataLoader().load_latest_files()
        """

        try:
            cfi = u.Cfi(cfi).value
        except Exception as e:
            self.__logger.error(f'Error: {e}')
            return

        if vcap:
            mifid_file_list = self.__get_latest_vcap_files()
        else:
            mifid_file_list = self.__get_latest_fitrs_files(file_type=file_type, eqt=eqt, cfi=cfi)
        
        if isin:
            self.__logger.info(f'Filtering records for the given ISINs')
            if len(mifid_file_list_isin := mifid_file_list[mifid_file_list["Id"].isin(isin)]) > 0:
                mifid_file_list = mifid_file_list_isin
            else:
                self.__logger.warning(f'No record found for the given ISINs, keeping default')

        list_urls = mifid_file_list["download_link"].unique()

        list_dwndl_dfs = []
        self.__logger.info(f'Downloading {len(list_urls)} files')
        
        if save_locally:
            self.__logger.info(f'Saving files locally')
        else:
            self.__logger.info(f'Files will not be saved locally, flag the parameter save_locally=True to save them') 
        
        for url in list_urls:
            self.__logger.info(f'Downloading and parsing {url}')
            list_dwndl_dfs.append(self.__utils.download_and_parse_file(url, save=save_locally, update=update))
            
        self.__logger.info('Process done!')
        return pd.concat(list_dwndl_dfs)


    
    def load_ssr_exempted_shares(self, today: bool = True):

        """
        Retrieves SSR (Short Selling Regulation) exempted shares data from the European Securities and Markets Authority register for all European countries including Norway and Great Britain. Optionally filters the results to include only records relevant to the current date.

        Args:
            today (bool): If True, the function filters the data to show only records where the modification date, start date of exemption, or both are relevant for today's date. Defaults to True.

        Returns:
            pd.DataFrame: A DataFrame containing the SSR exempted shares data, filtered based on the 'today' parameter. This data includes fields such as country code, ISIN, modification dates, and exemption start dates.

        Examples:
            >>> # Retrieve all SSR exempted shares data without any date filtering
            >>> exempted_shares = EsmaDataLoader().load_ssr_exempted_shares(today=False)
            >>> # Retrieve SSR exempted shares data relevant for today's date
            >>> exempted_shares_today = EsmaDataLoader().load_ssr_exempted_shares()
        """

        list_countries = [ "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", 
                           "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", 
                           "NL", "PL", "PT", "RO", "SE", "SI", "SK", "NO", "GB"]
        
        list_dfs = []
        
        self.__logger.info(f'Requesting SSR Exempted Shares')
        with tqdm(total=len(list_countries), position=0, leave=True) as pbar:
            for country in list_countries:
                
                pbar.set_description(f"Processing request for {country}")
                pbar.update(1)
                
                country_query = self.query_url.ssr.format(country=country)
                request = requests.get(country_query)
                if request.status_code == 200:
                    json_request = request.json()["response"]["docs"]
                    df = pd.DataFrame(json_request)
                    list_dfs.append(df)
                else:
                    self.warning(f'Request failed, status code {request.status_code} for country {country}')
        
        delivery_df = pd.concat(list_dfs) 

        if not today: 
            self.__logger.info(f'Process done!')
            return delivery_df

        self.__logger.info(f'Filtering for today\'s date')
        today_date = datetime.today().strftime("%Y-%m-%d")
        
        filtered_data = delivery_df.query('shs_modificationBDate > @today_date and shs_exemptionStartDate <= @today_date')

        duplicates = filtered_data[filtered_data.duplicated(subset='shs_isin', keep=False)]
        duplicates = duplicates[duplicates['shs_modificationDateStr'] <= today_date]
        
        non_duplicates = filtered_data[~filtered_data['shs_isin'].isin(duplicates['shs_isin'])]
        
        final_data = pd.concat([duplicates, non_duplicates]).reset_index(drop=True)
        self.__logger.info(f'Process done!')
        
        return final_data       


    def __get_files_single_df_mifid(self, dataset: str):

        """
        Retrieves a DataFrame of files for a specific MIFID dataset.

        Args:
            dataset (str): The dataset name (e.g., 'fitrs', 'firds', or 'dvcap') to fetch the files for.

        Returns:
            pd.DataFrame: A DataFrame containing the file data for the given dataset.
        """

        if dataset == u.Dataset.FIRDS.value:

            query_mifid = self.query_url.mifid.format(db=dataset, 
                                                  date_column='publication_date', 
                                                  creation_date_from=self.creation_date_from, 
                                                  creation_date_to=self.creation_date_to, 
                                                  limit=self.limit)
        else:
            query_mifid = self.query_url.mifid.format(db=dataset,
                                                date_column='creation_date',
                                                creation_date_from=self.creation_date_from,
                                                creation_date_to=self.creation_date_to,
                                                limit=self.limit)
        
        self.__logger.info(f'Requesting {dataset} files')
        request = requests.get(query_mifid)
        
        if request.status_code == 200:
            self.__logger.info(f'Request successful, parsing response')
            files = self.__utils.parse_request_to_df(request)
        else:
            self.__logger.error(f'Request failed, status code {request.status_code}')
            return pd.DataFrame()

        return files  

        
    def __get_latest_vcap_files(self):

        """
        Retrieves the latest DVCAP (VCAP) files based on the most recent date.

        Returns:
            pd.DataFrame: A DataFrame containing the latest VCAP files.
        """
        
        pattern_extract_vcap = r'(?P<filetype>[A-Za-z]+)_(?P<date>\d{8})'
        
        mifid_file_list = self.__get_files_single_df_mifid(u.Dataset.DVCAP.value)
        file_name_explosion = mifid_file_list.file_name.str.extract(pattern_extract_vcap)
        mifid_file_list = pd.concat([mifid_file_list, file_name_explosion], axis=1)
        max_date = max(mifid_file_list.date)

        return mifid_file_list.loc[lambda x: x.date == max_date]
    
    def __get_latest_fitrs_files(self, file_type: str, cfi: str, eqt: bool):

        """
        Retrieves the latest FITRS files filtered by file type, CFI code, and instrument type (equity or non-equity).

        Args:
            file_type (str): The type of the file (e.g., 'Full').
            cfi (str): The CFI code to filter the files.
            eqt (bool): Determines if the files should be for equity instruments (True) or non-equity instruments (False).

        Returns:
            pd.DataFrame: A DataFrame containing the latest FITRS files filtered by the specified criteria.
        """
        
        pattern_extract_ft =  r'(?P<filetype>[A-Za-z]+)_(?P<date>\d{8})(?:_(?P<cfi>[A-Za-z]+))?_(?P<nfile>\d+of\d+)\.zip'
        
        mifid_file_list = self.__get_files_single_df_mifid(u.Dataset.FITRS.value)
        mifid_file_list = mifid_file_list.loc[lambda x: x.file_type == file_type]
        file_name_explosion = mifid_file_list.file_name.str.extract(pattern_extract_ft)
        mifid_file_list = pd.concat([mifid_file_list, file_name_explosion], axis=1)
        mifid_file_list = mifid_file_list.loc[lambda x: x.cfi == cfi]
        max_date = mifid_file_list.groupby('file_type').agg({'date': 'max'}).date.iloc[0]

        if eqt:
            mifid_file_list = mifid_file_list.loc[lambda x: x.instrument_type == "Equity Instruments"]
        else:
            mifid_file_list = mifid_file_list.loc[lambda x: x.instrument_type == "Non-Equity Instruments"]

        return mifid_file_list.loc[lambda x: x.date == max_date]
     

if __name__ == '__main__':

    dl = EsmaDataLoader()
    dl.load_latest_files(save_locally=True)
   