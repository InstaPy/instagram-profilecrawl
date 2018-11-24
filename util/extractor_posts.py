"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall
import math
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests
from util.settings import Settings
from .util import web_adress_navigator
import datetime
from util.instalogger import InstaLogger
from util.exceptions import PageNotFound404, NoInstaProfilePageFound, NoInstaPostPageFound


def extract_post_info(browser, postlink):
    """Get the information from the current post"""

    try:
        InstaLogger.logger().info("Scrapping Post Link: " + postlink)
        web_adress_navigator(browser, postlink)
    except PageNotFound404 as e:
        raise NoInstaPostPageFound(e)
    except NoSuchElementException as err:
        InstaLogger.logger().error("Could not get information from post: " + postlink)
        InstaLogger.logger().error(err)
        pass

    post = browser.find_element_by_class_name('ltEKP')
    date = ''
    # Get caption
    caption = ''
    username = ''
    try:
        username = post.find_element_by_class_name('e1e1d').text
    except:
        InstaLogger.logger().error("ERROR - getting Post infos (username) ")

    # Get location details
    location_url = ''
    location_name = ''
    location_id = 0
    lat = ''
    lng = ''

    try:
        # Location url and name
        location_div = post.find_element_by_class_name('M30cS').find_elements_by_tag_name('a')
        if location_div:
            location_url = location_div[0].get_attribute('href')
            location_name = location_div[0].text
            # Longitude and latitude
            location_id = location_url.strip('https://www.instagram.com/explore/locations/').split('/')[0]
            url = 'https://www.instagram.com/explore/locations/' + location_id + '/?__a=1'
            response = requests.get(url)
            data = response.json()
            lat = data['graphql']['location']['lat']
            lng = data['graphql']['location']['lng']
        InstaLogger.logger().info("location_id:" + location_id)
        InstaLogger.logger().info("location_url:" + location_url)
        InstaLogger.logger().info("location_name:" + location_name)
        InstaLogger.logger().info("lat:" + lat)
        InstaLogger.logger().info("lng:" + lng)
    except:
        InstaLogger.logger().error("getting Location Infos  (perhaps not set)")

    try:
        date = post.find_element_by_xpath('//a/time').get_attribute("datetime")
        InstaLogger.logger().info("date:" + str(date))
    except:
        InstaLogger.logger().error("ERROR - getting Post Date ")

    imgs = post.find_elements_by_tag_name('img')
    img = ''

    if len(imgs) >= 2:
        img = imgs[1].get_attribute('src')
    else:
        img = imgs[0].get_attribute('src')

    likes = 0

    if len(post.find_elements_by_tag_name('section')) > 2:
        likes = post.find_elements_by_tag_name('section')[1] \
            .find_element_by_tag_name('div').text
        likes = likes.split(' ')

        # count the names if there is no number displayed
        if len(likes) > 2:
            likes = len([word for word in likes if word not in ['and', 'like', 'this']])
        else:
            likes = likes[0]
            likes = likes.replace(',', '').replace('.', '')
            likes = likes.replace('k', '00')
        InstaLogger.logger().info("post-likes:" + likes)

    #if likes is not known, it would cause errors to convert empty string to int

    try:
        likes = int(likes)
    except Exception as err:
        print ("Extracting number of likes failed. Saving likes as -1")
        print (err)
        likes = -1
        
    user_comments = []
    user_commented_list = []
    mentions = []
    tags = []
    caption = ''
    commentscount = 0

    try:
        user_comments, user_commented_list, commentscount = extract_post_comments(browser, post)
    except:
        InstaLogger.logger().error("trying to get comments (function)")

    try:
        caption, tags = extract_post_caption(user_comments, username)
        # delete first comment because its the caption of the user posted
        if len(caption) > 0:
            user_comments.pop(0)
    except:
        InstaLogger.logger().error("trying to get caption/tags (function)")

    try:
        mentions = extract_post_mentions(browser, post)
    except:
        InstaLogger.logger().error("trying to get mentions (function)")

    return caption, location_url, location_name, location_id, lat, lng, img, tags, int(
        likes), commentscount, date, user_commented_list, user_comments, mentions


def extract_post_mentions(browser, post):
    mentions = []
    if (Settings.mentions is True):
        try:
            if post.find_elements_by_class_name('xUdfV'):  # perhaps JYWcJ
                mention_list = post.find_elements_by_class_name('xUdfV')  # perhaps JYWcJ
                for mention in mention_list:
                    user_mention = mention.get_attribute("href").split('/')
                    mentions.append(user_mention[3])
                InstaLogger.logger().info(str(len(mentions)) + "mentions")
        except:
            InstaLogger.logger().error("getting mentions")
    return mentions


def extract_post_caption(user_comments, username):
    tags = []
    caption = ''
    try:
        if len(user_comments) > 0:
            user_commented = user_comments[0]
            if username == user_commented['user']:
                caption = user_commented['comment']
                InstaLogger.logger().info("caption:" + caption)
                tags = findall(r'#[A-Za-z0-9]*', caption)
    except:
        InstaLogger.logger().error("getting caption")
    return caption, tags


def extract_post_comments(browser, post):
    # if more than 22 comment elements, use the second to see
    # how much comments, else count the li's

    # first element is the text, second either the first comment
    # or the button to display all the comments

    comments = []
    user_commented_list = []
    user_comments = []
    try:
        if post.find_elements_by_tag_name('ul'):
            comment_list = post.find_element_by_tag_name('ul')
            comments = comment_list.find_elements_by_tag_name('li')

            if len(comments) > 1:
                # load hidden comments
                tried_catch_comments = 0
                while (comments[1].text.lower() == 'load more comments' or comments[1].text.lower().startswith(
                        'view all')):
                    try:
                        if comments[1].find_element_by_tag_name('button'):
                            print("click button for loading more")
                            comments[1].find_element_by_tag_name('button').click()
                        elif comments[1].find_element_by_tag_name('a'):
                            print("click a for loading more")
                            comments[1].find_element_by_tag_name('a').click()
                        sleep(Settings.sleep_time_between_comment_loading)
                    except:
                        print("error on clicking - next try (tried: " + str(tried_catch_comments) + ")comments:" + str(len(comments)) + ")")
                        tried_catch_comments = tried_catch_comments + 1
                        if tried_catch_comments > 10:
                            print("exit getting comments")
                            break
                        sleep(Settings.sleep_time_between_comment_loading)

                    comment_list = post.find_element_by_tag_name('ul')
                    comments = comment_list.find_elements_by_tag_name('li')
                # adding who commented into user_commented_list
                InstaLogger.logger().info("found comments" + str(len(comments)))
            else:
                print("1 comment")

            for comm in comments:
                try:
                    user_commented = comm.find_element_by_tag_name('a').get_attribute("href").split('/')
                    user_commented_list.append(user_commented[3])
                except:
                    InstaLogger.logger().error("ERROR something went wrong getting user_commented")
                # first comment has to be loaded everytime to get the caption and tag from post
                if (Settings.output_comments is True or len(user_comments) < 1):
                    user_comment = {}
                    try:
                        user_comment = {
                            'user': user_commented[3],
                            'comment': comm.find_element_by_tag_name('span').text
                        }
                        InstaLogger.logger().info(
                            user_commented[3] + " -- " + comm.find_element_by_tag_name('span').text)
                        user_comments.append(user_comment)
                    except:
                        InstaLogger.logger().error("ERROR something went wrong getting comment")

        InstaLogger.logger().info(str(len(user_commented_list)) + " comments.")
    except BaseException as e:
        InstaLogger.logger().error(e)
    except:
        InstaLogger.logger().error("getting comments")

    return user_comments, user_commented_list, int(len(comments) - 1)
