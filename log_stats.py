# simple module for reading crawled profile information and logging the stats
import json
import datetime
import csv
import argparse
from .util.settings import Settings


def log_stats(username):
    profile_file = Settings.profile_location + '/' + username + '.json'
    with open(profile_file, 'r') as f_profile:
        profile = json.load(f_profile)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

        print('Reading crawled profile info of {}'.format(username))
        print(profile)

        # sum up likes and comments
        likes = 0
        comments = 0
        for post in profile['posts']:
            likes += post['likes']
            comments += post['comments']

        # append collected stats to stats.csv
        with open('stats.csv', 'a', newline='') as f_stats:
            writer = csv.writer(f_stats)
            writer.writerow([timestamp, profile['username'], profile['followers'], profile['following'],
                            profile['num_of_posts'], likes, comments])
            print('Added stats to stats.csv')


def parse_args():
    parser = argparse.ArgumentParser(description="Read and log collected stats from crawled profiles")
    parser.add_argument("-u", "--user", help="Username", required=True, default=None, dest="user")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    log_stats(args.user)
