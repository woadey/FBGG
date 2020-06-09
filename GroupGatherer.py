from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure ChromeDriver
options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
options.add_argument('--disable-notifications')
driver = webdriver.Chrome(options=options)
line_break = "\n-----------------------------------------------------------------------------------------------------------"


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
    driver.get("https://facebook.com")
    print("Please login normally through facebook." + line_break)
    WebDriverWait(driver, 120).until(
        lambda bs: bs.find_element_by_css_selector('a[aria-current="page"]'))
    print("Please navigate to the group you would like to scrape." + line_break)
    WebDriverWait(driver, 120).until(EC.url_contains("groups"))
    ans = False
    while not ans:
        ans = question_prompt("Is this the group you wish to scrape? ")


def calibrate():
    print("Grabbing current url\n")
    current_url = driver.current_url
    print(current_url)


def scrape_members():
    print("Scraping members")


def scrape_group_content():
    print("Scraping group content")


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
        print("Please respond with a 'Yes' or 'No'")
        question_prompt(question)


if __name__ == "__main__":
    main()
