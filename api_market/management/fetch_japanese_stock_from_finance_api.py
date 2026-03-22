import logging
import sys
import gc
import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
# import yfinance as yf
import datetime

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False
logger.addHandler(handler)


class JapanStockModel(object):
    def __init__(self, _ticker_symbol, _start, _end=str(datetime.date.today())):
        self.train = None
        self.ticker_symbol = _ticker_symbol
        self.start = _start
        self.end = _end
        self._duration = 30

    @staticmethod
    def fetch_japan_stock_by_pdr_stooq(
            _ticker_symbol: int, _start: str, _end: str) -> pd.DataFrame:
        """
        2025.05 ~ yfinace cannot response our request.
                          then, change to pandas_datareader by stooq
        """
        ticker_symbol_dr = str(_ticker_symbol) + ".JP"
        try:
            df = pdr.DataReader(ticker_symbol_dr, "stooq", start=_start, end=_end)
            logger.debug(df)
            return df
        except Exception as e:
            logger.debug(f"Failed to download {ticker_symbol_dr}: {e}")
            return pd.DataFrame()

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    def import_data(self):
        # self.train, self.test, self.sample = self._import_csv()
        self.train = self.fetch_japan_stock_by_pdr_stooq(
            self.ticker_symbol, self.start, self.end)

    def plot_stock(self):
        self.train['Close'].plot(figsize=(12, 6), color='green')
        plt.show()


def fetch_stock_dataframe(
        company_code, start='2010-01-01', end=str(datetime.date.today()), span=30):
    if company_code is None:
        return None

    dataset = JapanStockModel(company_code, start, end)
    dataset.duration = span
    dataset.import_data()
    d_year = dataset.train.index
    data = np.array(dataset.train['Close'])
    d = {'year': d_year,
         'value': data}
    df = pd.DataFrame(d)
    del dataset

    return df


def main_no_prediction():
    """
    Test this clas.

    fetch GMO stock and plot graph.
    """
    ticker_symbols = {'GMO': 7177,
                      'JapanCeramic': 6929,
                      'MHI': 7011,
                      'Zaoh': 9986,
                      'mirai': 7931}
    start = '2000-01-01'
    end = str(datetime.date.today())
    span = 365

    machin_learning = JapanStockModel(ticker_symbols['GMO'], start, end)
    # machin_learning = JapanStockModel(7203, '2023-01-01', '2023-12-01')
    machin_learning.duration = span
    machin_learning.import_data()
    machin_learning.plot_stock()


def main():
    ticker = 7203  # Toyota
    start = '1990-01-01'
    end = str(datetime.date.today())
    span = 365
    data = fetch_stock_dataframe(ticker, start, end, span)
    logger.info(data)


if __name__ == '__main__':
    # main_no_prediction()
    main()

    gc.collect()
    logger.info({'action': 'garbage collection', 'gc': gc.get_stats()[2]})