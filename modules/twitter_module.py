

#//img[@alt='Image']
#user webdriver or scrappy to parse this shit

import subprocess
import logging
import json
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def download_tweet(url, logger) -> (str, str, str):
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    driver.get('https://www.reddit.com/r/2visegrad4you/comments/130f10t/this_is_what_the_west_did_to_us/')

    # Get the Network Logs
    network_logs = driver.execute_script("return window.performance.getEntries()")

    for log in network_logs:
         print('URL:', log['name'])
         print('Headers:', log['requestHeaders'])
         print('\n')

    driver.quit()

        

if __name__ == "__main__":
    download_tweet(url="", logger=logger)