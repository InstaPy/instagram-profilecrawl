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


def get_user_info(browser):
    """Get the basic user info from the profile screen"""

    container = browser.find_element_by_class_name('v9tJq')
    print("ok")
    img_container = browser.find_element_by_class_name('RR-M-')
    infos = container.find_elements_by_class_name('Y8-fY ')
    alias_name = container.find_element_by_class_name('-vDIg') \
        .find_element_by_tag_name('h1').text
    try:
        bio = container.find_element_by_class_name('-vDIg') \
            .find_element_by_tag_name('span').text
    except:
        print("\nBio is empty")
        bio = ""
    try:
        bio_url = container.find_element_by_class_name('yLUwa').text
    except:
        print("\nBio Url is empty")
        bio_url = ""
    print("\nalias name: ", alias_name)
    print("\nbio: ", bio)
    print("\nurl: ", bio_url, "\n")
    prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
    num_of_posts = extract_exact_info(infos[0])
    followers = extract_exact_info(infos[1])
    following = extract_exact_info(infos[2])

    return alias_name, bio, prof_img, num_of_posts, followers, following, bio_url


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


def extract_post_info(browser):
    """Get the information from the current post"""

    post = browser.find_element_by_class_name('ltEKP')

    # Get caption
    caption = ''
    caption_username = ''
    # try:
    username = post.find_element_by_class_name('e1e1d').text
    # print ("username:",username)
    try:
        caption_username = post.find_elements_by_class_name('gElp9')[0].find_element_by_tag_name('a').text
    except:
        pass
        # print ("caption username:",caption_username)
    if username == caption_username:
        caption = post.find_element_by_class_name('Xl2Pu').find_element_by_class_name('gElp9').find_element_by_tag_name(
            'span').text
        print("caption:", caption)
    # except Exception as err:
    #  print (err)

    # Get location details
    location_url = ''
    location_name = ''
    location_id = 0
    lat = ''
    lng = ''
    try:
        # Location url and name
        x = post.find_element_by_class_name('M30cS').find_elements_by_tag_name('a')
        location_url = x[0].get_attribute('href')
        location_name = x[0].text

        # Longitude and latitude
        location_id = location_url.strip('https://www.instagram.com/explore/locations/').split('/')[0]
        url = 'https://www.instagram.com/explore/locations/' + location_id + '/?__a=1'
        response = requests.get(url)
        data = response.json()
        lat = data['graphql']['location']['lat']
        lng = data['graphql']['location']['lng']
    except:
        pass

    # print('BEFORE IMG')

    imgs = post.find_elements_by_tag_name('img')
    img = ''

    # print ("imgs:", imgs)

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

    # if more than 22 comment elements, use the second to see
    # how much comments, else count the li's

    # first element is the text, second either the first comment
    # or the button to display all the comments
    comments = []
    tags = []
    # print ("gonna take date")
    date = post.find_element_by_xpath('//a/time').get_attribute("datetime")
    print("date is ", date)

    user_commented_list = []
    user_comments = []
    try:
        if post.find_elements_by_tag_name('ul'):
            comment_list = post.find_element_by_tag_name('ul')
            comments = comment_list.find_elements_by_tag_name('li')

            if len(comments) > 1:
                # load hidden comments
                while (comments[1].text.lower() == 'load more comments' or comments[1].text.lower().startswith(
                        'view all')):
                    comments[1].find_element_by_tag_name('a').click()
                    comment_list = post.find_element_by_tag_name('ul')
                    comments = comment_list.find_elements_by_tag_name('li')
                # adding who commented into user_commented_list
                for comm in comments:
                    user_commented = comm.find_element_by_tag_name('a').get_attribute("href").split('/')
                    user_commented_list.append(user_commented[3])
                    if (Settings.output_comments is True):
                        try:
                            user_comment = {
                                'user': user_commented[3],
                                'comment': comm.find_element_by_tag_name('span').text
                            }
                            print(user_commented[3] + " -- " + comm.find_element_by_tag_name('span').text)

                            user_comments.append(user_comment)
                        except:
                            pass
                tags = comments[0].text + ' ' + comments[1].text
            else:
                tags = comments[0].text

            tags = findall(r'#[A-Za-z0-9]*', tags)
            print(len(user_commented_list), " comments.")
    except:
        pass

    mentions = []
    mention_list = []
    if (Settings.mentions is True):
        print(len(post.find_elements_by_class_name('xUdfV')), "mentions")
        try:
            if post.find_elements_by_class_name('xUdfV'):  # perhaps JYWcJ
                mention_list = post.find_elements_by_class_name('xUdfV')  # perhaps JYWcJ
                for mention in mention_list:
                    user_mention = mention.get_attribute("href").split('/')
                    # print(user_mention[3])
                    mentions.append(user_mention[3])
        except:
            pass
    return caption, location_url, location_name, location_id, lat, lng, img, tags, int(likes), int(
        len(comments) - 1), date, user_commented_list, user_comments, mentions


def extract_posts(browser, num_of_posts_to_do):
    """Get all posts from user"""
    links = []
    links2 = []

    # list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    # list links2 contains all the links collected so far
    try:
        body_elem = browser.find_element_by_tag_name('body')

        # load_button = body_elem.find_element_by_xpath\
        #  ('//a[contains(@class, "_1cr2e _epyes")]')
        # body_elem.send_keys(Keys.END)
        # sleep(3)

        # load_button.click()

        previouslen = 0
        breaking = 0

        num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)
        print("Getting first", num_of_posts_to_scroll,
              "posts but check ", num_of_posts_to_do,
              " posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")
        while (len(links2) < num_of_posts_to_do):
            links2 = []
            prev_divs = browser.find_elements_by_tag_name('main')
            links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
            links = sum([[link_elem.get_attribute('href')
                          for link_elem in elems] for elems in links_elems], [])
            for link in links:
                if "/p/" in link:
                    #print("links ", len(links2),"/",num_of_posts_to_do)
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
                print("\nNot getting any more posts, ending scrolling.")
                sleep(2)
                break
            previouslen = len(links2)
            ##

    except NoSuchElementException as err:
        print('- Something went terribly wrong\n')

    post_infos = []

    counter = 1
    # into user_commented_total_list I will add all username links who commented on any post of this user
    user_commented_total_list = []

    for link in links2:

        print("\n", counter, "/", len(links2))
        counter = counter + 1

        print("\nScrapping link: ", link)
        web_adress_navigator(browser, link)
        try:
            caption, location_url, location_name, location_id, lat, lng, img, tags, likes, comments, date, user_commented_list, user_comments, mentions = extract_post_info(
                browser)

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
                'date': date,
                'tags': tags,
                'likes': likes,
                'comments': {
                    'count': comments,
                    'list': user_comments
                },
                'mentions': mentions
            })
            user_commented_total_list = user_commented_total_list + user_commented_list
        except NoSuchElementException as err:
            print('- Could not get information from post: ' + link)
            print(err)
    return post_infos, user_commented_total_list


def extract_information(browser, username, limit_amount):
    """Get all the information for the given username"""

    user_link = "https://www.instagram.com/{}/".format(username)
    web_adress_navigator(browser, user_link)
    num_of_posts_to_do = 999999
    try:
        alias_name, bio, prof_img, num_of_posts, followers, following, bio_url \
            = get_user_info(browser)
        if limit_amount < 1:
            limit_amount = 999999
        num_of_posts_to_do = min(limit_amount, num_of_posts)
    except:
        print("\nError: Couldn't get user profile.\nTerminating")
        quit()
    prev_divs = browser.find_elements_by_class_name('_70iju')

    post_infos = []
    user_commented_total_list = []
    if Settings.scrap_posts_infos is True:
        try:
            post_infos, user_commented_total_list = extract_posts(browser, num_of_posts_to_do)
        except:
            pass

    information = {
        'alias': alias_name,
        'username': username,
        'bio': bio,
        'prof_img': prof_img,
        'num_of_posts': num_of_posts,
        'followers': followers,
        'following': following,
        'bio_url': bio_url,
        'scrapped': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'posts': post_infos
    }

    print("\nUser ", username, " has ", len(user_commented_total_list), " comments.")

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
