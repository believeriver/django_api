import os
import sys
from time import sleep
import gc
from typing import Optional
from selenium.webdriver.common.by import By
import json

# Set up the path to include the parent directory for importing common modules
my_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(my_path)

from api_market.collectors.common.settings import setup_logger
from api_market.collectors.common.base_scraper import IDataSet, IFetchDataFromUrl, ISaveToFile

# Set up logger
logger = setup_logger(name=__name__)
logger.info('Path added to sys.path: {}'.format(my_path))


class CompanyData(IDataSet):
    def __init__(self):
        self.companies = []


class FetchDataFromIRBank(IFetchDataFromUrl):
    def __init__(self, dataset: CompanyData, company_code: int) -> None:
        super().__init__()
        self.base_url = f"https://irbank.net/{company_code}/results"
        self.url = self.base_url
        self.company_code = company_code
        self.dataset = dataset
        self.delay_time = 3
        self._header = None
        self._td_obb = None
        self._td_odd = None

    def _fetch_test_by_selenium(self, company_code) -> Optional[str]:
        """ This is not used. 2025.12.19"""
        driver = self._fetch_driver_by_selenium(self.url, self.delay_time, True, False)
        sleep(1)

        try:
            # 1. まずページ全体のリンクを全出力して確認
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print("=== 全 a タグ（最初の20個） ===")
            for i, link in enumerate(all_links[:20]):
                href = link.get_attribute("href") or ""
                title = link.get_attribute("title") or ""
                text = link.text.strip()[:30]
                print(f"{i}: {text} | title='{title}' | href={href}")

            # 2. 「決算」「results」「kessan」関連のリンクを探す
            print("\n=== 決算関連リンク検索 ===")
            for link in all_links:
                text = link.text.lower()
                href = link.get_attribute("href") or ""
                if any(word in text for word in ["決算", "results", "kessan"]):
                    print(f"FOUND: text='{link.text}' href='{href}'")

            # 3. より緩いセレクタで試す
            selectors_to_try = [
                "a[href*='results']",  # /results を含む
                "a[href*='/E']",  # /E00492/results の /E
                ".nsq a",  # nsq クラスのナビ
                "nav a",  # ナビゲーション
                "ul li a",  # リスト内のリンク
            ]

            for selector in selectors_to_try:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"\n{selector}: {len(elements)} 個見つかりました")
                    for elem in elements[:5]:  # 最初の5個
                        print(f"  - {elem.text} -> {elem.get_attribute('href')}")
                except Exception as e:
                    print(f"{selector}: エラー {e}")

            # 4. 手動で決算っぽいURLを特定（2914の場合は /E00492/results）
            # 実際のページでは決算リンクが見つからない場合があるので、
            # 会社コードから推測するか固定パターンで対応
            detail_url = f"https://irbank.net/{company_code}/results"  # とりあえずこれで
            print(f"推測URL: {detail_url}")
            return detail_url

        finally:
            driver.quit()

    # def fetch_main_soup(self, delay: int = 10) -> None:
    def fetch_soup_main(self, delay: int = 3) -> None:
        """2025.12.19"""
        try:
            self._soup_main = self._fetch_soup(
                self.base_url, delay=delay, method='selenium')
            if self._soup_main:
                print(f"DEBUG: title = {self._soup_main.title}")
        except Exception as e:
            print(f'[ERROR]: {e}')

    @staticmethod
    def convert_units(value: str):
        if value == '-':
            return 0

        value = value.strip('*')
        value = value.strip('%')
        value = value.strip('円')

        convert = value.maketrans(
            {'兆': '*1000000000000,',
             '億': '*100000000,',
             '万': '*10000,',
             '百': '*100,',
             '円': ''})
        sale_formula = value.translate(convert)
        # print(sale_formula)
        values = sale_formula.split(',')

        result = 0
        for val in values:
            if val != "":
                result += eval(val)

        return result

    def test_to_csv(self, company_code, item_name):
        filename = 'lib/temp/' + str(company_code) + '_' + item_name + '.csv'
        company_data = None

        for data in self.dataset.companies:
            # print(data['company_code'], company_code)
            if int(data['company_code']) == company_code:
                company_data = data['trend_data']

        if company_data:
            with open(filename, mode='w') as fp:
                fp.write(str(company_code) + ',' + item_name + '\n')
                for data in company_data:
                    fp.write(str(data[0]) + ',' + str(data[1]) + '\n')
            print('create csv')
        else:
            print('no data')

    def fetch_table_data(self, table_name: str):
        # company_name_item = self._soup_main.find('div', id='container').select_one('main > div > h1 > a')
        company_name_item = self._soup_main.find('div', id='container').select_one('main > div > p > a')
        print(company_name_item)
        company_code = company_name_item.text.split(' ')[0]
        company_name = company_name_item.text.split(' ')[1]
        # print(company_code, company_name)

        test_soup = self._soup_main.find_all('div', class_='mgr inline')
        result = {}

        data = []
        for idx, item in enumerate(test_soup):
            tb_titles = item.select_one("h2")
            # print(idx, tb_titles.text)
            item_title = tb_titles.text.split('#')[0]
            # print(item_title)
            if table_name == "売上高":
                table_name_list = [table_name, "収益"]
            else:
                table_name_list = [table_name]
            #  item_title == table_name:
            if item_title in table_name_list:
                # print(tb_titles.text)
                item_year = item.select("dt")
                item_dd = item.select("dd")
                item_datasets = []
                for dd in item_dd:
                    temp = dd.select_one("span.text")
                    if temp is not None:
                        item_datasets.append(temp)
                    else:
                        item_datasets.append(dd)

                for i, y in enumerate(item_year):
                    # print(i, y.text, self.convert_units(item_datasets[i].text))
                    data.append([y.text.split('\u2009')[0], self.convert_units(item_datasets[i].text)])

        result = {
            'company_code': company_code,
            'company_name': company_name,
            'item_name': table_name,
            'trend_data': data
        }
        self.dataset.companies.append(result)

    def check_fetch_table_data(self, table_name: str):
        # company code : 9110 NSユナイテッド海運
        d_items = {
            "売上高": 'c_1',
            "営業利益率": 'c_33',
            "EPS": 'c_6',
            "自己資本比率": 'c_12',
            "営業活動によるCF": 'c_17',
            "現金等": 'c_22',
            "一株配当": 'c_24',
            "配当性向": 'c_25'
        }
        print(d_items["売上高"])
        # check
        table_soup = self._soup_main.find('div', id=d_items[table_name])
        # search table title
        tb_title = table_soup.select_one("h2")
        # print(tb_title.text)
        dt_year = table_soup.select("dt")
        dt_datasets = table_soup.select("span.text")
        # year
        for i, dt in enumerate(dt_year):
            print(i, dt.text, self.convert_units(dt_datasets[i].text))


class SaveToCsvFile(ISaveToFile):
    def __init__(self, filename: str, dataset: CompanyData):
        super().__init__(filename, dataset)


if __name__ == '__main__':
    """
    Test the program.
    """
    db_name = 'IRBank.db'
    tb_name = 'companies'
    file_name = 'IRBank.csv'

    data_items = [
        "売上高",
        "営業利益率",
        "EPS",
        "自己資本比率",
        "営業活動によるCF",
        "現金等",
        "一株配当",
        "配当性向"]

    # scraping
    company_list = CompanyData()

    # select item
    item = data_items[0]

    fetch_IR_bank = FetchDataFromIRBank(company_list, 2914)
    fetch_IR_bank.fetch_soup_main(delay=1)
    fetch_IR_bank.fetch_table_data(item)

    print(company_list.companies)

    # fetch_IR_bank.test_to_csv(9986, item)
    # fetch_IR_bank.test_to_csv(9110, item)

    gc.collect()

