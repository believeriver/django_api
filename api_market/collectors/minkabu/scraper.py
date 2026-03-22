import os
import sys
import gc
import json

# Set up the path to include the parent directory for importing common modules
my_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
sys.path.append(my_path)

from common.settings import setup_logger
from common.base_scraper import IDataSet, IFetchDataFromUrl

# Set up logger
logger = setup_logger(name=__name__)
logger.info('Path added to sys.path: {}'.format(my_path))

"""
Fetch the industry information for minkabu
Export result to test.csv.

Created by Tagawa.
email:
ver: 1.0
date: 2025.08.10
"""


class CompanyData(IDataSet):
    def __init__(self):
        self.companies = []


class FetchDataFromMinkabu(IFetchDataFromUrl):
    def __init__(self, dataset: CompanyData, company_code: str) -> None:
        super().__init__()
        self.base_url = 'https://minkabu.jp'
        self.url = self.base_url + '/stock/{}'.format(company_code)
        self.company_code = company_code
        self.dataset = dataset
        self._header = None
        self._td_obb = None
        self._td_odd = None

    @staticmethod
    def _check_value(value: str) -> float:
        if "倍" in value:
            return float(value.replace("倍", ""))
        else:
            return 0

    def fetch_select_item(self):
        # self.fetch_soup_main(delay=3)
        _industry_info_id = "contents"
        industry_info = self._soup_main.find(id=_industry_info_id)
        # industry info
        _industry_type_css = "div.ly_content_wrapper.size_ss"
        _industry_company_info_css = "div.ly_content_wrapper.size_ss"
        industry = industry_info.select_one(_industry_type_css).find('a').text
        company_info = industry_info.select(_industry_company_info_css)[1].text
        company_info = company_info.strip().replace(' ', '').replace('\t', '')
        # company info
        _table_css_step1 = "div.ly_col.ly_colsize_6_fix"
        _table_css_step2 = "tr.ly_vamd"
        _table_css_step3 = "td.ly_vamd_inner.ly_colsize_9_fix.fwb.tar.wsnw"
        tb_step1 = industry_info.select(_table_css_step1)[1]
        tb_step2 = tb_step1.select(_table_css_step2)
        per = self._check_value(tb_step2[1].select_one(_table_css_step3).text)
        psr = self._check_value(tb_step2[2].select_one(_table_css_step3).text)
        pbr = self._check_value(tb_step2[3].select_one(_table_css_step3).text)
        d = {
            'code': self.company_code,
            'industry': industry,
            'description': company_info,
            'per': per,
            'psr': psr,
            'pbr': pbr,
        }
        self.dataset.companies.append(d)


def main():
    datasets = CompanyData()
    scraping = FetchDataFromMinkabu(datasets, str(9219))
    scraping.fetch_soup_main(delay=3)
    scraping.fetch_select_item()
    for data in datasets.companies:
        print(data)

    gc.collect()


if __name__ == "__main__":
    main()
