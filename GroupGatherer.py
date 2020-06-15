import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# Configure ChromeDriver
options = Options()
# options.add_argument("--headless")
# options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument("--disable-gpu")
options.add_argument("--disable-notifications")
options.add_argument("--disable-extensions")
options.add_argument("--disable-3d-apis")
options.add_argument("--disable-accelerated-jpeg-decoding")
options.add_argument("--disable-2d-canvas-clip-aa")
options.add_argument("--disable-accelerated-2d-canvas")
options.add_argument("--disable-accelerated-mjpeg-decode")
options.add_argument("--disable-accelerated-video-decode")
options.add_argument("--disable-avfoundation-overlays")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-canvas-aa")
options.add_argument("--disable-checker-imaging")
options.add_argument("--disable-composited-antialiasing")
options.add_argument("--disable-display-color-calibration")
options.add_argument("--disable-display-list-2d-canvas")
options.add_argument("--disable-flash-3d")
options.add_argument("--disable-flash-stage3d")
options.add_argument("--disable-gpu-vsync")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-sync")
# options.add_argument("--disable-threaded-compositing")
options.add_argument("--disable-threaded-scrolling")
options.add_argument("--disable-webgl")
options.add_argument("--disable-webgl-image-chromium")
options.add_argument("--num-raster-threads=1")
options.add_argument("--disable-logging")
# options.add_argument("--incognito")
options.add_argument("--window-size=1024,768")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

# Variables
line_break = "\n-------------------------------------------------------------------------------------------------------"
url = None
member_count = -1
all_members = []
all_posts = []
all_comments = []
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
    try:
        # Login
        login()

        # Crawl About
        crawl_about()

        # Crawl Members
        # member_page = crawl_members()

        # Crawl Content
        discussion_page = crawl_discussion()

        # Scrape Members
        # scrape_members(member_page)

        # Scrape Discussion
        scrape_discussion(discussion_page)
    except Exception as ex:
        raise Exception(
            "Failed scraping : " + str(ex)
        )
    finally:
        # Close Driver
        driver.close()


def login():
    try:
        driver.get("https://facebook.com")
        print("Please login normally through facebook." + line_break)

        # Dev Code
        ###
        driver.maximize_window()
        driver.find_element_by_css_selector("#email").send_keys("sean.smits@gmail.com")
        time.sleep(.5)
        driver.find_element_by_css_selector("#pass").send_keys("4P*bT6PE3Fx23RDU8c2Jd5^pc")
        time.sleep(.5)
        driver.find_element_by_css_selector("#loginbutton").click()
        ###

        WebDriverWait(driver, 300).until(
            lambda bs: bs.find_element_by_css_selector('a[title="Profile"]'))
        print("Login Successful" + line_break)
        print("Please navigate to the group you would like to scrape." + line_break)
        WebDriverWait(driver, 300).until(EC.url_contains("groups"))
        question_prompt("Is this the group you wish to scrape? [y/n] : ")
    except Exception as ex:
        raise Exception(
            "ERROR LOGGING IN : " + str(ex)
        )


def crawl_about():
    print("Scraping group info...")
    try:
        driver.find_element_by_link_text("About").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to the 'About' tab... " + str(ex)
        )

    global url, member_count
    url = driver.current_url
    soup = beautify_page()
    headers = soup.select('span._2iem._50f7')
    for head in headers:
        if head.text.find("Members ·") == 0:
            member_count = int(head.text.split()[-1].replace(",", ""))
            break
    print("GROUP URL : " + url)
    print("TOTAL MEMBERS : " + str(member_count) + line_break)


def crawl_members():
    try:
        driver.find_element_by_link_text("Members").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Members' tab... " + str(ex)
        )

    print("Loading all members...")
    scroll_to_element('div.mam> div > a[id][rel="async"]')
    print("Crawling all members...")
    print("COMPLETED" + line_break)
    return beautify_page()


def scrape_members(page):
    mem_container = page.select_one("#groupsMemberSection_all_members")
    if mem_container is None:
        mem_container = page.select_one("#groupsMemberSection_recently_joined")
    members_list = mem_container.select("div[class='clearfix _60rh _gse']")
    print("MEMBERS SCRAPED : " + str(len(members_list)))
    global member_count
    print("SUCCESS RATE : " + str(int(len(members_list)/member_count*100)) + "%" + line_break)
    for mem in members_list:
        mem_name = mem.select_one("a[ajaxify]").get('title')
        mem_url = mem.select_one("a[ajaxify]").get('href')
        mem_type = mem.select_one("a[ajaxify*='badge_type=']")
        if mem_type is None:
            mem_type = "Member"
        else:
            mem_type = mem_type.text
        member = {
            'MEMBER_NAME': mem_name,
            'MEMBER_URL': mem_url,
            'MEMBER_TYPE': mem_type
        }
        global all_members
        all_members.append(member)


# TODO fix 'view all'
def crawl_discussion():
    try:
        driver.find_element_by_link_text("Discussion").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Discussion tab... " + str(ex)
        )

    print("Loading all group content...")
    scroll_to_element('#pagelet_group_pager > div > div[id*="u_fetchstream_"]')
    print("Scraping all group content...")

    while True:
        try:
            view_more = driver.find_element_by_css_selector("a._4sxc._42ft")
            driver.execute_script("arguments[0].scrollIntoView(true);", view_more)
            view_more.click()
            print("Viewed More")
        except Exception as ex:
            print("Completed Expanding : " + str(ex).strip())
            break
    soup = beautify_page()
    check_posts = soup.select("div[data-testid='post_message']")
    print("POSTS SCRAPED : " + str(len(check_posts)) + line_break)
    return soup


# TODO scrape posts and comments
def scrape_discussion(page):
    pass


def beautify_page():
    time.sleep(3)
    return BeautifulSoup(driver.page_source, "lxml")


def scroll_to_element(loading_selector):
    print("~~SCROLLING~~")
    time.sleep(3)
    while True:
        try:
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, loading_selector)))
        except Exception as ex:
            print("Done Scrolling : " + str(ex).strip())
            break


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
