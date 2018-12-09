<img src="https://s3-eu-central-1.amazonaws.com/centaur-wp/designweek/prod/content/uploads/2016/05/11170038/Instagram_Logo-1002x1003.jpg" width="200" align="right">

# Instagram-Profilecrawl

## Quickly crawl the information (e.g. followers, tags etc...) of an instagram profile. No login required!
Automation Script for crawling information from ones instagram profile.  
Like e.g. the number of posts, followers, and the tags of the the posts

#### Getting started
Just do:
```bash
git clone https://github.com/timgrossmann/instagram-profilecrawl.git
```

It uses selenium and requests to get all the information so install them with:
```bash
pip install -r requirements.txt
```

Install the proper `chromedriver` for your operating system.  Once you (download it)[https://sites.google.com/a/chromium.org/chromedriver/downloads] just drag and drop it into `instagram-profilecrawl/assets` directory.

## Use it!
Now you can start using it following this example:
*keep in mind that entering username and password is optional*
```bash
python3.5 crawl_profile.py username1 username2 ... usernameX
```

**Settings:**
To limit the amount of posts to be analyzed, change variable limit_amount in crawl_profile.py. Default value is 12000.\

####new feature:
**optional login:**\
If you want to access more features(such as private accounts which you followed with yours will be accessible) you must enter your username and password in setting.py but remember its optional.\
here are the steps to do so:
1. Open Settings.py
2. At the button you must see `login_username` & `login_username`
3. Put your information inside the quotation marks
### Run on Raspberry Pi
To run the crawler on Raspberry Pi with Firefox, follow these steps:

1. Install Firefox: `sudo apt-get install firefox-esr`
2. Get the `geckodriver` as [described here](https://github.com/timgrossmann/InstaPy/blob/master/docs/How_to_Raspberry.md#how-to-update-geckodriver-on-raspbian)
3. Install `pyvirtualdisplay`: `sudo pip3 install pyvirtualdisplay`
4. Run the script for RPi: `python3 crawl_profile_pi.py username1 username2 ...`

**Collecting stats:**

If you are interested in collecting and logging stats from a crawled profile, use the `log_stats.py` script *after* runnig `crawl_profile.py` (or `crawl_profile_pi.py`).
For example, on Raspberry Pi run:

1. Run `python3 crawl_profile_pi.py username`
2. Run `python3 log_stats.py -u username` for specific user or `python3 log_stats.py` for all user

This appends the collected profile info to `stats.csv`. Can be useful for monitoring the growth of an Instagram account over time.
The logged stats are: Time, username, total number of followers, following, posts, likes, and comments.
The two commands can simply be triggered using `crontab` (make sure to trigger `log_stats.py` several minutes after `crawl_profile_pi.py`).

**Settings:**

Path to the save the profile jsons:
```python
Settings.profile_location = os.path.join(BASE_DIR, 'profiles')
```
Should the profile json file should get a timestamp
```python
Settings.profile_file_with_timestamp = True
```

Path to the save the commentors:
```python
Settings.profile_commentors_location = os.path.join(BASE_DIR, 'profiles')
```
Should the commentors file should get a timestamp
```python
Settings.profile_commentors_file_with_timestamp = True
```

Scrap & save the posts json
```python
Settings.scrap_posts_infos = True
```
How many (max) post should be scraped
```python
Settings.limit_amount = 12000
```
Should the comments also be saved in json files
```python
Settings.output_comments = False
```
Should the mentions in the post image saved in json files
```python
Settings.mentions = True
```

Time between post scrolling (increase if you got errors)
```python
Settings.sleep_time_between_post_scroll = 1.5
```
Time between comment scrolling (increase if you got errors)
```python
Settings.sleep_time_between_comment_loading = 1.5
```

Output debug messages to Console
```python
Settings.log_output_toconsole = True
```
Path to the logfile
```python
Settings.log_location = os.path.join(BASE_DIR, 'logs')
```
Output debug messages to File
```python
Settings.log_output_tofile = True
```
New logfile for every run
```python
Settings.log_file_per_run = False
```



#### The information will be saved in a JSON-File in ./profiles/{username}.json
> Example of a files data
```
{
  "alias": "Tim Gro\u00dfmann",
  "username": "grossertim",
  "num_of_posts": 127,
  "posts": [
    {
      "caption": "It was a good day",
      "location": {
        "location_url": "https://www.instagram.com/explore/locations/345421482541133/caffe-fernet/",
        "location_name": "Caffe Fernet",
        "location_id": "345421482541133",
        "latitude": 1.2839,
        "longitude": 103.85333
      },
      "img": "https://scontent.cdninstagram.com/t51.2885-15/e15/p640x640/16585292_1355568261161749_3055111083476910080_n.jpg?ig_cache_key=MTQ0ODY3MjA3MTQyMDA3Njg4MA%3D%3D.2",
      "date": "2018-04-26T15:07:32.000Z",
      "tags": ["#fun", "#good", "#goodday", "#goodlife", "#happy", "#goodtime", "#funny", ...],
      "likes": 284,
      "comments": {
        "count": 0,
        "list": [],
       },
     },
     {
      "caption": "Wild Rocket Salad with Japanese Sesame Sauce",
      "location": {
        "location_url": "https://www.instagram.com/explore/locations/318744905241462/junior-kuppanna-restaurant-singapore/",
        "location_name": "Junior Kuppanna Restaurant, Singapore",
        "location_id": "318744905241462",
        "latitude": 1.31011,
        "longitude": 103.85672
      },
      "img": "https://scontent.cdninstagram.com/t51.2885-15/e35/16122741_405776919775271_8171424637851271168_n.jpg?ig_cache_key=MTQ0Nzk0Nzg2NDI2ODc5MTYzNw%3D%3D.2",
      "date": "2018-04-26T15:07:32.000Z",
      "tags": ["#vegan", "#veganfood", "#vegansofig", "#veganfoodporn", "#vegansofig", ...],
      "likes": 206,
      "comments": {
        "count": 1,
        "list": [
          {
            "user": "pastaglueck",
            "comment": "nice veganfood"
           },
         ],
       },
     },
     .
     .
     .
     ],
  "prof_img": "https://scontent.cdninstagram.com/t51.2885-19/s320x320/14564896_1313394225351599_6953533639699202048_a.jpg",
  "followers": 1950,
  "following": 310
}
```

The script also collects usernames of users who commented on the posts and saves it in ./profiles/{username}_commenters.txt file, sorted by comment frequency.

#### With the help of [Wordcloud](https://github.com/amueller/word_cloud) you could do something like that with your used tags
![](http://i65.tinypic.com/2nkrrtg.png)

<hr />

###### Have Fun & Feel Free to report any issues
