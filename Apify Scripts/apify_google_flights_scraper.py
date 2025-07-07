import asyncio
from apify import Actor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_google_flights(url):
    # --- WebDriver Configuration ---
    Actor.log.info("Configuring WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    # Arguments required for running in Apify's Docker container
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.get(url)

    # --- Wait for Page to Load ---
    try:
        wait = WebDriverWait(driver, 20)
        Actor.log.info("Waiting for flight results to load on the page...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.zISZ5c')))
    except Exception as e:
        Actor.log.error(f"Error waiting for flight results: {e}")
        Actor.log.error("The website's structure may have changed, or the page didn't load.")
        driver.quit()
        return []

    # --- Parse Page Content ---
    Actor.log.info("Parsing page content...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # --- Extract Flight Data ---
    flights_data = []
    flight_elements = soup.select('li.pIav2d')

    if not flight_elements:
        Actor.log.warning("No flight elements were found. The CSS selectors may be outdated.")
        return []

    Actor.log.info(f"Found {len(flight_elements)} flight elements. Extracting data...")
    for flight in flight_elements:
        airline = flight.select_one('div.sSHqwe')
        departure_time = flight.select_one('span[aria-label*="Departure time:"]')
        arrival_time = flight.select_one('span[aria-label*="Arrival time:"]')
        duration = flight.select_one('div.gvkrdb')
        stops = flight.select_one('div.EfT7Ae span')
        price = flight.select_one('div.FpEdX span')

        flights_data.append({
            "airline": airline.get_text(strip=True) if airline else "N/A",
            "departure_time": departure_time.get_text(strip=True) if departure_time else "N/A",
            "arrival_time": arrival_time.get_text(strip=True) if arrival_time else "N/A",
            "duration": duration.get_text(strip=True) if duration else "N/A",
            "stops": stops.get_text(strip=True) if stops else "N/A",
            "price": price.get_text(strip=True) if price else "N/A",
        })

    return flights_data

async def main():
    async with Actor:
        Actor.log.info("Starting flight scraper Actor...")

        # URL is now hardcoded as in the original script
        target_url = "https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI2LTAxLTEyagcIARIDSkZLcgcIARIDU0ZPGh4SCjIwMjYtMDEtMjlqBwgBEgNTRk9yBwgBEgNKRktAAUABSAFwAYIBCwj___________8BmAEB"
        Actor.log.info(f"Target URL is hardcoded to: {target_url}")
# asyncio.to_thread() runs the synchronous scraping function in a separate thread.
        scraped_flights = await asyncio.to_thread(scrape_google_flights, target_url)

        if scraped_flights:
            # Push the results to the Apify Dataset
            await Actor.push_data(scraped_flights)
            Actor.log.info(f"\nSuccessfully scraped and pushed {len(scraped_flights)} flights to the dataset.")
        else:
            Actor.log.warning("Scraping did not return any data.")
