import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from apify import Actor
import asyncio

# Saving current price data to the named key-value store

async def save_current_data(data):
    try:
        store = await Actor.open_key_value_store(name='historical-prices')
        await store.set_value('historical_prices', data)
    except Exception as e:
        Actor.log.error(f"Error saving current data: {e}")


async def main():
    async with Actor:
        print("Starting eBay headphone scraper...")
        Actor.log.info("Starting eBay headphone scraper...")

        actor_input = await Actor.get_input() or {}
        url = actor_input.get('url', 'https://www.ebay.com/b/Headphones/112529/bn_879608')
        max_items = actor_input.get('max_items', 10)
        print(f"Scraping URL: {url}, Max items: {max_items}")
        Actor.log.info(f"Scraping URL: {url}, Max items: {max_items}")

        # Set up Selenium WebDriver with a unique user data directory
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        # Use a temporary directory to avoid user data directory conflicts
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f'--user-data-dir={temp_dir}')

        driver = None

        try:
            driver = webdriver.Chrome(service=service, options=options)
            print("WebDriver initialized successfully.")
            Actor.log.info("WebDriver initialized successfully.")

            # Fetch the page
            print("Fetching page...")
            Actor.log.info("Fetching page...")
            driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Find product items
            product_containers = driver.find_elements(By.CSS_SELECTOR, 'li.brwrvr__item-card.brwrvr__item-card--list')
            print(f"Found {len(product_containers)} product containers.")
            Actor.log.info(f"Found {len(product_containers)} product containers.")

            if not product_containers:
                print("No product containers found. Check CSS selectors or page structure.")
                Actor.log.error("No product containers found. Check CSS selectors or page structure.")
                return

            current_data = {}
            items_found = 0

            for container in product_containers[:max_items]:
                try:
                    name_elem = container.find_elements(By.CSS_SELECTOR, 'h3.textual-display.bsig__title__text')
                    name = name_elem[0].text.strip() if name_elem else "Name not found"

                    price_elem = container.find_elements(By.CSS_SELECTOR, 'span.textual-display.bsig__price.bsig__price--displayprice')
                    price = price_elem[0].text.strip() if price_elem else "Price not found"

                    item = {
                        'name': name,
                        'price': price,
                        'url': url
                    }

                    current_data[name] = price
                    items_found += 1

                    print(f"Item {items_found}: {name} - {price}")
                    Actor.log.info(f"Item {items_found}: {name} - {price}")

                    await Actor.push_data(item)

                except Exception as e:
                    print(f"Error processing item: {e}")
                    Actor.log.error(f"Error processing item: {e}")
                    continue

            # Save current prices to named KVS
            await save_current_data(current_data)

            print(f"Scraping completed. Total items scraped: {items_found}")
            Actor.log.info(f"Scraping completed. Total items scraped: {items_found}")

        except Exception as e:
            print(f"Critical error: {e}")
            Actor.log.error(f"Critical error: {e}")

        finally:
            if driver:
                driver.quit()
                print("WebDriver closed.")
                Actor.log.info("WebDriver closed.")

if __name__ == "__main__":
    asyncio.run(main())
