"""
qlik_scraper.py

This script is used to scrape customer stories from the Qlik website.

It uses Selenium for browser automation and BeautifulSoup for parsing HTML.

The script navigates through the customer stories pages, starting from
https://www.qlik.com/us/resource-library?page=1&limit=9&resourceType=Customer%20Story, and extracts the following data for each story:

- ID: A unique identifier for the story.
- URL: The URL of the story.
- Title: The title of the story.

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

base_url = "https://www.qlik.com/us/resource-library?page=1&limit=9&resourceType=Customer%20Story"
driver = webdriver.Chrome()
driver.get(base_url)

def extract_and_print_data(driver, link):
    """Fetches, extracts, relevant data, and stores it in a JSON object."""
    global id_counter  # Declare id_counter as global
    driver.get(link)

    data = {}
    data['id'] = "qlik_" + str(id_counter)
    id_counter += 1
    data['url'] = link
    data['title'] = driver.title

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    data['company'] = link.split("/")[-1].replace("-", " ").capitalize()

    content_elements = soup.select('div.rich-text-body p')

    text_to_remove = "Integrate, transform, analyze, and act on data Connect and combine data from hundreds of sources Build a trusted data foundation Take action with AI-powered insight Maximize the value of your data with AI Get the help you need to make your data work harder Integrate, transform, analyze, and act on data Connect and combine data from hundreds of sources Build a trusted data foundation Take action with AI-powered insight Maximize the value of your data with AI Get the help you need to make your data work harder"

    content = ' '.join([element.text for element in content_elements]).replace(text_to_remove, '')
    data['content'] = content
    
    return data

def get_story_links(driver):
    """Fetches all story links on the current page."""
    story_links = []
    try:
        story_links_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.styles-module--resource-media-card--30d74'))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        story_links = [element.get_attribute('href') for element in story_links_elements]
        return story_links
    except TimeoutException:
        print("No story links found on the page.")
        return []


# Gather all story links
all_story_links = []

# Pagination
for page_index in range(1, 21):  # Start from page 1
    if page_index > 1:  # Skip the base URL which is already loaded
        base_url_template = "https://www.qlik.com/us/resource-library?page={}&limit=9&resourceType=Customer%20Story"
        page_url = base_url_template.format(page_index)
        driver.get(page_url)

    story_links = get_story_links(driver)  # Get links for the new page
    all_story_links.extend(story_links)

    # If there are no stories on the page, finish the scraping
    if not all_story_links:
        print(f"No stories found on page {page_index}. Finishing the scraping.")
        break

print(all_story_links)

for story_link in tqdm(all_story_links, desc="Processing links", unit="link"):
    data = extract_and_print_data(driver, story_link)
    all_data.append(data)

with open('customer_stories_qlik.json', 'w') as outfile:
    json.dump(all_data, outfile, indent=4)

driver.quit()