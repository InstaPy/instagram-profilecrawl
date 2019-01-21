from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from time import sleep
from re import findall
import math

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from util.settings import Settings
from .util import web_adress_navigator
from util.extractor_posts import extract_post_info
import datetime
from util.instalogger import InstaLogger
from util.exceptions import PageNotFound404, NoInstaProfilePageFound


def login(browser, login_username, login_password):
    login_url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    browser.get(login_url)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "HmktE")))
    id_input = browser.find_element_by_xpath("//input[@name='username']")
    id_input.send_keys(login_username)
    pass_input = browser.find_element_by_xpath("//input[@name='password']")
    pass_input.send_keys(login_password)
    pass_input.send_keys(Keys.RETURN)
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mt3GC")))
    except Exception as e:
        if EC.presence_of_element_located((By.CLASS_NAME, "AjK3K ")):
            print("Verification Code required")
        else:
            print(e, "username or password is wrong")
        sys.exit(1)
