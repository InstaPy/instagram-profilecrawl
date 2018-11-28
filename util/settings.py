import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings:
    profile_location = os.path.join(BASE_DIR, 'profiles')
    profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
    profile_file_with_timestamp = True
    profile_commentors_file_with_timestamp = True
    limit_amount = 12000
    scrap_posts_infos = True
    output_comments = False
    sleep_time_between_post_scroll = 1.5
    sleep_time_between_comment_loading = 1.5
    mentions = True

    log_output_toconsole = True
    log_output_tofile = True
    log_file_per_run = False
    log_location = os.path.join(BASE_DIR, 'logs')

    #from Instpy
    # Set a logger cache outside object to avoid re-instantiation issues
    loggers = {}
