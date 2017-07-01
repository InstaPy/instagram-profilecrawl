"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def get_user_info(browser):
  """Get the basic user info from the profile screen"""

  container = browser.find_element_by_class_name('_de9bg')
  img_container = browser.find_element_by_class_name('_o0ohn')

  infos = container.find_elements_by_class_name('_218yx')

  alias_name = container.find_element_by_class_name('_bugdy')\
                        .find_element_by_tag_name('h2').text
  prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
  num_of_posts = int(infos[0].text.split(' ')[0].replace(',', ''))
  followers = infos[1].text.split(' ')[0].replace(',', '').replace('.', '')
  followers = int(followers.replace('k', '00').replace('m', '00000'))
  following = infos[2].text.split(' ')[0].replace(',', '').replace('.', '')
  following = int(following.replace('k', '00'))

  return alias_name, prof_img, num_of_posts, followers, following


def extract_post_info(browser):
  """Get the information from the current post"""

  post = browser.find_element_by_class_name('_tjnr4')

  print('BEFORE IMG')

  imgs = post.find_elements_by_tag_name('img')
  img = ''

  if len(imgs) >= 2:
    img = imgs[1].get_attribute('src')

  likes = post.find_elements_by_tag_name('section')[1]\
            .find_element_by_tag_name('div').text

  likes = likes.split(' ')

  #count the names if there is no number displayed
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
  comment_list = post.find_element_by_tag_name('ul')
  comments = comment_list.find_elements_by_tag_name('li')

  if len(comments) > 1:
    tags = comments[0].text + ' ' + comments[1].text
  else:
    tags = comments[0].text

  tags = findall(r'#[A-Za-z0-9]*', tags)

  if len(comments) < 22:
    comments = len(comments) - 1
  else:
    comments = comments[1].find_element_by_tag_name('span').text
    comments = comments.replace(',', '')

  return img, tags, int(likes), int(comments)


def extract_information(browser, username):
  """Get all the information for the given username"""

  browser.get('https://www.instagram.com/' + username)

  alias_name, prof_img, num_of_posts, followers, following \
    = get_user_info(browser)

  prev_divs = browser.find_elements_by_class_name('_myci9')

  if num_of_posts > 12:
    try:
      body_elem = browser.find_element_by_tag_name('body')

      load_button = body_elem.find_element_by_xpath\
        ('//a[contains(@class, "_8imhp _glz1g")]')
      body_elem.send_keys(Keys.END)
      sleep(1)

      load_button.click()

      body_elem.send_keys(Keys.HOME)
      sleep(1)

      while len(browser.find_elements_by_class_name('_myci9')) > len(prev_divs):
        prev_divs = browser.find_elements_by_class_name('_myci9')
        body_elem.send_keys(Keys.END)
        sleep(1)
        body_elem.send_keys(Keys.HOME)
        sleep(1)

    except NoSuchElementException as err:
      print('- Only few posts\n')

  links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
  links = sum([[link_elem.get_attribute('href')
                for link_elem in elems] for elems in links_elems], [])

  post_infos = []

  for link in links:
    browser.get(link)

    try:
      img, tags, likes, comments = extract_post_info(browser)

      post_infos.append({
        'img': img,
        'tags': tags,
        'likes': likes,
        'comments': comments
      })
    except NoSuchElementException:
      print('- Could not get information from post: ' + link)

  information = {
    'alias': alias_name,
    'username': username,
    'prof_img': prof_img,
    'num_of_posts': num_of_posts,
    'followers': followers,
    'following': following,
    'posts': post_infos
  }

  return information
