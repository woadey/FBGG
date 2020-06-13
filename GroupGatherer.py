import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            lambda bs: bs.find_element_by_css_selector('a[aria-current="page"]'))
        print("Please navigate to the group you would like to scrape." + line_break)
        WebDriverWait(driver, 300).until(EC.url_contains("groups"))
        question_prompt("Is this the group you wish to scrape? ")
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
            "Unable to switch to 'About' tab... " + str(ex)
        )
    global url, member_count
    url = driver.current_url
    temp = driver.find_element_by_css_selector("div > div > div > div > div > h2 > div > span > strong").text
    member_count = int(temp.replace(",", ""))


def scrape_members():
    print("Loading all members...")
    try:
        driver.find_element_by_link_text("Members").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Members' tab... " + str(ex)
        )
    scroll_to_element(
        '#mount_0_0 > div > div > div.rq0escxv.l9j0dhe7.du4w35lb > div.rq0escxv.l9j0dhe7.du4w35lb > div > div > div.j83'
        'agx80.cbu4d94t.d6urw2fd.dp1hu0rb.l9j0dhe7.du4w35lb > div > div.rq0escxv.l9j0dhe7.du4w35lb.j83agx80.cbu4d94t.d2'
        'edcug0.rj1gh0hx.buofh1pr.g5gj957u.hpfvmrgz.dp1hu0rb > div > div > div.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn > di'
        'v > div > div > div > div > div > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div.k4urcfbm '
        '> div.lzcic4wl.afxn4irw.r8dsh44q.ee40wjg4.skuavjfj.ku44ohm1.g6srhlxm.lszeityy.n1l5q3vz.cxmmr5t8.n851cfcs.hcuky'
        'x3x.ue3kfks5.pw54ja7n.uo3d90p7.l82x9zwi.k4urcfbm.p1ueia1e'
    )
    print("Scraping all members...")
    # TODO scrape members names and urls


def scrape_group_content():
    print("Loading all group content...")
    try:
        driver.find_element_by_link_text("Discussion").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Discussion tab... " + str(ex)
        )
    scroll_to_element(
        '#mount_0_0 > div > div > div.rq0escxv.l9j0dhe7.du4w35lb > div.rq0escxv.l9j0dhe7.du4w35lb > div > div > div.j83'
        'agx80.cbu4d94t.d6urw2fd.dp1hu0rb.l9j0dhe7.du4w35lb > div > div.rq0escxv.l9j0dhe7.du4w35lb.j83agx80.cbu4d94t.d2'
        'edcug0.rj1gh0hx.buofh1pr.g5gj957u.hpfvmrgz.dp1hu0rb > div > div > div.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn > di'
        'v > div > div > div.rq0escxv.l9j0dhe7.du4w35lb.qmfd67dx.gile2uim.buofh1pr.g5gj957u.hpfvmrgz.aov4n071.oi9244e8.'
        'bi6gxh9e.h676nmdw.aghb5jc5 > div:nth-child(3) > div.rek2kq2y > div > div:nth-child(2) > div'
    )
    print("Scraping all group content...")
    # TODO scrape posts and comments


def scroll_to_element(selector):
    print("~~SCROLLING~~")
    time.sleep(3)
    while True:
        loader = driver.find_element_by_css_selector(selector)
        if loader is not None:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", loader)
            except Exception as ex:
                raise Exception("Error scrolling : " + str(ex))
        else:
            print("Done Scrolling." + line_break)
            break


def question_prompt(question):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    answer = input(question)
    if answer in yes:
        print(line_break)
        return True
    elif answer in no:
        return False
    else:
        print("Please respond with a 'Yes' or 'No'.")
        question_prompt(question)


if __name__ == "__main__":
    main()
