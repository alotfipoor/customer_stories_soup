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

base_url = "https://www.knime.com/customers"
driver = webdriver.Chrome()
driver.get(base_url)

try:
    accept_cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button-primary'))
    )
    accept_cookies_button.click()
except TimeoutException:
    print("No 'Accept and close' button found.")

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
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.absolute img'))
        )
        company_name = company_name_element.get_attribute('alt')
        data['company'] = company_name
    except TimeoutException:
        company_name = "Company name not found"

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    content_elements = soup.select(r'div.px-6.md\:pl-14.md\:pr-36')
    content = ' '.join([element.text for element in content_elements])
    data['content'] = content
    
    return data

def get_story_links(driver):
    """Fetches all story links on the current page."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[target="_self"]'))
        )
        html = driver.page_source
        with open("output.html", "w") as f:
            f.write(html)
        soup = BeautifulSoup(html, "html.parser")
        story_links = soup.select('a[target="_self"]')
        return story_links
        # return story_link_elements
    except TimeoutException:
        print("No story links found on the current page.")
        return []

while True:  # Continue until there are no more pages
    try:
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gatsby-focus-wrapper"]/div/div[3]/div/div[3]/button'))
        )
        ActionChains(driver).move_to_element(show_more_button).perform()  # Scroll to the button
        time.sleep(2)  # Wait for 2 seconds to let the page load
        show_more_button.click()  # Click the button
    except TimeoutException:
        print("No more 'Load More' button. Finishing the scraping.")
        break

    # Get links for the new page
    story_links = get_story_links(driver)
    if driver.current_url != base_url:  # If the current URL is not the base URL, break the loop
        break
    
for story_link in tqdm(story_links, desc="Processing links", unit="link"):
    link = urljoin(base_url, story_link.get('href'))
    data = extract_and_print_data(driver, link)
    all_data.append(data)

with open('customer_stories_knime.json', 'w') as outfile:
    json.dump(all_data, outfile, indent=4)

driver.quit()