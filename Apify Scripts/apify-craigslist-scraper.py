# CHANGE: Added `asyncio` for asynchronous operations and `Actor` for Apify platform integration.
# Removed `pandas` and `time` as they are replaced by Apify's dataset and asyncio's sleep.
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from apify import Actor

# CHANGE: The entire WebDriver initialization is moved to the global scope.

# CHANGE: Replaced print() with Actor.log for platform-integrated logging.
Actor.log.info('Initializing Selenium WebDriver in global scope...')
selenium_options = Options()
selenium_options.add_argument('--headless')
# CHANGE: Added required arguments for running Selenium inside a Docker container.
selenium_options.add_argument('--no-sandbox')
selenium_options.add_argument('--disable-dev-shm-usage')
selenium_options.add_argument('--disable-gpu')
selenium_options.add_argument('--window-size=1920,1080')
selenium_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# CHANGE: Kept webdriver-manager as it proved to be the most reliable way to get the correct driver.
chrome_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=chrome_service, options=selenium_options)
Actor.log.info('WebDriver initialized successfully.')


# CHANGE: The entire scraping logic is wrapped in an `async def main()` function.
# This is the standard entry point for an Apify Actor.
async def main():
    """
    Main function for the Apify Actor.
    """
    # CHANGE: Logic is wrapped in the `async with Actor:` context manager to use Apify features.
    async with Actor:
        Actor.log.info('--- Craigslist Job Scraper ---')

        # CHANGE: Configuration is now inside the main function scope.
        base_url = "https://newyork.craigslist.org/search/cps#search=2~thumb~0"
        target_listings_count = 50
        
        # CHANGE: Removed `all_listings_data` list and added a simple counter.
        collected_count = 0
        try:
            # CHANGE: The script now uses the globally initialized 'driver' instance.
            Actor.log.info(f"Fetching listings from: {base_url}")
            driver.get(base_url)

            Actor.log.info("Waiting for page content to load...")
            # CHANGE: Replaced `time.sleep()` with the asynchronous `asyncio.sleep()`.
            await asyncio.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            listings_on_page = soup.find_all('div', class_='cl-search-result')

            if not listings_on_page:
                Actor.log.warning("No listings found. The website structure might have changed.")
            else:
                Actor.log.info(f"Found {len(listings_on_page)} listings. Processing up to {target_listings_count}...")
                for listing_item in listings_on_page:
                    # CHANGE: Check against the new counter instead of `len(all_listings_data)`.
                    if collected_count >= target_listings_count:
                        Actor.log.info(f"Collected {collected_count} listings. Target reached.")
                        break

                    # Extract data fields (logic remains the same)
                    title, post_url, location, date_posted = 'N/A', 'N/A', 'N/A', 'N/A'

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
                    
                    # CHANGE: Data is organized into a dictionary for structured output.
                    listing_data = {
                        "title": title,
                        "location": location,
                        "date_posted": date_posted,
                        "url": post_url
                    }

                    # CHANGE: Replaced appending to a list with pushing data directly to the Apify dataset.
                    await Actor.push_data(listing_data)
                    collected_count += 1
        
        except Exception as e:
            # CHANGE: Used Actor.log.exception for rich error logging.
            Actor.log.exception(f"An error occurred during scraping: {e}")
        finally:
            # CHANGE: driver.quit() is now in the finally block of the main async function.
            Actor.log.info("Quitting Selenium WebDriver...")
            driver.quit()
        
        Actor.log.info(f"--- Script Finished: Collected {collected_count} listings ---")

# CHANGE: Removed the pandas DataFrame creation block entirely.
# The Apify dataset is now the primary output.

# CHANGE: Added a standard Python entry point to run the main async function.
if __name__ == "__main__":
    asyncio.run(main())
