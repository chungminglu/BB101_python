from selenium import webdriver as Browser #sign in function
from bs4 import BeautifulSoup
import selenium.common.exceptions
import selenium.webdriver.common.alert
from selenium.common.exceptions import WebDriverException
import json
import os
import sys

def open_and_login():
    global browser
    chrome_options = Browser.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    browser = Browser.Chrome(chrome_options=chrome_options)
    url = "https://zh-tw.facebook.com/login/"
    browser.get(url)
    username ='v78203'#input('username:')
    password ='v3034141'#input('password:')
    search_input = browser.find_element_by_xpath('//*[@id="email"]')
    search_input.send_keys(username)
    search_input = browser.find_element_by_xpath('//*[@id="pass"]')
    search_input.send_keys(password)
    browser.find_element_by_xpath('//*[@id="loginbutton"]').click()

def get_likes_list(url_input):  # 連線到某個人抓他按讚的粉絲頁
    success = 0  # checking connection is succeeded or not
    count = 0  # define how many times we have tried to connect
    likes_list = []
    while (success == 0 and count<4) :
        try:
            browser.get(url_input)  # go user's page and find his likes
            browser.find_element_by_link_text('More').click()
            browser.implicitly_wait(0.5)
            browser.find_element_by_link_text('Likes').click()

            soup_for_while = BeautifulSoup(browser.page_source, 'lxml')
            select_condition = soup_for_while.select(
                '#timeline-medley > div > div.mbm._5vf.sectionHeader._4khu > div.uiHeader > div > div > h3')

            count_for_while = 0
            while select_condition == [] and count_for_while < 200:
                browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                soup_for_while = BeautifulSoup(browser.page_source, 'lxml')
                select_condition = soup_for_while.select(
                    '#timeline-medley > div > div.mbm._5vf.sectionHeader._4khu > div.uiHeader > div > div > h3')
                browser.implicitly_wait(0.5)
                count_for_while += 1

            success = 1

            soup = BeautifulSoup(browser.page_source, 'lxml')  # find the likes list and save it to likes_list

            for link in soup.select('#collection_wrapper_2409997254 > div')[0].select(
                    'ul > li > div > div > div > div'):
                each_like = {}
                each_like['like_name'] = link.select('div > div > a')[0].text
                each_like['like_url'] = link.select('div > div > a')[0]['href']
                each_like['like_category'] = link.select('div > div')[1].text
                likes_list.append(each_like)

        except selenium.common.exceptions.ElementNotSelectableException:
            # print(url_input,'\n','user do not permit likes reading','\n','or wrong url')
            success = 1
        except Exception:
            count += 1

    return likes_list

def read_friends_csv(countLikesCrawling):  # read the friends from the file
    i = 0
    with open("./data/new_friends.csv.csv", "r") as file:
        friendList = []
        for line in file:
            if i in range(countLikesCrawling, countLikesCrawling + 100):
                friendList.append(line)
            elif i > countLikesCrawling + 100:
                break
            i += 1
    return friendList

def read_progress_csv():
    with open("./data/progress.csv", "r") as file:
        count = int(file.read())
    return count

def to_likes_csv(likesList):
    with open("./data/likes.csv", "a") as file:
        for f in likesList:
            file.write(f + "\n")

def to_copy_likes_csv(likesList):
    with open("./data/likes_copy.csv", "a") as file:
        for f in likesList:
            file.write(f + "\n")

def save_progress(countLikesCrawling):
    with open("./data/progress.csv", "w") as file:
        file.write(str(countLikesCrawling))



data = "new_data"  # make the data direction if not exist
if not os.path.exists(data):
    os.makedirs(data)

likesList = []
likesList_copy = []

try:
    countLikesCrawling = read_progress_csv()  # read progress, if from the first time set it as 0
except (FileNotFoundError, IndexError):
    countLikesCrawling = 0

try:
    friendList = read_friends_csv(countLikesCrawling)  # from progress read 100 friendslist
except (FileNotFoundError, IndexError):
    print('please check the friends list file')

open_and_login()
try:
    while True:
        for link in friendList:
            data = {'user_url': link, 'user_likes': get_likes_list(link)}
            jdata = json.dumps(data, ensure_ascii=False)
            likesList.append(jdata)
            likesList_copy.append(jdata)
            countLikesCrawling += 1
            printstring = ('now is on number ' + str(countLikesCrawling) + ' crawling')
            sys.stdout.write('\r' + printstring)
            if countLikesCrawling % 50 == 0:
                to_copy_likes_csv(likesList_copy)
                save_progress(countLikesCrawling)
                likesList_copy = []
        friendList = read_friends_csv(countLikesCrawling)

except (WebDriverException, KeyboardInterrupt) as e:
    to_likes_csv(likesList)
    save_progress(countLikesCrawling)

browser.close()

