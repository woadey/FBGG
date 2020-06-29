import time
import os
import csv
from collections import OrderedDict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

# Configure ChromeDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--blink-settings=imagesEnabled=false")
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
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

# Variables
line_break = """
--------------------------------------------------------------------------------------------------------------------------"""
group_name = "NoGroupNameAcquired"
folder_path = ""
group_folder = ""
url = ""
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
    print("""
                                ███████╗░█████╗░░█████╗░███████╗██████╗░░█████╗░░█████╗░██╗░░██╗
                                ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██║░██╔╝
                                █████╗░░███████║██║░░╚═╝█████╗░░██████╦╝██║░░██║██║░░██║█████═╝░
                                ██╔══╝░░██╔══██║██║░░██╗██╔══╝░░██╔══██╗██║░░██║██║░░██║██╔═██╗░
                                ██║░░░░░██║░░██║╚█████╔╝███████╗██████╦╝╚█████╔╝╚█████╔╝██║░╚██╗
                                ╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚══════╝╚═════╝░░╚════╝░░╚════╝░╚═╝░░╚═╝
    
    ░██████╗░██████╗░░█████╗░██╗░░░██╗██████╗░░░░░░░░██████╗░░█████╗░████████╗██╗░░██╗███████╗██████╗░███████╗██████╗░
    ██╔════╝░██╔══██╗██╔══██╗██║░░░██║██╔══██╗░░░░░░██╔════╝░██╔══██╗╚══██╔══╝██║░░██║██╔════╝██╔══██╗██╔════╝██╔══██╗
    ██║░░██╗░██████╔╝██║░░██║██║░░░██║██████╔╝█████╗██║░░██╗░███████║░░░██║░░░███████║█████╗░░██████╔╝█████╗░░██████╔╝
    ██║░░╚██╗██╔══██╗██║░░██║██║░░░██║██╔═══╝░╚════╝██║░░╚██╗██╔══██║░░░██║░░░██╔══██║██╔══╝░░██╔══██╗██╔══╝░░██╔══██╗
    ╚██████╔╝██║░░██║╚█████╔╝╚██████╔╝██║░░░░░░░░░░░╚██████╔╝██║░░██║░░░██║░░░██║░░██║███████╗██║░░██║███████╗██║░░██║
    ░╚═════╝░╚═╝░░╚═╝░╚════╝░░╚═════╝░╚═╝░░░░░░░░░░░░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
    
--------------------------------------------------------------------------------------------------------------------------    
--------------------------------------------------------------------------------------------------------------------------    
""")
    question_prompt("Please confirm 2FA is disabled on your account [y/n] : ")
    question_prompt("Please confirm you are using Classic Facebook [y/n] : ")
    email = input("Email or Phone : ")
    password = input("Password : ")
    print("Logging in...")
    print(line_break.strip())
    try:
        driver.get("https://facebook.com")
    except Exception as ex:
        raise Exception(
            "Unable to access 'https://facebook.com'... " + str(ex)
        )

    try:
        driver.find_element_by_css_selector("#email").send_keys(email)
        time.sleep(.5)
        driver.find_element_by_css_selector("#pass").send_keys(password)
        time.sleep(.5)
        driver.find_element_by_css_selector('#loginbutton').click()

        WebDriverWait(driver, 300).until(
            lambda bs: bs.find_element_by_css_selector('a[title="Profile"]'))
        print("Login Successful." + line_break)
    except Exception as ex:
        raise Exception(
            "ERROR LOGGING IN : " + str(ex) + "\n\n Please try again."
        )

    group_url = input("Please enter the group URL you wish to scrape : ")
    print(line_break.strip())
    driver.get(group_url)


def scrape_about():
    print("Scraping group info...")
    try:
        driver.find_element_by_css_selector('a[title="About"]').click()
        global url
        url = driver.current_url.replace("about/", "")
    except Exception as ex:
        raise Exception(
            "Unable to switch to the 'About' tab... " + str(ex)
        )

    global group_name, member_count
    soup = beautify_page()
    headers = soup.select('span._2iem._50f7')
    for head in headers:
        if head.text.find("Members ·") != -1:
            member_count = int(head.text.split()[-1].replace(",", ""))
            break
    group_name = soup.select_one("#leftCol > div >div > div >div > h1 > a").text
    print("GROUP NAME : " + group_name)
    print("TOTAL MEMBERS : " + str(member_count) + line_break)
    save_html(Tab.ABOUT, soup)


def scrape_members():
    try:
        global url
        driver.get(url + 'members/')
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
        driver.get(url)
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
    return BeautifulSoup(driver.page_source.encode('utf-8'), "lxml")


def scroll(tab, loading_selector):
    print("      ~~SCROLLING~~")
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


def check_if_bottomed(loading_selector):
    try:
        driver.find_element_by_css_selector(loading_selector)
        return False
    except NoSuchElementException:
        print("      ~~COMPLETED~~")
        return True
    except Exception as ex:
        raise Exception(
            "ERROR CHECKING BOTTOM OF PAGE : " + str(ex)
        )


def wait_to_load(tab):
    if tab is Tab.MEMBERS:
        try:
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(
                (By.CSS_SELECTOR, 'div.morePager > div > span > img')))
        except TimeoutException:
            print("Timed-out during 'wait-to-load()'...")
        except Exception as ex:
            raise Exception(
                "ERROR WAITING TO LOAD PAGE : " + str(ex)
            )
    elif tab is Tab.DISCUSSION:
        try:
            WebDriverWait(driver, 30).until(EC.invisibility_of_element(
                (By.CSS_SELECTOR, 'div.async_saving > div[data-testid="fbfeed_placeholder_story"]')))
        except TimeoutException:
            print("Timed-out during 'wait-to-load()'...")
        except Exception as ex:
            raise Exception(
                "ERROR WAITING TO LOAD PAGE : " + str(ex)
            )


def view_all():
    while True:
        try:
            view_more = driver.find_element_by_css_selector("a._4sxc._42ft")
            driver.execute_script("arguments[0].scrollIntoView(false);", view_more)
            driver.execute_script("window.scrollBy(0,250)")
            view_more.click()
            time.sleep(0.1)
        except StaleElementReferenceException:
            print("Stale element during 'view_all()'...")
        except NoSuchElementException:
            # print("Completed Expanding")
            break
        except ElementClickInterceptedException:
            remove_hover = driver.find_element_by_css_selector("._3mf5._3mg0")
            driver.execute_script("arguments[0].scrollIntoView(false);", remove_hover)
            driver.execute_script("window.scrollBy(0,100)")
            remove_hover.click()
            print("Element Click is Intercepted...")
            time.sleep(5)
        except Exception as ex:
            raise Exception(
                "Error Expanding Comments : " + str(ex).strip()
            )


def question_prompt(question):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    answer = input(question)
    if answer.lower() in yes:
        print(line_break.strip())
        return
    elif answer.lower() in no:
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
                poster = post.select_one('.fwb > a').text
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
            try:
                reacts = post.select('._1n9l')
                post_reactions = 0
                for react in reacts:
                    post_reactions += int(react.get('aria-label').split()[0])
            except AttributeError:
                post_reactions = 0
            try:
                post_shares = int(post.select_one('._3rwx._42ft').text.split()[0])
            except AttributeError:
                post_shares = 0

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
                    'Comment': comment_content,
                    'By': commenter,
                    'Likes': comment_likes,
                    'Time': comment_time,
                    'Link': comment_link,
                    'Image': comment_img
                }
                all_comments.append(comment)

            post = OrderedDict()
            post['POSTER'] = poster
            post['POST_URL'] = post_url
            post['POST_LINK'] = post_link
            post['POST_IMG'] = post_img
            post['POST_TIME'] = post_time
            post['POST_REACTIONS'] = post_reactions
            post['POST_SHARES'] = post_shares
            post['POST_CONTENT'] = post_content
            post['POST_COMMENTS'] = all_comments
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
    try:
        spreadsheet_folder = group_folder + "Spreadsheets\\"
        os.makedirs(os.path.dirname(spreadsheet_folder), exist_ok=True)
        with open(spreadsheet_folder + file_name, 'w', encoding='utf-8') as output_file:
            if tab == Tab.MEMBERS:
                dict_writer = csv.DictWriter(output_file, all_members[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(all_members)
            elif tab == Tab.DISCUSSION:
                writer = csv.writer(output_file)
                writer.writerow(all_posts[0].keys())
                for post in all_posts:
                    formatted_row = []
                    for key, value in post.items():
                        if key != 'POST_COMMENTS':
                            formatted_row.append(value)
                    for comment in post['POST_COMMENTS']:
                        formatted_row.append(comment)
                    writer.writerow(formatted_row)
    except Exception as ex:
        raise Exception(
            "ERROR SAVING SPREADSHEETS : " + str(ex)
        )


if __name__ == "__main__":
    main()
