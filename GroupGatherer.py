import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Configure ChromeDriver
options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
options.add_argument('--disable-notifications')
driver = webdriver.Chrome(options=options)

# Variables
line_break = "\n-------------------------------------------------------------------------------------------------------"
url = None
member_count = -1
all_members = []
all_posts = []
all_comments = []
member = {
    'MEMBER_NAME': None,
    'MEMBER_URL': None,
    'MEMBER_TYPE': None
}
post = {
    'POST_ID': None,
    'POST_URL': None,
    'POST_CONTENT': None,
    'POST_TIME': None,
    'POST_IMG': None,
    'POST_LIKES': None,
    'POST_SHARES': None,
    'POST_COMMENTS': all_comments
}
comment = {
    'COMMENT_CONTENT': None,
    'COMMENT_LIKES': None
}


def main():
    # Login
    login()

    # Calibrate Scraper
    calibrate()

    # Scrape Members
    scrape_members()

    # Scrape Content
    scrape_group_content()

    # Close Driver
    driver.close()


def login():
    try:
        driver.get("https://facebook.com")
        print("Please login normally through facebook." + line_break)
        WebDriverWait(driver, 300).until(
            lambda bs: bs.find_element_by_css_selector('a[title="Profile"]'))
        print("Login Successful" + line_break)
        question_prompt("IMPORTANT : Confirm you are using the older version of Facebook [y/n]: ")
        print("Please navigate to the group you would like to scrape." + line_break)
        WebDriverWait(driver, 300).until(EC.url_contains("groups"))
        question_prompt("Is this the group you wish to scrape? [y/n] : ")
    except Exception as ex:
        raise Exception(
            "ERROR LOGGING IN : " + str(ex)
        )


def calibrate():
    print("Scraping group info..." + line_break)
    try:
        driver.find_element_by_link_text("About").click()
        WebDriverWait(driver, 10).until(EC.visibility_of('#pagelet_group_about'))
    except Exception as ex:
        raise Exception(
            "Unable to switch and load the 'About' tab... " + str(ex)
        )
    global url, member_count
    url = driver.current_url
    soup = beautify_page()
    headers = soup.select('span._2iem._50f7')
    for head in headers:
        if head.text.find("Members ·") == 0:
            member_count = int(head.text.split()[-1].replace(",", ""))
            print(member_count)
            break
    print("GROUP URL : " + url)
    print("TOTAL MEMBERS : " + str(member_count))


def scrape_members():
    print("Loading all members...")
    try:
        driver.find_element_by_link_text("Members").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Members' tab... " + str(ex)
        )
    scroll_to_element('div.mam> div > a[id][rel="async"]')
    print("Scraping all members...")
    soup = beautify_page()
    # TODO scrape members names and urls


def scrape_group_content():
    print("Loading all group content...")
    try:
        driver.find_element_by_link_text("Discussion").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Discussion tab... " + str(ex)
        )
    scroll_to_element('#pagelet_group_pager > div > div[id*="u_fetchstream_"]')
    print("Scraping all group content...")
    soup = beautify_page()
    # TODO scrape posts and comments


def beautify_page():
    return BeautifulSoup(driver.page_source, "html.parser")


def scroll_to_element(loading_selector):
    print("~~SCROLLING~~")
    time.sleep(3)
    while True:
        try:
            loader = driver.find_element_by_css_selector(loading_selector)
            driver.execute_script("arguments[0].scrollIntoView();", loader)
            print("scrolled")
            WebDriverWait(driver, 10).until(EC.invisibility_of_element(loader))
        except NoSuchElementException:
            print("Done Scrolling.")
            break
        except Exception as ex:
            raise Exception(
                "Error scrolling to element : " + str(ex)
            )


def question_prompt(question):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    answer = input(question)
    if answer in yes:
        print(line_break)
        return
    elif answer in no:
        print("Please make necessary changes to ensure a 'Yes' answer.")
        question_prompt(question)
    else:
        print("Please respond with a 'Yes' or 'No'.")
        question_prompt(question)


if __name__ == "__main__":
    main()
