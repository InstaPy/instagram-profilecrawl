"""Goes through all usernames and collects their information"""
import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from util.extractor import extract_information

chrome_options = Options()
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--lang=en-US')
#chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
browser = webdriver.Chrome('./assets/chromedriver', chrome_options=chrome_options)

# makes sure slower connections work as well
browser.implicitly_wait(25)

def get_all_user_names():
  """Returns all the usernames given as parameter"""

  #display provide username
  if len(sys.argv) < 2:
    sys.exit('- Please provide at least one username!\n')

  return [username for username in sys.argv[1:]]

try:
  usernames = get_all_user_names()

  for username in usernames:
    print('Extracting information from {username}...'.format(username=username))
    information = extract_information(browser, username)

    with open('./profiles/{username}.json'.format(username=username), 'w+') as fp:
      json.dump(information, fp, indent=4)

except KeyboardInterrupt:
  print('Aborted...')

finally:
  browser.delete_all_cookies()
  browser.close()