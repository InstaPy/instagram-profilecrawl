#!/usr/bin/env python3.5
"""Goes through all usernames and collects their information"""
import sys
from util.settings import Settings
from util.datasaver import Datasaver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as Firefox_Options

from util.cli_helper import get_all_user_names
from util.extractor import extract_followers
from util.account import login
from util.chromedriver import init_chromedriver


chrome_options = Options()
chromeOptions = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096}
chromeOptions.add_experimental_option("prefs", prefs)
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--lang=en-US')
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})

capabilities = DesiredCapabilities.CHROME


try:
    browser = init_chromedriver(chrome_options, capabilities)
except Exception as exc:
    print(exc)
    sys.exit()


try:
    usernames = get_all_user_names()

    for username in usernames:
        print('Extracting information from ' + username)
        try:
            if len(Settings.login_username) != 0:
                login(browser, Settings.login_username, Settings.login_password)
            extract_followers(browser, username, Settings.limit_amount)
        except:
            print("Error with user " + username)
            sys.exit(1)

finally:
    browser.delete_all_cookies()
    browser.close()
