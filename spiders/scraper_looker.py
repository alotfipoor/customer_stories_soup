"""
looker_scraper.py

This script is used to scrape data from a specific URL and store the relevant data in a JSON object.

Dependencies:
- BeautifulSoup: For parsing HTML and extracting the data.
- json: For creating JSON objects.
- urllib: For URL parsing and decoding.
- selenium: For automating web browser interaction.

Global Variables:
- id_counter: A counter for assigning unique IDs to each data object.
- all_data: A list to store all the data objects.
- base_url: The URL from which the data is to be scraped.

Functions:
- extract_and_print_data(driver, link): Fetches, extracts, and stores relevant data from a given link.

Workflow:
- The script first initializes a webdriver and opens the base_url.
- It then dismisses any cookie notification on the webpage.
- The function extract_and_print_data is defined, which opens a given link, extracts the relevant data, and stores it in a JSON object.
"""

from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, unquote
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Initialize an ID counter
id_counter = 1

# Data storage
all_data = []

base_url = "https://cloud.google.com/customers#/products=Data_Analytics"
driver = webdriver.Chrome()
driver.get(base_url)

# Dismiss the cookie notification (if present)
try:
    cookie_notification_dismiss_button_selector = 'button.glue-cookie-notification-bar__reject'
    cookie_notification_dismiss_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_notification_dismiss_button_selector))
    )
    cookie_notification_dismiss_button.click()
except TimeoutException:
    pass  # No cookie notification found

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

    # Extract company name from the URL
    path = urlparse(link).path
    data['company'] = unquote(path.split('/')[-2]).replace('-', ' ')

    content_section = soup.select_one('.story-content-block')
    if content_section:
        # Preserve formatting, get HTML content as a string
        data['content'] = content_section.prettify() 
    else:
        data['content'] = "Content Unavailable"
    
    return data

def get_story_links(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.cloud-card__footer > a'))
    )
    html = driver.page_source
    with open("output.html", "w") as f:
        f.write(html)
    soup = BeautifulSoup(html, "html.parser")
    story_links = soup.select('div.cloud-card__footer > a')
    return story_links

# story_links = get_story_links(driver)

# for story_link in story_links:
#     link = urljoin(base_url, story_link.get('href'))

#     if 'www.youtube.com' in link or 'youtube.com' in link or 'youtu.be' in link:
#         continue

#     data = extract_and_print_data(driver, link)
#     all_data.append(data)

# Store the original window handle
original_window = driver.current_window_handle

while True:
    story_links = get_story_links(driver)

    for story_link in story_links:
        link = urljoin(base_url, story_link.get('href'))

        if any(x in link for x in ['www.youtube.com', 'youtube.com', 'youtu.be']):
            continue  # Skip YouTube links

        # Open the story link in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(link)

        data = extract_and_print_data(driver, link)
        all_data.append(data)

        # Close the new tab and switch back to the original window
        driver.close()
        driver.switch_to.window(original_window)

    # Find and click the "Next" button
    next_button_selector = '//button[.//span[contains(text(), "Next page")]]'
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_button_selector))
        )
        # driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        next_button.click()
    except TimeoutException:
        print("End of pagination reached.")
        with open('customer_stories.json', 'w') as outfile:
            json.dump(all_data, outfile, indent=4)
        break

with open('customer_stories.json', 'w') as outfile:
    json.dump(all_data, outfile, indent=4)

driver.quit()