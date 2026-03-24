import sys
import os
import gc
import math
import json

# Set up the path to include the parent directory for importing common modules
my_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(my_path)

from api_market.collectors.common.settings import setup_logger
from api_market.collectors.common.base_scraper import IDataSet, IFetchDataFromUrl

# Set up logger
logger = setup_logger(name=__name__)
logger.info('Path added to sys.path: {}'.format(my_path))


class CompanyData(IDataSet):
    def __init__(self):
        self.companies = []


class FetchDataFromYahooFinance(IFetchDataFromUrl):
    def __init__(self, page_index, dataset: CompanyData, delay_time: int = 5) -> None:
        super().__init__()
        self.base_url = 'https://finance.yahoo.co.jp'
        self.url = self.base_url + '/stocks/ranking/dividendYield?market=all&term=daily&page={}'.format(page_index)
        self.dataset = dataset
        self.delay_time = delay_time
        self.update_date = ''

    def fetch_soup_main(self, delay: int = 5) -> None:
        self._soup_main = self._fetch_soup(self.url, delay=self.delay_time, method='requests')
        # print(self._soup_main)

    def fetch_max_page_index(self):
        url = self.url.format(1)
        soup = self._fetch_soup(url, delay=self.delay_time, method='requests')
        loop_index, update = None, None
        if soup:
            page_index_area = soup.find('div', id='pagertop').find_all('p')
            for i, p_tag in enumerate(page_index_area):
                if i == 0:
                    temp = p_tag.text.strip('件中')
                    temp = temp.split(' ')
                    max_page_index = int(temp[2])
                    loop_index = math.ceil(max_page_index / 50)
                else:
                    update = p_tag.text
        return loop_index, update

    def fetch_select_item(self):
        """
        ver 2025.08.09 val table mame
        """
        _table_class_name = 'table.RankingTable__table__zvh5'
        _tr_class_name = 'tr.RankingTable__row__1Gwp'
        _th_class_name = 'th.RankingTable__head__2mLL.RankingTable__rank__2fAZ'
        _td_class_name = 'td.RankingTable__detail__P452'
        _li_code_class_name = 'li.RankingTable__supplement__vv_m'
        _td_stock = 'td.RankingTable__detail__P452.RankingTable__detail--value__i9gr'
        _span_stock = 'span.StyledNumber__value__3rXW'
        _td_dividend = 'td.RankingTable__detail__P452.RankingTable__detail--value__i9gr'
        _td_dividend = _td_dividend + '.RankingTable__detail--highlight__2Iu2'
        _span_dividend = 'span.StyledNumber__value__3rXW'

        data_tables = self._soup_main.select_one(_table_class_name).find('tbody')
        rows_table = data_tables.select(_tr_class_name)
        for index, row in enumerate(rows_table):
            rank = row.select_one(_th_class_name).text
            name = row.select_one(_td_class_name).find('a').text
            code = row.select_one(_li_code_class_name).text
            stock = row.select_one(_td_stock).select_one(_span_stock).text
            dividend = row.select_one(_td_dividend).select_one(_span_dividend).text.strip('+')
            # dividend = row.select_one(_td_dividend)
            # print(index, rank, code, name, stock, dividend)

            d = {
                'company_code': code,
                'company_name': name,
                'company_stock': stock,
                'company_dividend': dividend,
                'company_rank': rank,
                'company_rank_date': self.update_date
            }
            self.dataset.companies.append(d)


def main():

    company_list = CompanyData()

    fetch_yahoo_finance = FetchDataFromYahooFinance(1, company_list)
    max_index, update_date = fetch_yahoo_finance.fetch_max_page_index()
    logger.info({"max_index":max_index, "update_date": update_date})

    # idx = max_index
    idx = 1
    fetch_yahoo_finance = FetchDataFromYahooFinance(idx, company_list, delay_time=5)
    fetch_yahoo_finance.update_date = update_date
    fetch_yahoo_finance.fetch_soup_main()
    # print(fetch_yahoo_finance._soup_main)

    logger.info('start fetch_select_item')
    fetch_yahoo_finance.fetch_select_item()
    #
    logger.info(json.dumps(company_list.companies, indent=2, ensure_ascii=False))

    gc.collect()


if __name__ == '__main__':
    main()
