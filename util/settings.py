import os
from sys import platform as p_os
from os.path import abspath, dirname, join
from os import getenv
from dotenv import load_dotenv

# ROOT_DIR = abspath(dirname(__file__))
BASE_DIR = abspath(dirname(__file__))
dotenv_path = join(BASE_DIR, '.env')
load_dotenv(dotenv_path)
IG_USERNAME = getenv("IG_USERNAME", "")
IG_PASSWORD = getenv("IG_PASSWORD", "")

OS_ENV = "windows" if p_os == "win32" else "osx" if p_os == "darwin" else "linux"


class Settings:
    profile_location = os.path.join(BASE_DIR, 'profiles')
    profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
    profile_file_with_timestamp = True
    profile_commentors_file_with_timestamp = True
    limit_amount = 1000
    scrape_posts_infos = True
    scrape_posts_likers = False
    scrape_follower = False
    output_comments = False
    sleep_time_between_post_scroll = 14.5
    sleep_time_between_comment_loading = 1.5
    mentions = True

    log_output_toconsole = True
    log_output_tofile = True
    log_file_per_run = False
    log_location = join(BASE_DIR, 'logs')

    # from Instpy
    # Set a logger cache outside object to avoid re-instantiation issues
    loggers = {}

    login_username = IG_USERNAME
    login_password = IG_PASSWORD

    # chromedriver
    chromedriver_min_version = 2.36
    specific_chromedriver = f"chromedriver_{OS_ENV}"
    chromedriver_location = os.path.join(BASE_DIR, "assets", specific_chromedriver)

    if not os.path.exists(chromedriver_location):
        chromedriver_location = os.path.join(BASE_DIR, 'assets', 'chromedriver')
