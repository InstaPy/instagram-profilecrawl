import csv
import errno
import json
import datetime
import os
import re
import random
import signal
import time

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .settings import Settings
from .time_util import sleep
from .time_util import sleep_actual
from .exceptions import PageNotFound404
from .instalogger import InstaLogger


def web_adress_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be navigated and if it is different, it does navigate"""

    try:
        current_url = browser.current_url
    except WebDriverException:
        try:
            current_url = browser.execute_script("return window.location.href")
        except WebDriverException:
            current_url = None

    if current_url is None or current_url != link:
        response = browser.get(link)

        if check_page_title_notfound(browser):
            InstaLogger.logger().error("Failed to get page " + link)
            raise PageNotFound404("Failed to get page " + link)
        # if response.status_code == 404:
        #    InstaLogger.logger().error("Failed to get page " + link)
        #   raise PageNotFound404()
        # update server calls

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "viewport")))


def check_page_title_notfound(browser):
    """ little bit hacky but selenium doesn't shown if 404 is send"""
    """ more infos https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/141 """

    title = browser.title
    return title.lower().startswith('page not found')


def check_folder(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return True
