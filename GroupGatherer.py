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
    try:
        # Login
        login()

        # Calibrate Scraper
        calibrate()

        # Scrape Members
        scrape_members()

        # Scrape Content
        scrape_group_content()
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


def calibrate():
    print("Scraping group info..." + line_break)
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
    print("Scraping all members..." + line_break)
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
    print("Scraping all group content..." + line_break)
    soup = beautify_page()
    # TODO scrape posts and comments


def beautify_page():
    time.sleep(3)
    return BeautifulSoup(driver.page_source, "html.parser")


# TODO fix stale element reference
def scroll_to_element(loading_selector):
    print("~~SCROLLING~~")
    time.sleep(3)
    while True:
        try:
            WebDriverWait(driver, 10).until(lambda bs: bs.find_element_by_css_selector(loading_selector))
            loader = driver.find_element_by_css_selector(loading_selector)
            driver.execute_script("arguments[0].scrollIntoView();", loader)
        except Exception as ex:
            print("Done Scrolling : " + str(ex))
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
