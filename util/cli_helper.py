"""Util functions for the script"""
import sys


def get_all_user_names():
    """Returns all the usernames given as parameter"""
    usernames = []

    if len(sys.argv) < 2:
        sys.exit('- You need to enter instagram_id username password in order to use program\n')

    usernames.append(sys.argv[1])

    return usernames

def get_id_and_pass():
    """get's the second & third arguments user enter and assign them to user & pass"""
    username_id = []
    password = []
    try:
        username_id.append(sys.argv[2])
        password.append(sys.argv[3])
    except:
        sys.exit('- You need to provide username and password of your account for the program\n')

    return username_id, password
