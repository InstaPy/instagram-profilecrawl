import math
import datetime
import pickle
from re import findall
import sys
from time import sleep

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .util import web_adress_navigator
from util.exceptions import PageNotFound404, NoInstaProfilePageFound
from util.instalogger import InstaLogger
from util.settings import Settings


def check_cookie(cookie):
    if isinstance(cookie.get('expiry'), float):
        cookie['expiry'] = int(cookie['expiry'])

    return cookie


def login(browser, login_username, login_password):
    login_url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    browser.get(login_url)
    try: 
        with open(f"./cookies/cookies-{login_username}.pkl", "rb") as cookie_jar:
            cookies = pickle.load(cookie_jar)
            for cookie in cookies:
                cookie = check_cookie(cookie)
                browser.add_cookie(cookie)

            print('using cookies')
    except:
        login_url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
        browser.get(login_url)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "HmktE")))
        id_input = browser.find_element_by_xpath("//input[@name='username']")
        id_input.send_keys(login_username)
        pass_input = browser.find_element_by_xpath("//input[@name='password']")
        pass_input.send_keys(login_password)
        pass_input.send_keys(Keys.RETURN)

        security_code = explicit_wait(
            browser, "VOEL", ["AjK3K ", "Class"], 4, False)

        if security_code:
            print('Verification Code required')
            send_security_code(browser)

        dismiss_notification_offer(browser)

    from time import sleep; sleep(5)
    from datetime import datetime; browser.save_screenshot(f'/tmp/screenshots/login-{datetime.now()}.png')

    try: 
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "XrOey")))
    except:
        print('login failed')
        return

    with open(f"./cookies/cookies-{login_username}.pkl", "wb") as cookie_jar:
        cookies = browser.get_cookies()
        for cookie in cookies:
            cookie = check_cookie(cookie)
        pickle.dump(cookies, cookie_jar)

    print('logged in')


def send_security_code(browser):
    # credits InstaPy
    send_security_code_button = browser.find_element_by_xpath(
        "//button[text()='Send Security Code']")

    (ActionChains(browser)
     .move_to_element(send_security_code_button)
     .click()
     .perform())

    print('A security code was sent to you')
    security_code = input('Type the security code here: ')

    security_code_field = browser.find_element_by_xpath((
        "//input[@id='security_code']"))

    (ActionChains(browser)
     .move_to_element(security_code_field)
     .click()
     .send_keys(security_code)
     .perform())

    submit_security_code_button = browser.find_element_by_xpath(
        "//button[text()='Submit']")

    (ActionChains(browser)
     .move_to_element(submit_security_code_button)
     .click()
     .perform())


def dismiss_notification_offer(browser):
    # credits InstaPy
    """ Dismiss 'Turn on Notifications' offer on session start """
    offer_elem_loc = "//div/h2[text()='Turn on Notifications']"
    dismiss_elem_loc = "//button[text()='Not Now']"
    # wait a bit and see if the 'Turn on Notifications' offer rises up
    offer_loaded = explicit_wait(
        browser, "VOEL", [offer_elem_loc, "XPath"], 4, False)

    if offer_loaded:
        dismiss_elem = browser.find_element_by_xpath(dismiss_elem_loc)
        dismiss_elem.click()


def explicit_wait(browser, track, ec_params, timeout=35, notify=True):
    # credits InstaPy
    """
    Explicitly wait until expected condition validates
    :param browser: webdriver instance
    :param track: short name of the expected condition
    :param ec_params: expected condition specific parameters - [param1, param2]
    :param timeout: amount of time (in seconds) for browser to wait for element (default: 15s)
    """
    # list of available tracks:
    # <https://seleniumhq.github.io/selenium/docs/api/py/webdriver_support/
    # selenium.webdriver.support.expected_conditions.html>

    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "PFL":
        ec_name = "page fully loaded"
        condition = (lambda browser: browser.execute_script(
            "return document.readyState")
                                     in ["complete" or "loaded"])

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]

        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(browser, timeout)
        result = wait.until(condition)

    except Exception as e:
        return False

    return result
