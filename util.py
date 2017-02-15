"""Util functions for the script"""
import sys

def get_all_user_names():
  """Returns all the usernames given as parameter"""
  usernames = []

  #display provide username
  if len(sys.argv) < 2:
    sys.exit('- Please provide at least one username!\n')

  for username in sys.argv[1:]:
    usernames.append(username)

  print(usernames)

  return usernames
