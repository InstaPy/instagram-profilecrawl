
import sys
from util.settings import Settings
import re
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from util.exceptions import WebDriverException
from util.instalogger import InstaLogger

def init_chromedriver(chrome_options, capabilities):
    chromedriver_location = Settings.chromedriver_location
    try:
        browser = webdriver.Chrome(chromedriver_location,
                                                desired_capabilities=capabilities,
                                                chrome_options=chrome_options)
    except WebDriverException as exc:
        InstaLogger.logger().error('ensure chromedriver is installed at {}'.format(
            Settings.chromedriver_location))
        raise exc

    matches = re.match(r'^(\d+\.\d+)',
                       browser.capabilities['chrome']['chromedriverVersion'])
    if float(matches.groups()[0]) < Settings.chromedriver_min_version:
        InstaLogger.logger().error('chromedriver {} is not supported, expects {}+'.format(
            float(matches.groups()[0]), Settings.chromedriver_min_version))
        browser.close()
        raise Exception('wrong chromedriver version')

    return browser