import glob
import requests
import json
from util.settings import Settings
import os
import shutil
import sys

profile_folder = Settings.profile_location + '/'
profile_folder_done = Settings.profile_location + '/done/'





list_of_files = glob.glob(profile_folder + '*.json') # * means all if need specific format then *.csv
if list_of_files==[]:
    print('Alles erledigt')
    sys.exit(0)

#print(list_of_files)
latest_file = min(list_of_files, key=os.path.getctime)

profile_filename = latest_file


try:
    os.stat(profile_folder_done)
except:
    os.mkdir(profile_folder_done)



url = 'http://trendmatch.test/instagramerinfo'
headers = {'Authorization' : 'xxx', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
r = requests.post(url, data=open(profile_filename, 'rb'), headers=headers)

print (r.text)
print (r.status_code)

if(r.status_code==201):
    shutil.move(profile_filename, profile_folder_done)
