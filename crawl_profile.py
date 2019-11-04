#!/usr/bin/env python3.5
"""Goes through all usernames and collects their information"""
import sys
from util.settings import Settings
from util.datasaver import Datasaver

from util.cli_helper import get_all_user_names
from util.extractor import extract_information
from util.account import login
from util.chromedriver import SetupBrowserEnvironment


Settings.chromedriver_location = '/usr/bin/chromedriver'

with SetupBrowserEnvironment(chrome_options, capabilities) as browser:
    try:
        if len(Settings.login_username) != 0:
            login(browser, Settings.login_username, Settings.login_password)
    except Exception as exc:
        print("Error login user: " + Settings.login_username)
        sys.exit()
        
    usernames = get_all_user_names()
    for username in usernames:
        print('Extracting information from ' + username)
        information = []
        user_commented_list = []
        try:
            information, user_commented_list = extract_information(browser, username, Settings.limit_amount)
        except:
            print("Error with user " + username)
            sys.exit(1)

        Datasaver.save_profile_json(username,information)

        print ("Number of users who commented on their profile is ", len(user_commented_list),"\n")

        Datasaver.save_profile_commenters_txt(username,user_commented_list)
        print ("\nFinished. The json file and nicknames of users who commented were saved in profiles directory.\n")
