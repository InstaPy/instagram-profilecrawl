#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json

from selenium import webdriver

from util.cli_helper import get_all_user_names
from util.extractor import extract_information

usernames = get_all_user_names()
browser = webdriver.Chrome('./assets/chromedriver')

#will be patient with slower page load times
browser.implicitly_wait(10)

for username in usernames:
  print('Extracting information from ' + username)
  information = extract_information(browser, username)

  with open('./profiles/' + username + '.json', 'w') as fp:
    json.dump(information, fp)

browser.delete_all_cookies()
browser.close()
