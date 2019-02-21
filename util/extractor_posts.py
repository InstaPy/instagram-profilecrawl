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
        InstaLogger.logger().info("Scraping Post Link: " + postlink)
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

    img_tags = []
    imgs = []
    imgdesc = []
    views = 0

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
        InstaLogger.logger().info("location_id: " + location_id)
        InstaLogger.logger().info("location_url: " + location_url)
        InstaLogger.logger().info("location_name: " + location_name)
        InstaLogger.logger().info("lat: " + lat)
        InstaLogger.logger().info("lng: " + lng)
    except:
        InstaLogger.logger().warning("getting Location Infos (perhaps not set)")

    try:
        date = post.find_element_by_xpath('//a/time').get_attribute("datetime")
        InstaLogger.logger().info("Post date: " + str(date))
    except:
        InstaLogger.logger().error("ERROR - getting Post Date ")

    try:
        img_tags = post.find_elements_by_class_name('FFVAD')
        InstaLogger.logger().info("number of images: " + str(len(img_tags)))
        for i in img_tags:
            imgs.append(i.get_attribute('src'))
            imgdesc.append(i.get_attribute('alt'))
            InstaLogger.logger().info("post image: " + imgs[-1])
            InstaLogger.logger().info("alt text: " + imgdesc[-1])
    except:
        InstaLogger.logger().error("ERROR - Post Image")

    likes = 0

    try:
        #if len(post.find_elements_by_xpath('//article/div/section')) > 2:
        # image or video post?
        if len(img_tags) >= 1:
            likes = post.find_element_by_xpath('//article/div[2]/section[2]/div/div/a/span').text
        else:
            try:
                views = int(post.find_element_by_xpath('//article/div[2]/section[2]/div/span/span').text.replace(",", ""))
                InstaLogger.logger().info("video views: " + str(views))
            except:
                InstaLogger.logger().error("ERROR - Getting Video Views")
            #click the view count to get the likes popup
            viewcount_click = post.find_element_by_xpath('//article/div[2]/section[2]/div/span')
            browser.execute_script("arguments[0].click();", viewcount_click)
            likes = post.find_element_by_xpath('//article/div[2]/section[2]/div/div/div[4]/span').text

        likes = likes.replace(',', '').replace('.', '')
        likes = likes.replace('k', '00')
        InstaLogger.logger().info("post likes: " + likes)
    except Exception as err:
        InstaLogger.logger().error("ERROR - Getting Post Likes")
        InstaLogger.logger().error(err)
    # if likes is not known, it would cause errors to convert empty string to int

    try:
        likes = int(likes)
    except Exception as err:
        InstaLogger.logger().error("ERROR - Extracting number of likes failed. Saving likes as -1")
        InstaLogger.logger().error(err)
        likes = -1

    user_comments = []
    user_commented_list = []
    user_liked_list = []
    mentions = []
    tags = []
    caption = ''
    commentscount = 0

    try:
        user_comments, user_commented_list, commentscount = extract_post_comments(browser, post)
    except:
        InstaLogger.logger().error("ERROR - getting Post comments function trying")

    try:
        caption, tags = extract_post_caption(user_comments, username)
        # delete first comment because its the caption of the user posted
        if len(caption) > 0:
            user_comments.pop(0)
    except:
        InstaLogger.logger().error("ERROR - getting Post caption/tags function")

    try:
        mentions = extract_post_mentions(browser, post)
    except:
        InstaLogger.logger().error("ERROR - getting Post Mentions function")

    try:
        user_liked_list = extract_post_likers(browser, post, postlink, likes)
    except:
        InstaLogger.logger().error("ERROR - getting Post Likers function")

    return caption, location_url, location_name, location_id, lat, lng, imgs, imgdesc, tags, int(
        likes), commentscount, date, user_commented_list, user_comments, mentions, user_liked_list, views


def extract_post_mentions(browser, post):
    mentions = []
    if (Settings.mentions is False):
        return mentions

    try:
        if post.find_elements_by_class_name('JYWcJ'):  # perhaps JYWcJ
            mention_list = post.find_elements_by_class_name('JYWcJ')  # perhaps JYWcJ
            for mention in mention_list:
                user_mention = mention.get_attribute("href").split('/')
                mentions.append(user_mention[3])
            InstaLogger.logger().info("mentions: " + str(len(mentions)))
    except Exception as err:
        InstaLogger.logger().error("Error - getting mentions")
        InstaLogger.logger().error(err)
    return mentions


def extract_post_caption(user_comments, username):
    tags = []
    caption = ''
    try:
        if len(user_comments) > 0:
            user_commented = user_comments[0]
            if username == user_commented['user']:
                caption = user_commented['comment']
                InstaLogger.logger().info("caption: " + caption)
                tags = findall(r'#[A-Za-z0-9äöüß]*', caption)
    except Exception as err:
        InstaLogger.logger().error("Error - getting caption")
        InstaLogger.logger().error(err)
    return caption, tags


def extract_post_comments(browser, post):
    # if more than 22 comment elements, use the second to see
    # how much comments, else count the li's

    # first element is the text, second either the first comment
    # or the button to display all the comments

    # sometimes getting comments ends in a endless loop
    # therefore reduce the run
    clicks_on_button = 0
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
                            print("clicking button for loading more comments")
                            browser.execute_script("arguments[0].click();", comments[1].find_element_by_tag_name('button'))
                            clicks_on_button = clicks_on_button + 1
                        elif comments[1].find_element_by_tag_name('a'):
                            print("clicking a for loading more")
                            browser.execute_script("arguments[0].click();", comments[1].find_element_by_tag_name('a'))
                            clicks_on_button = clicks_on_button + 1
                        sleep(Settings.sleep_time_between_comment_loading)
                        if (clicks_on_button >= Settings.max_buttonclicks_viewmorecomments):
                            InstaLogger.logger().warning("Clicked Button: " + str(clicks_on_button) + " to view more comments - perhaps there are some more perhaps there is a endless loop")
                            break
                    except:
                        print("error clicking - next try (tried: " + str(tried_catch_comments) + ") comments:" + str(
                            len(comments)) + ")")
                        tried_catch_comments = tried_catch_comments + 1
                        if tried_catch_comments > 10:
                            print("exit getting comments")
                            break
                        sleep(Settings.sleep_time_between_comment_loading)

                    comment_list = post.find_element_by_tag_name('ul')
                    comments = comment_list.find_elements_by_tag_name('li')
                InstaLogger.logger().info("found comments: " + str(len(comments)))
            else:
                print("found comment: 1")

            # adding who commented into user_commented_list
            for comm in comments:
                try:
                    user_commented = comm.find_element_by_tag_name('a').get_attribute("href").split('/')
                    user_commented_list.append(user_commented[3])
                except:
                    InstaLogger.logger().error("ERROR something went wrong getting user_commented")
                # first comment has to be loaded every time to get the caption and tag from post
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
        InstaLogger.logger().error("Error - getting comments")

    return user_comments, user_commented_list, int(len(comments) - 1)


def extract_post_likers(browser, post, postlink, likes):
    user_liked_list = []
    if (Settings.scrape_posts_likers is False):
        return user_liked_list
    else:
        InstaLogger.logger().info("GETTING LIKERS FROM POST")

    postlink = postlink + "liked_by/"
    try:

        post.find_element_by_xpath("//a[@class='zV_Nj']").click()

        likers_list = post.find_elements_by_xpath("//li[@class='wo9IH']//a[contains(@class, 'FPmhX')]")

        tried_catch_likers = 0
        while len(likers_list) < likes:
            likers_list_before = len(likers_list)
            InstaLogger.logger().info(
                "found likers: " + str(len(likers_list)) + " should be " + str(likes) + " -- scroll for more")
            try:
                div_likebox_elem = browser.find_element_by_xpath("//div[contains(@class, 'wwxN2')]")
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div_likebox_elem)

            except BaseException as e:
                tried_catch_likers = tried_catch_likers + 1
                print("error on scrolling - next try (tried: " + str(tried_catch_likers) + ") Message:" + e)

            sleep(Settings.sleep_time_between_post_scroll)
            likers_list = post.find_elements_by_xpath("//li[@class='wo9IH']//a[contains(@class, 'FPmhX')]")
            if (likers_list_before == len(likers_list)):
                tried_catch_likers = tried_catch_likers + 1
                print("error on scrolling - next try (tried: " + str(tried_catch_likers) + ")")
                sleep(Settings.sleep_time_between_post_scroll * 1.5)

            if tried_catch_likers > 10:
                print("exit scrolling likers")
                break

        likers_list = post.find_elements_by_xpath("//li[@class='wo9IH']//a[contains(@class, 'FPmhX')]")

        for liker in likers_list:
            user_like = liker.get_attribute("href").split('/')
            user_liked_list.append(user_like[3])

        InstaLogger.logger().info('likers: ' + str(len(user_liked_list)))

    except BaseException as e:
        InstaLogger.logger().error("Error - getting post likers")
        InstaLogger.logger().error(e)
    return user_liked_list
