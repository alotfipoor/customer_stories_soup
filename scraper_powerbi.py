from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, unquote
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
from tqdm import tqdm


# Initialize an ID counter
id_counter = 1

# Data storage
all_data = []

base_url = "https://customers.microsoft.com/en-us/search?sq=&ff=language%26%3EEnglish%26%26story_product_categories%26%3EPower%20BI&p=2&so=story_publish_date%20desc"
driver = webdriver.Chrome()
driver.get(base_url)

def extract_and_print_data(driver, link):
    """Fetches, extracts, relevant data, and stores it in a JSON object."""
    global id_counter  # Declare id_counter as global
    driver.get(link)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    data = {}
    # Add the ID to the data
    data['id'] = id_counter
    id_counter += 1
    data['url'] = link
    data['title'] = soup.select_one('title').text.strip() if soup.select_one('title') else "Title Unavailable"

    try:
        company_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.story-meta > div > a.c-hyperlink'))
        )
        company_name = company_name_element.text
    except TimeoutException:
        company_name = "Company name not found"

    data['company'] = company_name

    try:
        content_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Main Story Content"].col-sm-6'))
        )
        content = content_element.text
    except TimeoutException:
        content = "Content Unavailable"

    data['content'] = content
    
    return data

def get_story_links(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.search-result-container > a.search-result'))
    )
    html = driver.page_source
    with open("output.html", "w") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")
    story_links = soup.select('.search-result-container > a.search-result')
    return story_links

while True:
    try:
        loadMoreButton = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.load-more__button'))
            )
        time.sleep(2)  # pause for content to load
        loadMoreButton.click()
        time.sleep(5)  # pause for content to load
    except Exception as e:
        print(e)
        break

# Pagination
no_change_counter = 0  # Counter for number of times the scroll height doesn't change
while True:  # Continue until there are no more pages
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")  # Get scroll height

        while True:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # Scroll down to bottom
            time.sleep(2)  # Wait to load page

            new_height = driver.execute_script("return document.body.scrollHeight")  # Calculate new scroll height and compare with last scroll height
            if new_height == last_height:
                no_change_counter += 1  # Increment the counter
                if no_change_counter >= 3:  # If the scroll height doesn't change 3 times in a row, break out of the loop
                    break
            else:
                no_change_counter = 0  # Reset the counter if the scroll height changes
            last_height = new_height

            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.load-more__button'))
                )
                ActionChains(driver).move_to_element(show_more_button).perform()  # Scroll to the button
                show_more_button.click()  # Click the button
            except TimeoutException:
                print("No more 'Load More' button. Continuing to scroll.")
                continue

    except TimeoutException:
        print("No more pages. Finishing the scraping.")
        break

    # Get links for the new page
    story_links = get_story_links(driver)
    if driver.current_url != base_url:  # If the current URL is not the base URL, break the loop
        break
    
for story_link in tqdm(story_links, desc="Processing links", unit="link"):
    link = urljoin(base_url, story_link.get('href'))
    data = extract_and_print_data(driver, link)
    all_data.append(data)

with open('customer_stories_powerbi.json', 'w') as outfile:
    json.dump(all_data, outfile, indent=4)

driver.quit()