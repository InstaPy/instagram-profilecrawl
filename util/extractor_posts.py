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
from util.exceptions import PageNotFound404, NoInstaPostPageFound


class InstagramPost:
    def __init__(self, browser, postlink):
        self.browser = browser
        self.postlink = postlink

        try:
            InstaLogger.logger().info("Scraping Post Link: " + self.postlink)
            web_adress_navigator(self.browser, self.postlink)
        except PageNotFound404 as e:
            raise NoInstaPostPageFound(e)
        except NoSuchElementException as err:
            InstaLogger.logger().error("Could not get information from post: " + self.postlink)
            InstaLogger.logger().error(err)
            pass

        self.post = self.browser.find_element_by_class_name('ltEKP')

    def extract_post_info(self):
        """Get the information from the current post"""
        self.username = self.extract_username()
        self.date = self.extract_date()
        self.location_url, self.location_name, self.location_id, self.lat, self.lng = self.extract_location()

        self.img_tags, self.imgs, self.imgdesc = self.extract_image_data()

        likes, self.views = self.extract_likes_views(self.img_tags)
        self.likes = int(likes)

        self.comments, self.commentscount = self.extract_comments()

        self.user_commented_list, self.user_comments = self.extract_users_from_comments(self.comments)
        self.user_liked_list = self.extract_likers(self.likes)

        self.caption = self.extract_caption(self.user_comments, self.username)

        # delete first comment because its the caption of the user posted
        if len(self.caption) > 0:
            self.user_comments.pop(0)

        self.tags = self.extract_tags_from_caption(self.caption)
        self.mentions = self.extract_post_mentions()

    def extract_likes_views(self, img_tags):
        likes = 0
        views = 0

        try:
            # if len(self.post.find_elements_by_xpath('//article/div/section')) > 2:
            # image or video post?
            if len(img_tags) >= 1:
                likes = self.post.find_element_by_xpath('//article/div[2]/section[2]/div/div/button/span').text
            else:
                try:
                    views = int(
                        self.post.find_element_by_xpath('//article/div[2]/section[2]/div/span/span').text.replace(",", ""))
                    InstaLogger.logger().info("video views: " + str(views))
                except:
                    InstaLogger.logger().error("ERROR - Getting Video Views")
                # click the view count to get the likes popup
                viewcount_click = self.post.find_element_by_xpath('//article/div[2]/section[2]/div/span')
                self.browser.execute_script("arguments[0].click();", viewcount_click)
                likes = self.post.find_element_by_xpath('//article/div[2]/section[2]/div/div/div[4]/span').text

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

        return likes, views
    
    def extract_username(self):
        username = ''

        try:
            username = self.post.find_element_by_class_name('e1e1d').find_element_by_tag_name('a').text
        except:
            InstaLogger.logger().error("ERROR - getting Post infos (username) ")

        return username

    def extract_location(self):
        # Get location details
        location_url = ''
        location_name = ''
        location_id = 0
        lat = ''
        lng = ''

        try:
            # Location url and name
            location_div = self.post.find_element_by_class_name('M30cS').find_elements_by_tag_name('a')
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
            InstaLogger.logger().info("location_id: " + str(location_id))
            InstaLogger.logger().info("location_url: " + str(location_url))
            InstaLogger.logger().info("location_name: " + str(location_name))
            InstaLogger.logger().info("lat: " + str(lat))
            InstaLogger.logger().info("lng: " + str(lng))
        except Exception as err:
            InstaLogger.logger().warning("getting Location Infos (perhaps not set)")

        return location_url, location_name, location_id, lat, lng

    def extract_date(self):
        date = ''

        try:
            date = self.post.find_element_by_xpath('//a/time').get_attribute("datetime")
            InstaLogger.logger().info("Post date: " + str(date))
        except:
            InstaLogger.logger().error("ERROR - getting Post Date ")

        return date

    def extract_image_data(self):
        img_tags = []
        imgs = []
        imgdesc = []

        img_tags = self.post.find_elements_by_class_name('FFVAD')
        InstaLogger.logger().info("number of images: " + str(len(img_tags)))

        for i in img_tags:
            imgs.append(i.get_attribute('src'))
            imgdesc.append(i.get_attribute('alt'))
            InstaLogger.logger().info(f"post image: {imgs[-1]}")
            InstaLogger.logger().info(f"alt text: {imgdesc[-1]}")

        return img_tags, imgs, imgdesc

    def extract_post_mentions(self):
        mentions = []
        if (Settings.mentions is False):
            return mentions

        if self.post.find_elements_by_class_name('JYWcJ'):  # perhaps JYWcJ
            mention_list = self.post.find_elements_by_class_name('JYWcJ')  # perhaps JYWcJ
            for mention in mention_list:
                user_mention = mention.get_attribute("href").split('/')
                mentions.append(user_mention[3])
            InstaLogger.logger().info(f"mentions: {str(len(mentions))}")

        return mentions

    def extract_caption(self, user_comments, username):
        caption = ''
        if len(user_comments) > 0:
            user_commented = user_comments[0]
            if username == user_commented['user']:
                caption = user_commented['comment']
                InstaLogger.logger().info(f"caption: {caption}")
        return caption

    def extract_tags_from_caption(self, caption):
        return findall(r'#\w+', caption)

    def extract_comments(self):
        comments_found_last_run = 0
        comments_run_same_length = 0
        comments = []

        try:
            if self.post.find_elements_by_tag_name('ul'):
                comment_list = self.post.find_element_by_tag_name('ul')
                comments = comment_list.find_elements_by_tag_name('li')

                """
                if len(comments) > 1:
                    # load hidden comments
                    comments = load_more_comments(comments)
                    InstaLogger.logger().info(f"found comments: {len(comments)}")

                else:
                    InstaLogger.logger().info("found comment: 1")
                """
        except BaseException as e:
            InstaLogger.logger().error(e)
        except:
            InstaLogger.logger().error("Error - getting comments")

        return comments, int(len(comments) - 1)

    def load_more_comments(self, comments):
        tried_catch_comments = 0

        while (comments[1].text.lower() == 'load more comments' or 
               comments[1].text.lower().startswith('view all')):
            try:
                if comments[1].find_element_by_tag_name('button'):
                    InstaLogger.logger().info("clicking button for loading more comments")
                    self.browser.execute_script("arguments[0].click();",
                                           comments[1].find_element_by_tag_name('button'))
                elif comments[1].find_element_by_tag_name('a'):
                    InstaLogger.logger().info("clicking a for loading more")
                    self.browser.execute_script("arguments[0].click();", comments[1].find_element_by_tag_name('a'))

                sleep(Settings.sleep_time_between_comment_loading)

                comment_list = self.post.find_element_by_tag_name('ul')
                comments = comment_list.find_elements_by_tag_name('li')
                InstaLogger.logger().info(f"comments (loaded: {len(comments)} /lastrun: {comments_found_last_run})")

                if (comments_found_last_run == len(comments)):
                    comments_run_same_length = comments_run_same_length + 1
                    if comments_run_same_length > 10:
                        InstaLogger.logger().error(f"exit getting comments: {comments_run_same_length} x same length of comments, perhaps endless loop")
                        break
                else:
                    comments_same_length = 0

                comments_found_last_run = len(comments)
            except:
                InstaLogger.logger().error(
                    f"error clicking - next try (tried: {tried_catch_comments}) comments: {len(comments)}")
                tried_catch_comments = tried_catch_comments + 1
                if tried_catch_comments > 10:
                    InstaLogger.logger().error(
                        f"exit getting comments, {tried_catch_comments}x tried to get comments")
                    break
                sleep(Settings.sleep_time_between_comment_loading)

        return comments

    def extract_users_from_comments(self, comments):
        # adding who commented into user_commented_list
        user_commented_list = []
        user_comments = []

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
                        'comment': comm.find_element_by_css_selector('h2 + span, h3 + span').text
                    }
                    InstaLogger.logger().info(user_comment)
                    InstaLogger.logger().info(
                        user_commented[3] + " -- " + comm.find_element_by_css_selector('h2 + span, h3 + span').text)
                    user_comments.append(user_comment)
                except:
                    InstaLogger.logger().error("ERROR something went wrong getting comment")

        InstaLogger.logger().info(str(len(user_commented_list)) + " comments.")
        return user_commented_list, user_comments

    def extract_likers(self, likes):
        user_liked_list = []

        xpath_identifier_user = "//div[contains(@class, 'HVWg4') or contains(@class ,'btag')]/div/div/div/a"

        if (Settings.scrape_posts_likers is False):
            return user_liked_list
        else:
            InstaLogger.logger().info("GETTING LIKERS FROM POST")

        self.postlink = self.postlink + "liked_by/"
        tried_catch_likers = 0
        likers_list_before = 0
        try:
            # self.post.find_element_by_xpath("//a[contains(@class, 'zV_Nj')]").click()
            elementToClick = self.post.find_element_by_xpath("//a[contains(@class, 'zV_Nj')]")
            self.browser.execute_script("arguments[0].click();", elementToClick)
            sleep(3)

            # likers_list = self.post.find_elements_by_xpath("//li[@class='wo9IH']//a[contains(@class, 'FPmhX')]")
            likers_list = self.post.find_elements_by_xpath(xpath_identifier_user)
            InstaLogger.logger().info("LÄNGE " + str(len(likers_list)) + "")

            while len(likers_list) < likes:
                InstaLogger.logger().info(
                    "new likers in actual view: " + str(len(likers_list)) + " - list: " + str(
                        len(user_liked_list)) + " should be " + str(likes) + " -- scroll for more")
                try:
                    div_likebox_elem = self.browser.find_element_by_xpath(
                        "//div[contains(@class, 'i0EQd')]/div/div/div[last()]")  # old:wwxN2
                    # self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div_likebox_elem)
                    self.browser.execute_script("arguments[0].scrollIntoView(true);", div_likebox_elem)
                except BaseException as e:
                    tried_catch_likers = tried_catch_likers + 1
                    div_likebox_elem = self.browser.find_element_by_xpath(
                        "//div[contains(@class, 'i0EQd')]/div/div/div[1]")
                    self.browser.execute_script("arguments[0].scrollIntoView(true);", div_likebox_elem)
                    InstaLogger.logger().info("error on scrolling - next try (tried: " + str(tried_catch_likers) + ") Message:" + e)

                sleep(Settings.sleep_time_between_post_scroll)

                # likers_list = self.post.find_elements_by_xpath(" //li[@class='wo9IH']//a[contains(@class, 'FPmhX')]")
                likers_list = self.post.find_elements_by_xpath(xpath_identifier_user)
                for liker in likers_list:
                    user_like = liker.get_attribute("href").split('/')
                    username_liked_post = user_like[3]
                    if username_liked_post not in user_liked_list:
                        user_liked_list.append(username_liked_post)

                if (likers_list_before == len(user_liked_list)):
                    tried_catch_likers = tried_catch_likers + 1
                    InstaLogger.logger().info("error on scrolling - next try (tried: " + str(tried_catch_likers) + ")")
                    sleep(Settings.sleep_time_between_post_scroll * 1.5)
                    div_likebox_elem = self.browser.find_element_by_xpath(
                        "//div[contains(@class, 'i0EQd')]/div/div/div[1]")
                    self.browser.execute_script("arguments[0].scrollIntoView(true);", div_likebox_elem)

                if tried_catch_likers > 10:
                    InstaLogger.logger().error("exit scrolling likers " + str(tried_catch_likers) + "x tries - liker list: " + str(
                        len(user_liked_list)) + " should be " + str(likes) + "")
                    break
                likers_list_before = len(user_liked_list)

            InstaLogger.logger().info('likers: ' + str(len(user_liked_list)))

        except BaseException as e:
            InstaLogger.logger().error("Error - getting post likers")
            InstaLogger.logger().error(e)

        return user_liked_list
