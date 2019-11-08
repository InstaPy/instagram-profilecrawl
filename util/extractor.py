"""Methods to extract the data for the given usernames profile"""
import sys
from time import sleep, time
from re import findall
import math

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from util.settings import Settings
from .util import web_adress_navigator
from util.extractor_posts import InstagramPost
import datetime
from util.instalogger import InstaLogger
from util.exceptions import PageNotFound404, NoInstaProfilePageFound


class InstagramUser:
    def __init__(self, browser, username):
        self.browser = browser
        self.username = username
        self.num_of_posts = {'count': 0}
        self.followers = {'count' : 0}
        self.following = {'count' : 0}
        self.profile_image = ""
        self.bio = ""
        self.bio_url = ""
        self.alias = ""
        self.isprivate = False
        self.container = self.browser.find_element_by_class_name('v9tJq')
        self.posts = []
        self.scraped = None

    def _is_user_private(self):
        try:
            if self.container.find_element_by_class_name('Nd_Rl'):
                isprivate = True
        except:
            isprivate = False

        return isprivate

    def _user_alias(self):
        alias = self.container.find_element_by_class_name('-vDIg').find_element_by_tag_name('h1').text

        return alias

    def _user_bio(self):
        bio = self.container.find_element_by_class_name('-vDIg').find_element_by_tag_name('span').text
        return bio

    def _user_bio_url(self):
        try:
            bio_url = self.container.find_element_by_class_name('yLUwa').text
            return bio_url
        except NoSuchElementException:
            return self.bio_url


    def _user_profile_image(self):
        try:
            img_container = self.browser.find_element_by_class_name('RR-M-')
            profile_image = img_container.find_element_by_tag_name('img').get_attribute('src')
            return profile_image
        except NoSuchElementException:
            return self.profile_image


    def get_user_info(self):
        """Get the basic user info from the profile screen"""
        
        self.isprivate = self._is_user_private()
        self.alias = self._user_alias()
        self.bio = self._user_bio()
        self.bio_url = self._user_bio_url()
        self.profile_image = self._user_profile_image()

        infos = self.container.find_elements_by_class_name('Y8-fY')
        if infos:
            self.num_of_posts = {'count': extract_exact_info(infos[0])}
            self.following = {'count' : extract_exact_info(infos[2])}
            self.followers = {'count' : extract_exact_info(infos[1])}

            if Settings.scrape_follower == True:
                if not isprivate:
                    self.followers['list'] = extract_followers(self.browser, self.username)


        InstaLogger.logger().info("Alias name: " + self.alias)
        InstaLogger.logger().info("Bio: " + self.bio)
        InstaLogger.logger().info("Url: " + self.bio_url)
        InstaLogger.logger().info("Posts: " + str(self.num_of_posts))
        InstaLogger.logger().info("Follower: " + str(self.followers['count']))
        InstaLogger.logger().info("Following: " + str(self.following))
        InstaLogger.logger().info("Is private: " + str(self.isprivate))

    def to_dict(self):
        output = {}
        output['username'] = self.username
        output['num_of_posts'] = self.num_of_posts
        output['followers'] = self.followers
        output['following'] = self.following
        output['profile_image'] =self.profile_image
        output['bio'] = self.bio
        output['bio_url'] = self.bio_url
        output['alias'] = self.alias
        output['isprivate'] = self.isprivate
        output['posts'] = self.posts
        output['scraped'] = self.scraped
        return output


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


def extract_followers(browser, username):
    InstaLogger.logger().info('Extracting follower from ' + username)
    try:
        user_link = "https://www.instagram.com/{}".format(username)
        web_adress_navigator(browser, user_link)
    except PageNotFound404 as e:
        raise NoInstaProfilePageFound(e)
    sleep(5)

    followers = []

    # find number of followers
    elem = browser.find_element_by_xpath(
        "//span[@id='react-root']//header[@class='vtbgv ']//ul[@class='k9GMp ']/child::li[2]/a/span")
    elem.click()
    sleep(15)

    # remove suggestion list and load 24 list elements after this
    browser.execute_script("document.getElementsByClassName('isgrP')[0].scrollTo(0,500)")
    sleep(10)

    elems = browser.find_elements_by_xpath("//body//div[@class='PZuss']//a[@class='FPmhX notranslate _0imsa ']")
    for i in range(12):
        val = elems[i].get_attribute('innerHTML')
        followers.append(val)

    for i in range(12):
        browser.execute_script("document.getElementsByClassName('PZuss')[0].children[0].remove()")

    isDone = False

    while 1:
        try:

            start = time()
            browser.execute_script(
                "document.getElementsByClassName('isgrP')[0].scrollTo(0,document.getElementsByClassName('isgrP')[0].scrollHeight)")

            while 1:
                try:
                    if int(browser.execute_script(
                            "return document.getElementsByClassName('PZuss')[0].children.length")) == 24:
                        break
                except (KeyboardInterrupt, SystemExit):
                    # f.close()
                    raise
                except:
                    continue
                if time() - start > 10:
                    isDone = True
                    break

            if isDone:
                break

            elems = browser.find_elements_by_xpath("//body//div[@class='PZuss']//a[@class='FPmhX notranslate _0imsa ']")
            list_segment = ""
            for i in range(12):
                val = elems[i].get_attribute('innerHTML')
                list_segment += (val + '\n')
                followers.append(val)

            for i in range(12):
                browser.execute_script("document.getElementsByClassName('PZuss')[0].children[0].remove()")

            InstaLogger.logger().info(time() - start)

        except (KeyboardInterrupt, SystemExit):
            # f.close()
            raise
        except:
            continue

    list_segment = ""
    elems = browser.find_elements_by_xpath("//body//div[@class='PZuss']//a[@class='FPmhX notranslate _0imsa ']")
    for i in range(len(elems)):
        val = elems[i].get_attribute('innerHTML')
        list_segment += (val + '\n')
        followers.append(val)

    return followers


def get_num_posts(browser, num_of_posts_to_do):
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

        InstaLogger.logger().info(f"number of posts to do: {num_of_posts_to_do}")
        num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)
        InstaLogger.logger().info(f"Getting first {num_of_posts_to_scroll} posts but checking {num_of_posts_to_do} posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")
        while (len(links2) < num_of_posts_to_do):

            prev_divs = browser.find_elements_by_tag_name('main')
            links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
            links = sum([[link_elem.get_attribute('href')
                          for link_elem in elems] for elems in links_elems], [])

            for elems in links_elems:
                for link_elem in elems:

                    href = link_elem.get_attribute('href')
                    if "/p/" in href:
                        img = link_elem.find_element_by_tag_name('img')
                        src = img.get_attribute('src')
                        preview_imgs[href] = src

            for link in links:
                if "/p/" in link:
                    if (len(links2) < num_of_posts_to_do):
                        links2.append(link)

            links2 = list(set(links2))
            InstaLogger.logger().info(f"Scrolling profile {len(links2)} / {num_of_posts_to_scroll}")
            body_elem.send_keys(Keys.END)
            sleep(Settings.sleep_time_between_post_scroll)

            ##remove bellow part to never break the scrolling script before reaching the num_of_posts
            if (len(links2) == previouslen):
                breaking += 1
                InstaLogger.logger().info(f"breaking in {4 - breaking}...\nIf you believe this is only caused by slow internet, increase sleep time 'sleep_time_between_post_scroll' in settings.py")
            else:
                breaking = 0
            if breaking > 3:
                InstaLogger.logger().info("Not getting any more posts, ending scrolling")
                sleep(2)
                break
            previouslen = len(links2)
            ##

    except NoSuchElementException as err:
        InstaLogger.logger().error('Something went terribly wrong')

    return links2, preview_imgs


def extract_user_posts(browser, num_of_posts_to_do):
    links2, preview_imgs = get_num_posts(browser, num_of_posts_to_do)

    post_infos = []

    counter = 1
    # into user_commented_total_list I will add all username links who commented on any post of this user
    user_commented_total_list = []

    for postlink in links2:

        InstaLogger.logger().info(f"\n {counter} / {len(links2)}")
        counter = counter + 1

        try:
            instagram_post = InstagramPost(browser, postlink)
            instagram_post.extract_post_info()

            location = {
                'location_url': instagram_post.location_url,
                'location_name': instagram_post.location_name,
                'location_id': instagram_post.location_id,
                'latitude': instagram_post.lat,
                'longitude': instagram_post.lng,
            }

            post_infos.append({
                'caption': instagram_post.caption,
                'location': location,
                'imgs': instagram_post.imgs,
                'imgdesc': instagram_post.imgdesc,
                'preview_img': preview_imgs.get(instagram_post.postlink, None),
                'date': instagram_post.date,
                'tags': instagram_post.tags,
                'likes': {
                    'count': instagram_post.likes,
                    'list': instagram_post.user_liked_list
                },
                'views': instagram_post.views,
                'url': instagram_post.postlink,
                'comments': {
                    'count': instagram_post.commentscount,
                    'list': instagram_post.user_comments
                },
                'mentions': instagram_post.mentions
            })
            user_commented_total_list = user_commented_total_list + instagram_post.user_commented_list
        except NoSuchElementException as err:
            InstaLogger.logger().error("Could not get information from post: " + instagram_post.postlink)
            InstaLogger.logger().error(err)
    return post_infos, user_commented_total_list


def quick_post_extract(browser, num_of_posts_to_do):
    body_elem = browser.find_element_by_tag_name('body')

    previouslen = 0
    breaking = 0

    num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)

    post_infos = []
    posts_set = set()
    posts_set_len = 0

    while (posts_set_len < num_of_posts_to_do):
        print(posts_set_len)

        JSGetPostsFromReact = """
            var feed = document.getElementsByTagName('article')[0];
            var __reactInternalInstanceKey = Object.keys(feed).filter(k=>k.startsWith('__reactInternalInstance'))[0]
            var posts = feed[__reactInternalInstanceKey].return.stateNode.state.combinedPosts
            return posts;
        """
        posts_json = browser.execute_script(JSGetPostsFromReact)

        for post_json in posts_json:
            # TODO: Convert to InstagramPost
            # instagram_post = InstagramPost.from_react_json(post_json)
            post_code = post_json['code']
            if post_code in posts_set:
                continue

            posts_set.add(post_code)

            location = {}
            if post_json.get('location'):
                loc_id = post_json['location']['id']
                loc_slug = post_json['location']['slug']
            
                location = {
                    'location_url': f"https://www.instagram.com/explore/locations/{loc_id}/{loc_slug}/",
                    'location_name': post_json['location']['name'],
                    'location_id': loc_id,
                    'latitude': post_json['location']['lat'],
                    'longitude': post_json['location']['lng'],
                }

            num_comments = post_json['numComments']
            num_likes = post_json.get('numLikes') or post_json.get('numPreviewLikes', -1)

            post_infos.append({
                'caption': post_json['caption'],
                'location': location,
                'imgs': [],
                'imgdesc': [],
                'preview_img': post_json['thumbnailResources'],
                'date': post_json['postedAt'],
                'tags': [],
                'likes': {
                    'count': num_likes,
                    'list': []
                },
                'views': post_json.get('videoViews', -1),
                'url': f"https://www.instagram.com/p/{post_code}/",
                'comments': {
                    'count': num_comments,
                    'list': []
                },
                'mentions': []
            })

        body_elem.send_keys(Keys.END)
        sleep(Settings.sleep_time_between_post_scroll)

        posts_set_len = len(posts_set)
        ##remove below part to never break the scrolling script before reaching the num_of_posts
        if (posts_set_len == previouslen):
            breaking += 1
            InstaLogger.logger().info(f"breaking in {4 - breaking}...\nIf you believe this is only caused by slow internet, increase sleep time 'sleep_time_between_post_scroll' in settings.py")
        else:
            breaking = 0

        if breaking > 3:
            InstaLogger.logger().info("Not getting any more posts, ending scrolling")
            sleep(2)
            break

        previouslen = len(post_infos)

    return post_infos, []


def extract_information(browser, username, limit_amount):
    """Get all the information for the given username"""

    InstaLogger.logger().info('Extracting information from ' + username)
    isprivate = False

    try:
        user_link = "https://www.instagram.com/{}/".format(username)
        web_adress_navigator(browser, user_link)
    except PageNotFound404 as e:
        raise NoInstaProfilePageFound(e)

    num_of_posts_to_do = 999999

    ig_user = InstagramUser(browser, username)
    ig_user.get_user_info()

    if limit_amount < 1:
        limit_amount = 999999

    num_of_posts_to_do = min(limit_amount, ig_user.num_of_posts['count'])


    prev_divs = browser.find_elements_by_class_name('_70iju')

    post_infos = []
    user_commented_total_list = []
    if Settings.scrape_posts_infos is True and isprivate is False:
        post_infos, user_commented_total_list = quick_post_extract(browser, num_of_posts_to_do)

    ig_user.posts = post_infos
    ig_user.scraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    InstaLogger.logger().info("User " + username + " has " + str(len(user_commented_total_list)) + " comments.")

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

    return ig_user, user_commented_list
