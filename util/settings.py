import os
from sys import platform as p_os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OS_ENV = "windows" if p_os == "win32" else "osx" if p_os == "darwin" else "linux"

class Settings:
    profile_location = os.path.join(BASE_DIR, 'profiles')
    profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
    profile_file_with_timestamp = True
    profile_commentors_file_with_timestamp = True
    limit_amount = 4
    scrape_posts_infos = True
    scrape_posts_likers = False
    scrape_follower = False
    output_comments = False
    sleep_time_between_post_scroll = 1.5
    sleep_time_between_comment_loading = 1.5
    mentions = True
    aggregate_tags_stats = True

    log_output_toconsole = True
    log_output_tofile = True
    log_file_per_run = False
    log_location = os.path.join(BASE_DIR, 'logs')

    #from Instpy
    # Set a logger cache outside object to avoid re-instantiation issues
    loggers = {}

    login_username = ''
    login_password = ''

    #chromedriver
    chromedriver_min_version = 2.36
    specific_chromedriver = "chromedriver_{}".format(OS_ENV)
    chromedriver_location = os.path.join(BASE_DIR, "assets", specific_chromedriver)

    if not os.path.exists(chromedriver_location):
        chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver')
