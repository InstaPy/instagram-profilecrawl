"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall
import math
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests
from util.settings import Settings
from .util import web_adress_navigator
from util.extractor_posts import extract_post_info
import datetime
from util.instalogger import InstaLogger
from util.exceptions import PageNotFound404,NoInstaProfilePageFound,NoInstaPostPageFound

def get_user_info(browser):
    """Get the basic user info from the profile screen"""
    num_of_posts = 0
    followers = 0
    following = 0
    prof_img = ""
    bio = ""
    bio_url = ""
    alias_name = ""
    container = browser.find_element_by_class_name('v9tJq')
    isprivate = False

    try:
        infos = container.find_elements_by_class_name('Y8-fY ')
        num_of_posts = extract_exact_info(infos[0])
        followers = extract_exact_info(infos[1])
        following = extract_exact_info(infos[2])
    except:
        InstaLogger.logger().error("Infos (Follower, Abo, Posts) is empty")
        infos = ""

    try:
        alias_name = container.find_element_by_class_name('-vDIg').find_element_by_tag_name('h1').text
    except:
        InstaLogger.logger().info("alias is empty")

    try:
        bio = container.find_element_by_class_name('-vDIg') \
            .find_element_by_tag_name('span').text
    except:
        InstaLogger.logger().info("Bio is empty")

    try:
        bio_url = container.find_element_by_class_name('yLUwa').text
    except:
        InstaLogger.logger().info("Bio Url is empty")

    try:
        img_container = browser.find_element_by_class_name('RR-M-')
        prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
    except:
        InstaLogger.logger().info("image is empty")

    try:
        if container.find_element_by_class_name('Nd_Rl'):
            isprivate = True
    except:
        isprivate = False

    InstaLogger.logger().info("alias name: " + alias_name)
    InstaLogger.logger().info("bio: " + bio)
    InstaLogger.logger().info("url: " + bio_url)
    InstaLogger.logger().info("Posts: " + str(num_of_posts))
    InstaLogger.logger().info("Follower: " + str(followers))
    InstaLogger.logger().info("Following: " + str(following))
    InstaLogger.logger().info("isPrivate: " + str(isprivate))
    return alias_name, bio, prof_img, num_of_posts, followers, following, bio_url, isprivate


def extract_exact_info(info):
    exact_info = 0
    try:
        exact_info = int(info.find_element_by_tag_name('span').get_attribute('title').replace('.', '').replace(',', ''))
    except:
        exact_info = str(info.text.split(' ')[0].replace(',', ''))
        if exact_info.find('.') != -1:
            exact_info = exact_info.replace('.', '')
            exact_info = int(exact_info.replace('k', '00').replace('m', '00000'))
        else:
            exact_info = int(exact_info.replace('k', '000').replace('m', '000000'))
    return exact_info


def extract_user_posts(browser, num_of_posts_to_do):
    """Get all posts from user"""
    links = []
    links2 = []
    preview_imgs = {}

    # list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    # list links2 contains all the links collected so far
    # preview_imgs dictionary maps link in links2 to link's post's preview image src
    try:
        body_elem = browser.find_element_by_tag_name('body')

        # load_button = body_elem.find_element_by_xpath\
        #  ('//a[contains(@class, "_1cr2e _epyes")]')
        # body_elem.send_keys(Keys.END)
        # sleep(3)

        previouslen = 0
        breaking = 0
       
        print ("number of posts to do: ", num_of_posts_to_do)
        num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)
        print("Getting first", num_of_posts_to_scroll,
              "posts but check ", num_of_posts_to_do,
              " posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")
        while (len(links2) < num_of_posts_to_do):   
            
            prev_divs = browser.find_elements_by_tag_name('main')
            links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
            links = sum([[link_elem.get_attribute('href')
                          for link_elem in elems] for elems in links_elems], [])
            
            for elems in links_elems:
                for link_elem in elems:
                    
                    href = link_elem.get_attribute('href')
                    try:
                        if "/p/" in href:
                            try:
                                img = link_elem.find_element_by_tag_name('img')
                                src = img.get_attribute('src')
                                preview_imgs[href] = src
                            except NoSuchElementException:
                                print ("img exception 132")
                                continue       
                    except Exception as err:
                        print (err)
                        
            for link in links:
                if "/p/" in link:
                    if (len(links2) < num_of_posts_to_do):
                        links2.append(link)
            links2 = list(set(links2))
            print("Scrolling profile ", len(links2), "/", num_of_posts_to_scroll)
            body_elem.send_keys(Keys.END)
            sleep(Settings.sleep_time_between_post_scroll)

            ##remove bellow part to never break the scrolling script before reaching the num_of_posts
            if (len(links2) == previouslen):
                breaking += 1
                print("breaking in ", 4 - breaking,
                      "...\nIf you believe this is only caused by slow internet, increase sleep time 'sleep_time_between_post_scroll' in settings.py")
            else:
                breaking = 0
            if breaking > 3:
                print("Not getting any more posts, ending scrolling")
                sleep(2)
                break
            previouslen = len(links2)
            ##

    except NoSuchElementException as err:
        InstaLogger.logger().error('Something went terribly wrong')

    post_infos = []

    counter = 1
    # into user_commented_total_list I will add all username links who commented on any post of this user
    user_commented_total_list = []

    for postlink in links2:

        print("\n", counter, "/", len(links2))
        counter = counter + 1

        try:
            caption, location_url, location_name, location_id, lat, lng, img, tags, likes, commentscount, date, user_commented_list, user_comments, mentions = extract_post_info(
                browser, postlink)

            location = {
                'location_url': location_url,
                'location_name': location_name,
                'location_id': location_id,
                'latitude': lat,
                'longitude': lng,
            }

            post_infos.append({
                'caption': caption,
                'location': location,
                'img': img,
                'preview_img': preview_imgs.get(postlink, None),
                'date': date,
                'tags': tags,
                'likes': likes,
                'url': postlink,
                'comments': {
                    'count': commentscount,
                    'list': user_comments
                },
                'mentions': mentions
            })
            user_commented_total_list = user_commented_total_list + user_commented_list
        except NoSuchElementException as err:
            InstaLogger.logger().error("Could not get information from post: " + postlink)
            InstaLogger.logger().error(err)
        except:
            InstaLogger.logger().error("Could not get information from post: " + postlink)
    return post_infos, user_commented_total_list


def extract_information(browser, username, limit_amount):
    InstaLogger.logger().info('Extracting information from ' + username)
    """Get all the information for the given username"""
    isprivate = False
    try:
        user_link = "https://www.instagram.com/{}/".format(username)
        web_adress_navigator(browser, user_link)
    except PageNotFound404 as e:
        raise NoInstaProfilePageFound(e)

    num_of_posts_to_do = 999999
    alias_name = ''
    bio = ''
    prof_img = ''
    num_of_posts = 0
    followers = 0
    following = 0
    bio_url = ''
    try:
        alias_name, bio, prof_img, num_of_posts, followers, following, bio_url, isprivate = get_user_info(browser)
        if limit_amount < 1:
            limit_amount = 999999
        num_of_posts_to_do = min(limit_amount, num_of_posts)
    except Exception as err:
        InstaLogger.logger().error("Couldn't get user profile. - Terminating")
        quit()
    prev_divs = browser.find_elements_by_class_name('_70iju')

    post_infos = []
    user_commented_total_list = []
    if Settings.scrap_posts_infos is True and isprivate is False:
        try:
            post_infos, user_commented_total_list = extract_user_posts(browser, num_of_posts_to_do)
        except:
            InstaLogger.logger().error("Couldn't get user posts.")

    information = {
        'alias': alias_name,
        'username': username,
        'bio': bio,
        'prof_img': prof_img,
        'num_of_posts': num_of_posts,
        'followers': followers,
        'following': following,
        'bio_url': bio_url,
        'isprivate': isprivate,
        'scrapped': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'posts': post_infos
    }

    InstaLogger.logger().info( "User " +  username + " has " + str(len(user_commented_total_list)) + " comments.")

    # sorts the list by frequencies, so users who comment the most are at the top
    import collections
    from operator import itemgetter, attrgetter
    counter = collections.Counter(user_commented_total_list)
    com = sorted(counter.most_common(), key=itemgetter(1, 0), reverse=True)
    com = map(lambda x: [x[0]] * x[1], com)
    user_commented_total_list = [item for sublist in com for item in sublist]

    # remove duplicates preserving order (that's why not using set())
    user_commented_list = []
    last = ''
    for i in range(len(user_commented_total_list)):
        if username.lower() != user_commented_total_list[i]:
            if last != user_commented_total_list[i]:
                user_commented_list.append(user_commented_total_list[i])
            last = user_commented_total_list[i]

    return information, user_commented_list
