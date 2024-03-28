# BI tools Data Collection

This project is for scraping customer stories from BI platforms website.

Here is the list of the BI platforms:
- [Power BI](https://customers.microsoft.com/en-us/search?sq=power%20bi&ff=story_product_categories%26%3EPower%20BI&p=0&so=story_publish_date%20desc) ✅
- [Dash](https://plotly.com/user-stories/) ✅
- [Tableau](https://www.tableau.com/en-gb/solutions/customers) ✅
- [KNIME](https://www.knime.com/customers) ✅
- [QuickSight](https://aws.amazon.com/quicksight/customers/) ✅
- [Looker](https://cloud.google.com/customers#/products=Data_Analytics) ✅
- [Board](https://www.board.com/en/customers)
- [SAP](https://www.sap.com/uk/products/technology-platform/customer-stories.html)
- [Metabase](https://www.metabase.com/case_studies)

## Table of Contents

- [Structure](#Structure)
- [Usage](#usage)
- [Requirements](#Requirements)
- [License](#license)

## Structure

- `tableau_scraper.py`: This script scrapes customer stories from the Tableau website.
- `other_scraper.py`: This script scrapes data from another website. (Replace with actual description)
- `results/`: This directory contains the results of the scrapers.

## Usage

To run a scraper, navigate to the project directory in your terminal and run the Python script for the scraper. For example, to run the Tableau scraper, use the following command:

```bash
python tableau_scraper.py
```

The results will be saved in the results directory.

## Requirements

Python 3
Selenium
BeautifulSoup
Installation

This requirements.txt file lists the libraries your project depends on. To install the required libraries, use the following command:
```bash
pip install -r requirements.txt
```

You will also need to download the appropriate WebDriver for your browser and add it to your system's PATH.

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).