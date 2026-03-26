import sys
import os
import logging
import gc
from optparse import OptionParser

import django

# Set up the path to include the parent directory for importing common modules
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
# print(project_root)
sys.path.insert(0, project_root )
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api_market.models import Company, Information
from api_market.collectors.common.settings import setup_logger
from api_market.collectors.minkabu.scraper import CompanyData, FetchDataFromMinkabu

# Set up logger
logger = setup_logger(name=__name__)
logger.debug('Path added to sys.path: {}'.format(project_root))


def numeric_or_none(val):
    """
    int or float are OK. other is None
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def scraping(_start: int = 1, _end: int = 10):
    company_code_list = []
    company_list = Company.fetch_code_and_name()
    company_list = sorted(company_list, key=lambda x: x["dividend_rank"])
    logger.info({'max number of companies': len(company_list)})
    for company in company_list[_start:_end]:
        logger.debug({'code': company['code']})
        company_code_list.append(company['code'])

    for index, company_code in enumerate(company_code_list):
        logger.info({"index": index, "code": company_code})
        datasets = CompanyData()
        _scraping = FetchDataFromMinkabu(datasets, company_code)
        _scraping.fetch_soup_main(delay=3)
        _scraping.fetch_select_item()
        for company in datasets.companies:
            logging.debug(company)
            c_code = company['code']
            c_industry = company['industry']
            c_description = company['description']
            c_per = numeric_or_none(company['per'])
            c_psr = numeric_or_none(company['psr'])
            c_pbr = numeric_or_none(company['pbr'])
            db_info = Information.get_or_create_and_update(
                c_code, c_industry, c_description, c_per, c_psr, c_pbr)

            logger.info({
                # "code": db_info.company_code,
                "code": db_info.company.code,
                "industry": db_info.industry,
                "PER": db_info.per,
                "PSR": db_info.psr,
                "PBR": db_info.pbr,
                "updated_at": db_info.updated_at,
            })


def main():
    usage = 'usage: %prog -s <start index> -e <end index>'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--start', action='store', type='int', dest='start', help='start index')
    parser.add_option('-e', '--end', action='store', type='int', dest='end', help='end index')
    options, args = parser.parse_args()

    if options.start is None or options.end is None:
        raise Exception("start and end index are required.")

    start_index = int(options.start)
    end_index = int(options.end)
    logger.info({
        'start': start_index,
        'end': end_index,
    })

    scraping(start_index, end_index)


if __name__ == '__main__':
    # max index : 3372
    # python manage.py import_minkabu -s 0 -e 10
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    gc.collect()

