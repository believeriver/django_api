import os
import sys

path_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path_dir)

USER_AGENT = '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0'

LOG_FILE = path_dir + '/scraping.log'
