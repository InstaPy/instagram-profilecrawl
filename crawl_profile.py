#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json

from selenium import webdriver

from util.cli_helper import get_all_user_names
from util.extractor import extract_information

browser = webdriver.Chrome('./assets/chromedriver')
#will be patient with slower page load times
browser.implicitly_wait(25)

try:
  usernames = get_all_user_names()

  for username in usernames:
    print('Extracting information from ' + username)
    information = extract_information(browser, username)

    with open('./profiles/' + username + '.json', 'w') as fp:
      json.dump(information, fp)

except KeyboardInterrupt:
  print('Aborted...')

finally:
  browser.delete_all_cookies()
  browser.close()
