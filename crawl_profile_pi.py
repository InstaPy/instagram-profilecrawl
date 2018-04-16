#!/usr/bin/env python3.5

# use this file for running on Raspberry Pi
"""Goes through all usernames and collects their information"""
import json
from selenium import webdriver
from pyvirtualdisplay import Display
from util.cli_helper import get_all_user_names
from util.extractor import extract_information


display = Display(visible=0, size=(1024, 768))
display.start()

browser = webdriver.Firefox()

# makes sure slower connections work as well        
print ("Waiting 10 sec")
browser.implicitly_wait(10)

try:
  usernames = get_all_user_names()

  for username in usernames:
    print('Extracting information from ' + username)
    information, user_commented_list = extract_information(browser, username)

    with open('./profiles/' + username + '.json', 'w') as fp:
      json.dump(information, fp)

    print ("Number of users who commented on his/her profile is ", len(user_commented_list),"\n")
    file = open("./profiles/" + username + "_commenters.txt","w")
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
  display.stop()
