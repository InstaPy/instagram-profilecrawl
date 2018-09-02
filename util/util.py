from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import csv
import json
import datetime
import os
import re
import random
import sqlite3
import time
import signal
from .settings import Settings
from .time_util import sleep
from .time_util import sleep_actual
import errno
from util.instalogger import InstaLogger


def web_adress_navigator(browser, link):
    """Checks and compares current URL of web page and the URL to be navigated and if it is different, it does navigate"""

    try:
        current_url = browser.current_url
    except WebDriverException:
        try:
            current_url = browser.execute_script("return window.location.href")
        except NoSuchElementException:
            InstaLogger.logger().error("Failed to get page")
            total_posts = None
        except WebDriverException:
            current_url = None

    if current_url is None or current_url != link:
        browser.get(link)
        # update server calls
        sleep(2)

def check_folder(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return True