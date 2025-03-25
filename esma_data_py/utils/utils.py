import hashlib
import functools
import os
import re
import requests
import tempfile
import zipfile
import warnings
import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
from dataclasses import dataclass
from requests.models import Response
from enum import Enum
import logging


class Utils:

    """
    Utility class providing various helper methods for data processing, file handling, 
    logging, and caching. It includes functions for hashing strings, managing directories,
    logging, parsing XML responses, and caching DataFrames.

    This class is designed to work in symbiosis with EsmaDataLoader and  to simplify common tasks such as working with files, 
    handling data caching, and performing logging for operations related to data retrieval.

    """
    
    @staticmethod
    def _hash(string: str) -> str:
        
        """
        Generate an MD5 hash from a string.

        Args:
            string (str): The input string to hash.

        Returns:
            str: The MD5 hash of the input string.
        
        Example:
            >>> Utils._hash("my_string")
            'e99a18c428cb38d5f260853678922e03'
        """
        
        h = hashlib.new("md5")
        h.update(string.encode("utf-8"))
        return h.hexdigest()

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _warning_cached_data(file: str):
        
        """
        Warn about previously saved data being used and notify that an update can be triggered.

        Args:
            file (str): The file being used from the cache.
        
        Example:
            >>> Utils._warning_cached_data("file_path.csv")
            "Previously saved data used: file_path.csv"
        """
        """Warn about previously saved data being used."""
        
        logger = Utils.set_logger('EsmaDataUtils')
        logger.warning("Previously saved data used:\n{}\nSet update=True to get the most up-to-date data".format(file))

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _create_folder(folder: str = "data"):

        """
        Create a folder in the user's home directory to store data.

        Args:
            folder (str): The name of the folder to create. Default is "data".

        Returns:
            Path: The path to the created folder.

        Example:
            >>> folder_path = Utils._create_folder("my_data")
            >>> print(folder_path)
            "/home/user/esma_data_py/my_data"
        """

        main_folder = Path.home() / "esma_data_py" / folder

        if not main_folder.exists():
            main_folder.mkdir(parents=True)

        return main_folder

    def save_df(obj=pd.DataFrame, print_cached_data=True, folder="data"):

        """
        Decorator to save and retrieve DataFrames to/from cache as pickled files. If a file already exists and `update` is False,
        the cached version will be used.

        Args:
            obj (pd.DataFrame): Default object that will be returned if no new data is fetched.
            print_cached_data (bool): Whether to print a warning when cached data is used. Defaults to True.
            folder (str): The folder where the data is stored. Defaults to "data".

        Returns:
            function: A decorated function that will save and load data as necessary.
        
        Example:
            >>> @Utils.save_df()
            >>> def fetch_data():
            >>>     return pd.DataFrame({'col': [1, 2, 3]})
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger = Utils.set_logger('EsmaDataUtils')
                data_folder = Utils._create_folder(folder=folder)

                non_update_save_args = [str(value) for key, value in kwargs.items() if key not in ["update"]]
                string_file_arg = non_update_save_args + [func.__name__] + [str(arg) for arg in args]

                file_name = os.path.join(data_folder, Utils._hash("".join(string_file_arg)) + ".csv")

                update = kwargs.get("update", False)
                
                if not os.path.exists(file_name) or update:
                    df = func(*args, **kwargs)
                    try:
                        df.to_pickle(file_name)
                        logger.info(f"Data saved: {file_name}")
                    except Exception as e:
                        warnings.warn(f"Error saving file: {file_name}\n{str(e)}")
                        logger.error(f"Error, file not saved: {file_name}\n{df}")
                        logger.error(f"Type of df: {type(df)}")

                    df = obj(df)

                else:
                    try:
                        df = pd.read_pickle(file_name)
                        if "Unnamed: 0" in df.columns:
                            del df["Unnamed: 0"]
                    except Exception as e:
                        warnings.warn(f"Error loading file: {file_name}\n{str(e)}")
                        os.remove(file_name)
                        kwargs["update"] = True
                        logger.error("Unable to load data, function retriggered")
                        df = func(*args, **kwargs)
                        df = obj(df)
                    else:
                        if print_cached_data:
                            Utils._warning_cached_data(file_name)
                        df = obj(df)

                return df
            return wrapper
        return decorator

    @staticmethod
    def extract_file_name_from_url(url: str) -> str:
        
        """
        Extract the file name from a URL.

        Args:
            url (str): The URL from which to extract the file name.

        Returns:
            str: The extracted file name without extension.

        Example:
            >>> Utils.extract_file_name_from_url("http://example.com/file.zip")
            'file'
        """

        file_name_raw = url.split('/')[len(url.split('/')) - 1]
        file_name = file_name_raw.split(".")[0]
        return file_name

    @staticmethod
    def clean_inner_tags(root: ET):
        
        """
        Clean XML inner tags by stripping namespaces and adjusting the tag names.

        Args:
            root (ET): The XML tree to process.
        
        Example:
            >>> Utils.clean_inner_tags(root)  # root is an ElementTree object
        """

        parent_elem = None
        pattern_tag = r"\{[^}]*\}(\S+)"

        for elem in root.iter():
            if (clean_tag := re.search(pattern_tag, elem.tag).group(1)) in ['Amt', 'Nb']:
                elem.tag = '_'.join([parent_elem.tag, clean_tag])
            else:
                elem.tag = clean_tag

            parent_elem = elem

    @staticmethod
    def process_tags(child: ET) -> dict:
        
        """
        Process XML tags and map values into a dictionary.

        Args:
            child (ET): A child XML element to process.

        Returns:
            dict: A dictionary of processed tag-value pairs.

        Example:
            >>> tag_dict = Utils.process_tags(child)  # child is an XML element
        """

        mini_tags = defaultdict(list)
        list_additional_vals = [deque(range(2,101)) for _ in range(15)]
        mini_tags_list_map = defaultdict(int)

        for i in child.iter():
            if str(i.text).strip() != '':
                if i.tag not in mini_tags:
                    mini_tags[i.tag].append(i.text)
                else:
                    if i.tag not in mini_tags_list_map:
                        mini_tags_list_map[i.tag] = len(mini_tags_list_map)

                    key_list_map = mini_tags_list_map[i.tag]
                    key = '_'.join([i.tag, str(list_additional_vals[key_list_map].popleft())])
                    mini_tags[key].append(i.text)

        return mini_tags

    @staticmethod
    def parse_request_to_df(request: Response) -> pd.DataFrame:
        
        """
        Parse an XML response to a DataFrame.

        Args:
            request (Response): The HTTP response containing XML data.

        Returns:
            pd.DataFrame: The parsed DataFrame containing the XML data.

        Example:
            >>> df = Utils.parse_request_to_df(response)
        """

        xml = BeautifulSoup(request.text, 'xml')
        list_of_dicts = []

        for doc in xml.find_all('doc'):
            record_dict = {}

            for element in doc.find_all():
                name = element.get('name')  
                if name:  
                    record_dict[name] = element.text

            list_of_dicts.append(record_dict)

        data = pd.DataFrame.from_records(list_of_dicts)
        
        return data

    @staticmethod
    @save_df()
    def download_and_parse_file(url: str, update: bool = False) -> pd.DataFrame:
        
        """
        Download a file from a URL, extract its contents, and parse it into a DataFrame.

        Args:
            url (str): The URL to download the file from.
            update (bool): Whether to force an update of the cached data. Defaults to False.

        Returns:
            pd.DataFrame: The parsed DataFrame.

        Example:
            >>> df = Utils.download_and_parse_file("http://example.com/file.zip")
        """

        file_name = Utils.extract_file_name_from_url(url)
        r = requests.get(url)

        with tempfile.TemporaryDirectory() as temp_dir:
            dataDir = str(temp_dir) + "/" + file_name

            if not os.path.exists(dataDir):
                os.mkdir(dataDir)

            file_dwn = dataDir + "/" + "file_" + file_name

            with open(file_dwn, mode="wb") as file:
                file.write(r.content)
                with zipfile.ZipFile(file_dwn, "r") as zip_ref:
                    zip_ref.extractall(dataDir)

            file_xml = [dataDir + "/" + f for f in os.listdir(dataDir) if ".xml" in f][0]

            root = ET.parse(file_xml).getroot()

        Utils.clean_inner_tags(root)

        root_list = list(root.iter('NonEqtyTrnsprncyData'))
        if not root_list:
            root_list = list(root.iter('EqtyTrnsprncyData'))
        if not root_list:
            root_list = list(root.iter('VolCapRslt'))

        list_dicts = []
        for child in tqdm(root_list, desc='Parsing file ... ', position=0, leave=True):
            list_dicts.append(Utils.process_tags(child))

        df = pd.DataFrame.from_records(list_dicts)
        delivery_df = df.applymap(lambda x: x[0] if isinstance(x, list) else x)
        return delivery_df
    
    @staticmethod
    def set_logger(name: str):

        """
        Set up a logger for the specified name.

        Args:
            name (str): The name of the logger.

        Returns:
            logging.Logger: The configured logger.

        Example:
            >>> logger = Utils.set_logger("my_logger")
            >>> logger.info("This is an info log.")
        """
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.propagate = False

        return logger


class Dataset(Enum):
    FITRS = 'fitrs'
    FIRDS = 'firds'
    DVCAP = 'dvcap'


class Cfi(Enum):
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    H = 'H'
    I = 'I'
    J = 'J'
    O = 'O'
    R = 'R'
    S = 'S'


@dataclass
class QueryUrl:

    ssr: str = ('https://registers.esma.europa.eu/solr/esma_registers_mifid_shsexs/select?'
                'q=({{!parent%20which=%27type_s:parent%27}})&wt=json&indent=true&rows=150000&fq=(shs_countryCode:{country})')
    mifid: str = ('https://registers.esma.europa.eu/solr/esma_registers_{db}_files/select?q=*'
                  '&fq={date_column}:%5B{creation_date_from}T00:00:00Z+TO+{creation_date_to}T23:59:59Z%5D&wt=xml&indent=true&start=0&rows={limit}')
    fca_firds: str =  ('https://api.data.fca.org.uk/fca_data_firds_files?q=((file_type:FULINS)'
                       '%20AND%20(publication_date:[{creation_date_from}%20TO%20{creation_date_to}]))&from=0&size={limit}')
