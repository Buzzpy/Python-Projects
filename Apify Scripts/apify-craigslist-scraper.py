####- Change: Imported asyncio for non-blocking sleep in an async environment.
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

####- Change: Imported the Actor class from the Apify SDK to use platform features.
from apify import Actor

####- Change: Wrapped the entire logic in an async main function, the standard entry point for Apify Actors.
async def main():
    """
    Main function for the Apify Actor.
    """
    ####- Change: Initialized the Actor context manager to enable logging, input, and output.
    async with Actor:
        ####- Change: Replaced print() with Actor.log for platform-integrated logging.
        Actor.log.info('--- Craigslist Job Scraper ---')

        ####- Change: Configuration is now inside the main function. These values are hardcoded as requested.
        base_url = "https://newyork.craigslist.org/search/cps#search=2~thumb~0"
        target_listings_count = 50
        
        Actor.log.info('Initializing Selenium WebDriver...')
        selenium_options = Options()
        selenium_options.add_argument('--headless')
        ####- Change: Added required arguments for running Selenium in Apify's Docker environment.
        selenium_options.add_argument('--no-sandbox')
        selenium_options.add_argument('--disable-dev-shm-usage')
        selenium_options.add_argument('--disable-gpu')
        selenium_options.add_argument('--window-size=1920,1080')
        selenium_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = None
        ####- Change: Removed the `all_listings_data` list and added a counter to track scraped items.
        collected_count = 0
        try:
            ####- Change: Removed webdriver-manager and Service, as Apify's environment provides the driver automatically.
            driver = webdriver.Chrome(options=selenium_options)

            Actor.log.info(f"Fetching listings from: {base_url}")
            driver.get(base_url)

            Actor.log.info("Waiting for page content to load...")
            ####- Change: Replaced time.sleep with asyncio.sleep for asynchronous compatibility.
            await asyncio.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            listings_on_page = soup.find_all('div', class_='cl-search-result')

            if not listings_on_page:
                ####- Change: Replaced print() with Actor.log.warning for leveled logging.
                Actor.log.warning("No listings found. The website structure might have changed.")
            else:
                Actor.log.info(f"Found {len(listings_on_page)} listings. Processing up to {target_listings_count}...")
                for listing_item in listings_on_page:
                    ####- Change: Check against the new counter instead of the length of a list.
                    if collected_count >= target_listings_count:
                        Actor.log.info(f"Collected {collected_count} listings. Target reached.")
                        break

                    # Extract data fields
                    title = 'N/A'
                    post_url = 'N/A'
                    location = 'N/A'
                    date_posted = 'N/A'

                    result_info = listing_item.find('div', class_='result-info')
                    if result_info:
                        title_anchor = result_info.find('a', class_='posting-title')
                        if title_anchor:
                            title = title_anchor.text.strip()
                            if title_anchor.has_attr('href'):
                                post_url = title_anchor['href']

                        title_blob = result_info.find('div', class_='title-blob')
                        if title_blob:
                            location_element = title_blob.find_previous_sibling('div')
                            if location_element:
                                location = location_element.text.strip()

                        meta_div = result_info.find('div', class_='meta')
                        if meta_div:
                            date_span = meta_div.find('span', title=True)
                            if date_span:
                                date_posted = date_span.text.strip()
                    
                    ####- Change: Organized scraped data into a dictionary for structured output.
                    listing_data = {
                        "title": title,
                        "location": location,
                        "date_posted": date_posted,
                        "url": post_url
                    }

                    ####- Change: Replaced appending to a list with pushing data directly to the Apify dataset.
                    await Actor.push_data(listing_data)
                    ####- Change: Incremented the new counter after successfully pushing an item.
                    collected_count += 1
        
        except Exception as e:
            ####- Change: Used Actor.log.exception for rich error logging.
            Actor.log.exception(f"An error occurred during scraping: {e}")
        finally:
            if driver:
                Actor.log.info("Quitting Selenium WebDriver...")
                driver.quit()
        
        Actor.log.info(f"--- Script Finished: Collected {collected_count} listings ---")
