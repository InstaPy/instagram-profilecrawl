# simple module for reading crawled profile information and logging the stats
import json
import datetime
import csv
import argparse
from util.settings import Settings
import glob
import os
import shutil
import sys


def move_file_to_done(profile_filename):
    check_done_folder()
    profile_folder_done = Settings.profile_location + '/done/'
    try:
        shutil.move(profile_filename, profile_folder_done)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        # raise


def write_stats(profile):
    timestamp = profile['scraped']
    username = profile['username']
    print('Reading crawled profile info of {}'.format(username))
    print(profile)

    # sum up likes and comments
    likes = 0
    comments = 0
    for post in profile['posts']:
        likes += post['likes']['count']
        comments += post['comments']['count']

    # append collected stats to stats.csv
    with open('stats.csv', 'a', newline='') as f_stats:
        writer = csv.writer(f_stats)
        writer.writerow([timestamp, profile['username'], profile['followers'], profile['following'],
                         profile['num_of_posts'], likes, comments])
        print('Added stats to stats.csv')


def log_stats(username=None):
    profile_folder = Settings.profile_location + '/'
    if username is None:
        searchFiles = profile_folder + '*.json'
    else:
        searchFiles = profile_folder + username + '*.json'

    list_of_files = glob.glob(searchFiles)  # * means all if need specific format then *.csv
    while list_of_files != []:

        profile_filename = min(list_of_files, key=os.path.getctime)
        print(profile_filename)
        with open(profile_filename, 'r') as f_profile:
            profile = json.load(f_profile)
            write_stats(profile)

        move_file_to_done(profile_filename)

        try:
            list_of_files = glob.glob(searchFiles)  # * means all if need specific format then *.csv
        except:
            print("Unexpected error:", sys.exc_info()[0])
            # raise


def check_done_folder():
    profile_folder_done = Settings.profile_location + '/done/'
    try:
        os.stat(profile_folder_done)
    except:
        os.mkdir(profile_folder_done)


def parse_args():
    parser = argparse.ArgumentParser(description="Read and log collected stats from crawled profiles")
    parser.add_argument("-u", "--user", help="Username", required=False, default=None, dest="user")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    log_stats(args.user)
