"""
scraper_board.py

This script is used to scrape customer stories from the Board website.

It uses Selenium for browser automation and BeautifulSoup for parsing HTML.

The script navigates through the customer stories pages, starting from
https://www.board.com/en/customers, and extracts the following data for each story:

- ID: A unique identifier for the story.
- URL: The URL of the story.
- Title: The title of the story.
- Company: The name of the company the story is about.
- Content: The content of the story.

The extracted data is stored in a list of dictionaries, with each dictionary representing a story.

The script uses an ID counter to assign a unique ID to each story. The ID counter is initialized to 1 and is incremented for each story.

The script uses a WebDriver object to control the browser. The WebDriver is initialized to use Chrome.

Functions:
- extract_and_print_data(driver, link): Fetches a webpage, extracts the relevant data, and stores it in a dictionary.
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
import time
from tqdm import tqdm

# Initialize an ID counter
id_counter = 1

# Data storage
all_data = []

base_url = "https://www.board.com/en/customers"
driver = webdriver.Chrome()
driver.get(base_url)

def extract_and_print_data(driver, link):
    """Fetches, extracts, relevant data, and stores it in a JSON object."""
    global id_counter  # Declare id_counter as global
    driver.get(link)

    data = {}
    data['id'] = id_counter
    id_counter += 1
    data['url'] = link
    data['title'] = driver.title

    try:
        company_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img.img-fluid.customer-logo.mb-4.aspect-ratio-none'))
        )
        company_name = company_name_element.get_attribute('title')
        data['company'] = company_name
    except TimeoutException:
        company_name = "Company name not found"

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    content_elements = soup.select('div.content-body, div.node.node-news')
    content = ' '.join([element.text for element in content_elements])
    data['content'] = content
    
    return data

def get_story_links(driver):
    """Fetches all story links on the current page."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.card-list.mt-3 a'))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        story_links = soup.select('ul.card-list.mt-3 a')
        story_links = [link['href'] for link in story_links if link.has_attr('href')]
        return story_links
    except TimeoutException:
        print("No story links found on the page.")
        return []

# Gather all story links
all_story_links = []

# Pagination
for page_index in range(1, 20):  # Start from page 1
    if page_index > 1:  # Skip the base URL which is already loaded
        page_url = f"{base_url}?page={page_index}"
        driver.get(page_url)

    story_links = get_story_links(driver)  # Get links for the new page
    all_story_links.extend(story_links)

    # If there are no stories on the page, finish the scraping
    if not all_story_links:
        print(f"No stories found on page {page_index}. Finishing the scraping.")
        break

for story_link in tqdm(all_story_links, desc="Processing links", unit="link"):
    link = urljoin(base_url, story_link)
    data = extract_and_print_data(driver, link)
    all_data.append(data)


with open('customer_stories_board.json', 'w') as outfile:
    json.dump(all_data, outfile, indent=4)

driver.quit()