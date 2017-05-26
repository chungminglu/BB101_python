from selenium import webdriver as Browser
from bs4 import BeautifulSoup
import selenium.common.exceptions
import selenium.webdriver.common.alert
from selenium.common.exceptions import WebDriverException
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

def get_friends_list(url_input):  # 連線到某個人讀取他的朋友清單
    success = 0  # checking connection is succeeded or not
    count = 0  # define how many times we have tried to connect
    times_of_trying = 4  # the limited number we want to try
    friends_list = []
    while (success == 0 and count < times_of_trying):  # if not success to connect try few times
        try:
            browser.get(url_input)
            browser.find_elements_by_class_name('_6-6')[2].click()

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
                browser.implicitly_wait(0.8)
                count_for_while += 1

            success = 1  # if succeeded define success connection

            soup = BeautifulSoup(browser.page_source, 'lxml')
            section_friends = soup.select('#collection_wrapper_2356318349')[0].select('div')[0].select('ul')

            #             if count>5 :
            for friends in section_friends:  # find the friends list and save it to friend_list
                for friend in friends.select('li'):
                    if len(friend.select('div > div > div > div > div > div > a')) != 0:
                        if friend.select('div > div > div > div > div > div > a')[0].text == 'FriendFriends':
                            friends_list.append(
                                friend.select('div > div > div > div > div > div > a')[1]['href'].replace(
                                    '?fref=pb&hc_location=friends_tab', ''))

                        else:
                            friends_list.append(
                                friend.select('div > div > div > div > div > div > a')[0]['href'].replace(
                                    '?fref=pb&hc_location=friends_tab', ''))

        except selenium.common.exceptions.ElementNotSelectableException:
            count += 1
            browser.implicitly_wait(0.5)

        except Exception:
            success = 1

        except (AttributeError, IndexError):  # if user does not permit us to see his firends try few times
            count += 1
            browser.implicitly_wait(0.5)
            if count == times_of_trying:
                pass
    return friends_list

def read_frends_csv():
    friendList = []
    with open("./data/new_friends.csv", "r") as file:
        friendList = file.read().split()
    return friendList

def to_frends_csv(friendList):
    with open("./data/new_friends.csv", "w") as file:
        for f in friendList:
            file.write(f + "\n")

def read_friends_progress():
    with open("./data/friends_progress.csv", "r") as file:
        count = int(file.read())
    return count

def save_friends_progress(countLikesCrawling):
    with open("./data/friends_progress.csv", "w") as file:
        file.write(str(countLikesCrawling))

data = "new_data"
if not os.path.exists(data):
    os.makedirs(data)
open_and_login()

try:
    countLikesCrawling = read_friends_progress()  # read progress, if from the first time set it as 0
except (FileNotFoundError, IndexError):
    countLikesCrawling = 1

try:
    friendList = read_frends_csv()
    with open("./data/friendNum.csv", "r") as file:
        friendNum = int(file.read())

except (FileNotFoundError, IndexError):
    friendList = []
    account = input('please enter your account:')
    startURL = 'http://www.facebook.com/'+account
    friendList.append(startURL)
    for each_friend in get_friends_list(startURL):
        friendList.append(each_friend)
    friendNum = len(friendList)+1
    with open("./data/friendNum.csv", "w") as file:
        file.write(str(friendNum))


try:
    for i in range(countLikesCrawling,friendNum):
        each = friendList[i]
        for element in get_friends_list(each):
            if element not in friendList:
                friendList.append(element)
            if len(friendList) % 1000 == 0:
                with open("./data/friends_copy.csv", "w") as file:
                    for f in friendList:
                        file.write(f + "\n")
        countLikesCrawling += 1

except (WebDriverException, KeyboardInterrupt) as e:
    to_frends_csv(friendList)
    save_friends_progress(countLikesCrawling)