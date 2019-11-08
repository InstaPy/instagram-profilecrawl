#!/usr/bin/env python3.5
"""Goes through all usernames and collects their information"""
import sys

import arrow
from selenium.common.exceptions import NoSuchElementException

from util.account import login
from util.chromedriver import SetupBrowserEnvironment
from util.extractor import extract_information
from util.extractor_posts import InstagramPost
from util.exceptions import PageNotFound404, NoInstaPostPageFound
from util.settings import Settings


Settings.chromedriver_location = '/usr/bin/chromedriver'


def get_posts_from_username(username, caption, limit_amount):
    with SetupBrowserEnvironment() as browser:
        instagram_stats = []
        ig_stats, _ = extract_information(browser, username, limit_amount)
        now_datetime = arrow.now('US/Pacific')

        for post in ig_stats.posts:
            post_caption = post['caption']
            if caption in post_caption:
                post_stats = {
                    'username': username,
                    'post_url': post['url'],
                    'likes': post['likes']['count'],
                    'views': post['views'],
                    'caption': post_caption,
                    'checked_date': now_datetime.format('MM-DD-YYYY'),
                    'checked_time': now_datetime.format('hh:mm:ss A'),
                    'still_up': True,
                }
                instagram_stats.append(post_stats)

    return instagram_stats


def get_post_from_url(post_url):
    with SetupBrowserEnvironment() as browser:
        now_datetime = arrow.now('US/Pacific')
        try: 
            instagram_post = InstagramPost(browser, post_url)
            instagram_post.extract_post_info()

            post_stats = {
                'username': instagram_post.username,
                'post_url': post_url,
                'likes': instagram_post.likes,
                'views': instagram_post.views,
                'caption': instagram_post.caption,
                'checked_date': now_datetime.format('MM-DD-YYYY'),
                'checked_time': now_datetime.format('hh:mm:ss A'),
                'still_up': True
            }

        except NoInstaPostPageFound:
            post_stats = {
                'post_url': post_url,
                'checked_date': now_datetime.format('MM-DD-YYYY'),
                'checked_time': now_datetime.format('hh:mm:ss A'),
                'still_up': False
            }

    return [post_stats]
