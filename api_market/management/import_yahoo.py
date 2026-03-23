import gc
import sys
import os
from optparse import OptionParser

import django

# Set up the path to include the parent directory for importing common modules
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
# print(project_root)
sys.path.insert(0, project_root )
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api_market.models import Company
from api_market.collectors.common.settings import setup_logger
from api_market.collectors.yahoo_finance.scraper import CompanyData, FetchDataFromYahooFinance

# Set up logger
logger = setup_logger(name=__name__)
logger.info('Path added to sys.path: {}'.format(project_root))



def fetch_index_date(c_list: CompanyData):
    fetch_yahoo = FetchDataFromYahooFinance(1, c_list)
    max_idx, update_day = fetch_yahoo.fetch_max_page_index()
    update_day = update_day.split('(')[1]
    update_day = update_day.strip(')')
    # print(max_index, update_date)
    return max_idx, update_day


def scraping(debug_flg: bool = True):
    company_list = CompanyData()
    start_index = 1
    max_index, update_date = fetch_index_date(company_list)
    print(max_index, update_date)

    if debug_flg:
        print('[DEBUG] debug mode start.')
        max_index = 1

    for i in range(start_index, max_index+1):
        print('page=', i)
        fetch_yahoo_finance = FetchDataFromYahooFinance(i, company_list, delay_time=3)
        fetch_yahoo_finance.update_date = update_date
        fetch_yahoo_finance.fetch_soup_main()
        fetch_yahoo_finance.fetch_select_item()

        # print(company_list.companies)
        # write DB
        for company in company_list.companies:
            c_code = company['company_code']
            c_name = company['company_name']
            c_stock = company['company_stock']
            c_dividend = company['company_dividend']
            c_rank = company['company_rank']
            c_date = company['company_rank_date']
            company = Company.get_or_create_and_update(
                c_code, c_name, c_stock, float(c_dividend), int(c_rank), str(c_date))

            if debug_flg:
                print(c_rank, c_code, c_name, c_dividend)
                print(
                    company.dividend_rank,
                    company.code,
                    company.name,
                    company.dividend,
                    company.dividend_update)
    gc.collect()


def main():
    usage = 'usage: %prog -d/--debug'
    parser = OptionParser(usage=usage)
    parser.add_option(
        '-d', '--debug',
        action='store_true',
        dest='debug',
        default=False,
        help='debug flag True-> -d')
    options, args = parser.parse_args()

    debug = options.debug
    logger.info({
        'start': debug,
    })

    if debug is None:
        raise Exception("start and end index are required.")

    scraping(debug)


if __name__ == '__main__':
    main()
    # main(False)
