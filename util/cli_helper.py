"""Util functions for the script"""
import sys


def get_all_user_names():
    """Returns all the usernames given as parameter"""

    usernames = []
    profile_user = []
    user_password = []

    if len(sys.argv) < 2:
        sys.exit('- You need to enter instagram_id username password in order to use program\n')

    if ':' not in sys.argv[-1]:
        for username in sys.argv[1:]:
            usernames.append(username)
    else:
        for username in sys.argv[1:-1]:
            usernames.append(username)
        user, password = str(sys.argv[-1]).split(':')
        profile_user.append(user)
        user_password.append(password)

    return usernames, profile_user, user_password
