import os
import sys

# Set up Path for settings and logger
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(my_path)

# set up warnings
from bootstrap import setup_warnings
setup_warnings()

# Set up logger
import settings
from settings import setup_logger
logger = setup_logger(name=__name__)

from time import sleep
from typing import List, Optional
from abc import ABC, abstractmethod
import requests
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class IDataSet(ABC):
    @abstractmethod
    def __init__(self):
        pass


class IFetchDataFromUrl(ABC):
    def __init__(self):
        self.base_url = None
        self.url = None
        self._soup_main = None

    @staticmethod
    def _fetch_content_by_request(url: str, delay: int) -> bytes:
        # logger.info('delay time : ', delay, 'sec', 'request')
        logger.info(f'[scraping by request]delay time : {delay} sec')
        sleep(delay)
        r = requests.get(url)
        r.raise_for_status()

        return r.content

    @staticmethod
    def _fetch_driver_by_selenium(
            url: str, delay: int, is_head: bool = True, is_agent: bool = False) -> webdriver:
        logger.info(f'[scraping by request]delay time : {delay} sec')
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        if is_head:
            options.add_argument('--headless')

        if is_agent:
            options.add_argument(settings.USER_AGENT)

        # driver = webdriver.Chrome(options=options)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

        driver.implicitly_wait(5)

        driver.get(url)
        sleep(delay)
        return driver

    def _fetch_soup(
            self, url: str, delay: int = 10, method: str = 'requests') -> Optional[BeautifulSoup]:
        """ default delay time for request is 10 sec"""
        content = None
        if method == 'requests':
            content = self._fetch_content_by_request(url, delay)
        elif method == 'selenium':
            driver = self._fetch_driver_by_selenium(url, delay)
            content = driver.page_source
        else:
            logger.info('Please set method: "requests" or "selenium"')

        if content is not None:
            soup = BeautifulSoup(content, 'lxml')
            return soup
        else:
            return None

    def fetch_soup_main(self, delay: int = 10) -> None:
        self._soup_main = self._fetch_soup(self.url, delay=delay)

    def fetch_find_item(self):
        pass

    def fetch_select_item(self):
        pass


class ISaveToFile(ABC):
    def __init__(self, filename: str, dataset: List[dict]):
        self.filename = filename
        self.dataset = dataset

    def write_to_csvfile(self):
        df = pd.DataFrame(self.dataset)
        df.to_csv(self.filename, index=False, encoding='utf-8-sig')

    def write_to_file(self):
        pass


