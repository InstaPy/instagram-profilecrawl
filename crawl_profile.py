#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json
from .settings import Settings

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
browser.implicitly_wait(10)

try:
  usernames = get_all_user_names()

  for username in usernames:
    print('Extracting information from ' + username)
    information, user_commented_list = extract_information(browser, username, Settings.limit_amount)

    with open(Settings.profile_location + '/' + username + '.json', 'w') as fp:
      fp.write(json.dumps(information, indent=4))
                                                     
    print ("Number of users who commented on his/her profile is ", len(user_commented_list),"\n")
    file = open(Settings.profile_commentors_location + '/' + username + "_commenters.txt","w") 
    for line in user_commented_list:
      file.write(line)
      file.write("\n")
    file.close()     
    print ("\nFinished. The json file and nicknames of users who commented were saved in profiles directory.\n")

except KeyboardInterrupt:
  print('Aborted...')

finally:
  browser.delete_all_cookies()
  browser.close()
