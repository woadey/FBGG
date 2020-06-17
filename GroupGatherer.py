import time
import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

# Configure ChromeDriver
options = Options()
# options.add_argument("--headless")
# options.add_argument("--blink-settings=imagesEnabled=false")
# options.add_argument("--disable-threaded-compositing")
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
options.add_argument("--disable-threaded-scrolling")
options.add_argument("--disable-webgl")
options.add_argument("--disable-webgl-image-chromium")
options.add_argument("--num-raster-threads=1")
options.add_argument("--disable-logging")
options.add_argument("--incognito")
options.add_argument("--window-size=1024,768")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

# Variables
line_break = "\n-------------------------------------------------------------------------------------------------------"
group_name = "NoGroupNameAcquired"
folder_path = ""
group_folder = ""
url = None
member_count = -1
all_members = []
all_posts = []


class Tab:
    ABOUT = 0
    MEMBERS = 1
    DISCUSSION = 2


def main():
    # Login
    login()

    # Crawl About
    scrape_about()

    # Crawl Members
    scrape_members()

    # Crawl Content
    scrape_discussion()

    # Close Driver
    driver.close()

    # Parse Members
    parse_members()

    # Parse Discussion
    parse_discussion()

    print("COMPLETED ALL TASKS" + line_break)


def login():
    try:
        driver.get("https://facebook.com")
        print("Please login normally through facebook." + line_break)

        # TODO DEV CODE
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


def scrape_about():
    print("Scraping group info...")
    try:
        driver.find_element_by_link_text("About").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to the 'About' tab... " + str(ex)
        )

    global group_name, url, member_count
    url = driver.current_url
    soup = beautify_page()
    headers = soup.select('span._2iem._50f7')
    for head in headers:
        if head.text.find("Members ·") == 0:
            member_count = int(head.text.split()[-1].replace(",", ""))
            break
    group_name = soup.select_one("#leftCol > div >div > div >div > h1 > a").text
    print("GROUP NAME : " + group_name.split('about')[0])
    print("GROUP URL : " + url)
    print("TOTAL MEMBERS : " + str(member_count) + line_break)
    save_html(Tab.ABOUT, soup)


def scrape_members():
    try:
        driver.find_element_by_link_text("Members").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Members' tab... " + str(ex)
        )

    print("Loading all members...")
    scroll(Tab.MEMBERS, 'div.mam> div > a[id][rel="async"]')
    print("Scraping all members...")
    soup = beautify_page()
    print("Saving all data...")
    save_html(Tab.MEMBERS, soup)
    print("COMPLETED" + line_break)


def scrape_discussion():
    try:
        driver.find_element_by_link_text("Discussion").click()
    except Exception as ex:
        raise Exception(
            "Unable to switch to 'Discussion tab... " + str(ex)
        )

    print("Loading all group content...")
    scroll(Tab.DISCUSSION, '#pagelet_group_pager > div > div > div > div[data-testid="fbfeed_placeholder_story"]')
    print("Scraping all group content...")
    soup = beautify_page()
    print("Saving all data...")
    save_html(Tab.DISCUSSION, soup)
    print("COMPLETED" + line_break)


def beautify_page():
    time.sleep(3)
    return BeautifulSoup(driver.page_source, "lxml")


def scroll(tab, loading_selector):
    print("~~SCROLLING~~")
    time.sleep(3)
    while True:
        try:
            if tab is Tab.DISCUSSION:
                view_all()
            wait_to_load(tab)
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            if check_if_bottomed(loading_selector):
                break
        except TimeoutException:
            # Catches bottom in case 'check_if_bottomed()' fails
            print("CHECK_IF_BOTTOMED() FAILED, but this caught it :)")
            break
        except Exception as ex:
            raise Exception(
                "ERROR SCROLLING : " + str(ex).strip()
            )


# TODO might need fixing
def check_if_bottomed(loading_selector):
    flag = 0
    value = False
    while flag < 5:
        try:
            driver.find_element_by_css_selector(loading_selector)
            value = False
            break
        except NoSuchElementException:
            value = True
            flag += 1
        except Exception as ex:
            raise Exception(
                "ERROR CHECKING BOTTOM OF PAGE : " + str(ex)
            )
    print("~~COMPLETED~~")
    return value


def wait_to_load(tab):
    if tab is Tab.MEMBERS:
        try:
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(
                (By.CSS_SELECTOR, 'div.morePager > div > span > img')))
        except TimeoutException:
            # Catches bottom in case 'check_if_bottomed()' fails
            pass
        except Exception as ex:
            raise Exception(
                "ERROR WAITING TO LOAD PAGE : " + str(ex)
            )
    elif tab is Tab.DISCUSSION:
        try:
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(
                (By.CSS_SELECTOR, 'div.async_saving > div[data-testid="fbfeed_placeholder_story"]')))
        except TimeoutException:
            # Catches bottom in case 'check_if_bottomed()' fails
            pass
        except Exception as ex:
            raise Exception(
                "ERROR WAITING TO LOAD PAGE : " + str(ex)
            )


def view_all():
    while True:
        try:
            wait_to_load(Tab.DISCUSSION)
            view_more = driver.find_element_by_css_selector("a._4sxc._42ft")
            driver.execute_script("arguments[0].scrollIntoView(false);", view_more)
            driver.execute_script("window.scrollBy(0,250)")
            view_more.click()
        except StaleElementReferenceException:
            pass
        except NoSuchElementException:
            # print("Completed Expanding")
            break
        except Exception as ex:
            raise Exception(
                "Error Expanding Comments : " + str(ex).strip()
            )


def question_prompt(question):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    answer = input(question)
    if answer in yes:
        print(line_break.strip())
        return
    elif answer in no:
        print("Please make necessary changes to ensure a 'Yes' answer.")
        question_prompt(question)
    else:
        print("Please respond with a 'Yes' or 'No'.")
        question_prompt(question)


def save_html(tab, soup):
    if tab == Tab.ABOUT:
        file_name = "AboutPage.html"
    elif tab == Tab.MEMBERS:
        file_name = "MembersPage.html"
    else:
        file_name = "DiscussionPage.html"

    global group_name, folder_path, group_folder
    current_dir = os.getcwd()
    output_folder = current_dir + "\\Output\\"
    os.makedirs(os.path.dirname(output_folder), exist_ok=True)
    group_folder = output_folder + f"{group_name}\\"
    os.makedirs(os.path.dirname(group_folder), exist_ok=True)
    folder_path = group_folder + "Page Content\\"
    os.makedirs(os.path.dirname(folder_path), exist_ok=True)

    file_path = folder_path + file_name
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(str(soup))


def open_html(tab):
    if tab == Tab.ABOUT:
        file_name = "AboutPage.html"
    elif tab == Tab.MEMBERS:
        file_name = "MembersPage.html"
    else:
        file_name = "DiscussionPage.html"

    global folder_path
    with open(folder_path + file_name, "r", encoding='utf-8') as file:
        contents = file.read()
        return BeautifulSoup(contents, 'lxml')


def parse_members():
    page = open_html(Tab.MEMBERS)
    mem_container = page.select_one("#groupsMemberSection_all_members") or page.select_one(
        "#groupsMemberSection_recently_joined")
    members_list = mem_container.select("div[class='clearfix _60rh _gse']")
    print("MEMBERS SCRAPED : " + str(len(members_list)))

    for mem in members_list:
        try:
            try:
                mem_name = mem.select_one("._60ri > a").get('title') or mem.select_one("._60ri > a").text
            except AttributeError:
                mem_name = None
            try:
                mem_url = mem.select_one("._60ri > a").get('href')
            except AttributeError:
                mem_url = None
            try:
                mem_type = mem.select_one("a[href*='badge_type=']").text
            except AttributeError:
                mem_type = "Member"
            member = {
                'MEMBER_NAME': mem_name,
                'MEMBER_URL': mem_url,
                'MEMBER_TYPE': mem_type
            }
            global all_members
            all_members.append(member)
        except Exception as ex:
            raise Exception(
                "ERROR ADDING MEMBER : " + str(ex)
            )
    save_csv(Tab.MEMBERS)


def parse_discussion():
    page = open_html(Tab.DISCUSSION)
    posts_list = page.select('div[id*="mall_post"]')
    print("POSTS SCRAPED : " + str(len(posts_list)))

    for post in posts_list:
        try:
            try:
                poster = post.select_one('.fwb > a[title]').get('title') or post.select_one('.fwb > a').text
            except AttributeError:
                poster = None
            try:
                post_url = f"https://www.facebook.com{post.select_one('._5pcq').get('href')}"
            except AttributeError:
                post_url = None
            try:
                post_content = post.select_one('div[data-testid="post_message"]').text
            except AttributeError:
                post_content = None
            try:
                post_link = post.select_one('._6ks > a').get('href')
            except AttributeError:
                post_link = None
            try:
                post_time = post.select_one('abbr._5ptz').get('title')
            except AttributeError:
                post_time = None
            try:
                post_img = post.select_one('img[class="scaledImageFitWidth img"]').get('src')
            except AttributeError:
                post_img = None

            all_comments = []
            for com in post.select('div[aria-label*="Comment"]'):
                try:
                    commenter = com.select_one('._6qw4').text
                except AttributeError:
                    commenter = None
                try:
                    comment_content = com.select_one('._3l3x').text
                except AttributeError:
                    comment_content = None
                try:
                    comment_link = com.select_one('_ns_').get('href')
                except AttributeError:
                    comment_link = None
                try:
                    comment_img = com.select_one('_2txe').get('src')
                except AttributeError:
                    comment_img = None
                try:
                    comment_likes = com.select_one('_1lld').text
                except AttributeError:
                    comment_likes = None
                try:
                    comment_time = com.select_one('._6qw7 > abbr').get('data-tooltip-content')
                except AttributeError:
                    comment_time = None
                comment = {
                    'COMMENTER': commenter,
                    'COMMENT_CONTENT': comment_content,
                    'COMMENT_LINK': comment_link,
                    'COMMENT_IMG': comment_img,
                    'COMMENT_LIKES': comment_likes,
                    'COMMENT_TIME': comment_time
                }
                all_comments.append(comment)
            # TODO add post_likes and post_shares
            post = {
                'POSTER': poster,
                'POST_URL': post_url,
                'POST_CONTENT': post_content,
                'POST_LINK': post_link,
                'POST_TIME': post_time,
                'POST_IMG': post_img,
                'POST_LIKES': None,
                'POST_SHARES': None,
                'POST_COMMENTS': all_comments
            }
            all_posts.append(post)

        except Exception as ex:
            raise Exception(
                "ERROR ADDING POST : " + str(ex)
            )
    save_csv(Tab.DISCUSSION)


def save_csv(tab):
    print("Saving all data..." + line_break)
    if tab == Tab.ABOUT:
        file_name = "AboutPage.csv"
    elif tab == Tab.MEMBERS:
        file_name = "MembersPage.csv"
    else:
        file_name = "DiscussionPage.csv"

    global all_members, group_folder
    keys = None
    rows = None
    try:
        if tab == Tab.MEMBERS:
            keys = all_members[0].keys()
            rows = all_members
        elif tab == Tab.DISCUSSION:
            keys = all_posts[0].keys()
            rows = all_posts
        spreadsheet_folder = group_folder + "Spreadsheets\\"
        os.makedirs(os.path.dirname(spreadsheet_folder), exist_ok=True)
        with open(spreadsheet_folder + file_name, 'w', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(rows)
    except Exception as ex:
        raise Exception(
            "ERROR SAVING SPREADSHEETS : " + str(ex)
        )


if __name__ == "__main__":
    main()
