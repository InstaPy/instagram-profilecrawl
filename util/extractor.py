import json

def get_general_user_info(browser, username):
  browser.get('https://www.instagram.com/{username}/?__a=1'.format(username=username))
  user = json.loads(browser.find_element_by_tag_name("pre").text)['user']

  return user['id'], user['biography'], \
         user['full_name'], user['profile_pic_url'], \
         user['followed_by']['count'], user['follows']['count'], \
         user['media']['count']

def get_user_followers(browser, user_id, follower_count):
  browser.get(
    'https://www.instagram.com/graphql/query/?query_id=17851374694183129&variables=%7B"id":"{id}","first":{count}%7D'.format(
      id=user_id, count=follower_count))
  user_followers = json.loads(browser.find_element_by_tag_name("pre").text)['data']['user']['edge_followed_by']['edges']

  return [{
    'username': profile['username'],
    'full_name': profile['full_name'],
    'profile_pic': profile['profile_pic_url']
  } for profile in user_followers]

def get_user_followings(browser, user_id, following_count):
  browser.get(
    'https://www.instagram.com/graphql/query/?query_id=17874545323001329&variables=%7B"id":{id},"first":{count}%7D'.format(
      id=user_id, count=following_count))
  user_followings = json.loads(browser.find_element_by_tag_name("pre").text)['data']['user']['edge_follow']['edges']

  return [{
    'username': profile['username'],
    'full_name': profile['full_name'],
    'profile_pic': profile['profile_pic_url']
  } for profile in user_followings]

def get_user_posts(browser, user_id, post_count):
  browser.get(
    'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B"id":{id},"first":{count}%7D'.format(
      id=user_id, count=post_count))

  print(json.loads(browser.find_element_by_tag_name("pre").text))

  user_posts = json.loads(browser.find_element_by_tag_name("pre").text)['data']['user']['edge_owner_to_timeline_media']['edges']

  return [{
    'caption': post['edge_media_to_caption']['edges'][0]['node']['text'],
    'media_url': post['display_url'],
    'num_of_comments': post['edge_media_to_comment']['count'],
    'num_of_likes': post['edge_media_preview_like']['count'],
    'is_video': post['is_video']
  } for post in user_posts if post] if len(user_posts) > 0 else []

def extract_information(browser, username):
  user_id, \
  biography, \
  full_name, \
  profile_pic, \
  follower_count, \
  following_count, \
  post_count = get_general_user_info(browser, username)

  followers = get_user_followers(browser, user_id, follower_count)
  followings = get_user_followings(browser, user_id, following_count)
  #TODO get the data of all the posts
  posts = []#get_user_posts(browser, user_id, post_count)

  return {
    'user': {
      'full_name': full_name,
      'biography': biography,
      'profile_pic': profile_pic
    },
    'followers': {
      'amount': follower_count,
      'profiles': followers
    },
    'following': {
      'amount': following_count,
      'profiles': followings
    },
    'media': {
      'amount': post_count,
      'posts': posts
    }
  }