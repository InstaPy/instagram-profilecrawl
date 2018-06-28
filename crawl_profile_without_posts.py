#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json
import datetime
from util.settings import Settings
from util.datasaver import Datasaver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from util.cli_helper import get_all_user_names
from util.extractor import extract_information

chrome_options = Options()
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--lang=en-US')
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
browser = webdriver.Chrome('./assets/chromedriver', chrome_options=chrome_options)

# makes sure slower connections work as well        
print ("Waiting 10 sec")
browser.implicitly_wait(5)

Settings.limit_amount = 1
Settings.scrap_posts_infos = False
try:
  usernames = get_all_user_names()

  for username in usernames:
    print('Extracting information from ' + username)
    information, user_commented_list = extract_information(browser, username, Settings.limit_amount)
    Datasaver.save_profile_json(username,information)

except KeyboardInterrupt:
  print('Aborted...')

finally:
  browser.delete_all_cookies()
  browser.close()
