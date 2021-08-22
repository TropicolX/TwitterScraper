import csv
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions


def get_tweet_data(card):
    """Extract data from tweet"""
    username = card.find_element_by_xpath('.//span').text
    handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text

    # get postdate & filter out ads
    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return

    # content of tweet
    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    content = comment + responding

    # stats
    reply_count = card.find_element_by_xpath('//div[@data-testid="reply"]').text
    retweet_count = card.find_element_by_xpath('//div[@data-testid="retweet"]').text
    like_count = card.find_element_by_xpath('//div[@data-testid="like"]').text

    single_tweet = (username, handle, postdate, content, reply_count, retweet_count, like_count)
    return single_tweet


# create instance of webdriver
options = EdgeOptions()
options.use_chromium = True
driver = Edge(options=options)

# navigate to login screen and login
driver.get("https://www.twitter.com/login")
driver.implicitly_wait(10)

email = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
email.send_keys("jacobsbusayo@gmail.com")

my_password = "51xelarats%!"
password = driver.find_element_by_xpath('//input[@name="session[password]"]')
password.send_keys(my_password)
password.send_keys(Keys.RETURN)
driver.implicitly_wait(20)

# find search input and search for term
search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
search_input.send_keys('#polynote')
search_input.send_keys(Keys.RETURN)

# navigate to latest section
driver.find_element_by_link_text("Latest").click()

# get all tweets on the page
data = []
tweet_ids = set()
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True

while scrolling:
    cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for card_div in cards[-15:]:
        tweet = get_tweet_data(card_div)
        if tweet:
            tweet_id = "".join(tweet)
            if tweet_id not in tweet_ids:
                data.append(tweet)

    scroll_attempt = 0
    while True:
        # check scroll position
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(15)
        current_position = driver.execute_script("return window.pageYOffset;")
        if current_position == last_position:
            scroll_attempt += 1

            # end of scroll region
            if scroll_attempt >= 3:
                scrolling = False
                break
            else:
                sleep(15)  # attempt to scroll again
        else:
            last_position = current_position
            break

# saving the tweet data
with open("polynotes_tweets.csv", "x", newline="", encoding="utf-8") as f:
    header = ["Username", "Handle", "Timestamp", "Text", "Replies", "Retweets", "Likes"]
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)
