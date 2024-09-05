import httpx
from bs4 import BeautifulSoup
import apify
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

async def fetch_properties(url, headers):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch the HTML content. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        properties = []
        property_cards = soup.find_all('li', class_='ListItem-c11n-8-102-0__sc-13rwu5a-0')
        # Extracting relevant info
        for card in property_cards:
            obj = {}
            try:
                obj["Address"] = card.find('address', {'data-test': 'property-card-addr'}).text.strip()
            except AttributeError:
                obj["Address"] = None

            try:
                obj["Price"] = card.find('span', {'data-test': 'property-card-price'}).text.strip()
            except AttributeError:
                obj["Price"] = None

            try:
                details = card.find('ul', class_='StyledPropertyCardHomeDetailsList-c11n-8-102-0__sc-1j0som5-0 exCsDV')
                # Splitting data in the list
                details_list = details.find_all('li') if details else []
                obj["Bds"] = details_list[0].text.strip() if len(details_list) > 0 else None
                obj["Baths"] = details_list[1].text.strip() if len(details_list) > 1 else None
                obj["Sqft"] = details_list[2].text.strip() if len(details_list) > 2 else None
            except AttributeError:
                obj["Bds"] = obj["Baths"] = obj["Sqft"] = None

            properties.append(obj)

        return properties

async def main():
    async with apify.Actor:
        input = await apify.Actor.get_input() or {}
        base_url = input.get('url', 'https://www.zillow.com/new-york-ny/')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "upgrade-insecure-requests": "1"
        }

        all_properties = []
        page_number = 1

        while len(all_properties) < 20:
            url = f"{base_url}?page={page_number}"
            logging.info(f"Fetching page {page_number}...")
            properties = await fetch_properties(url, headers)

            if not properties:
                logging.info("No more properties found or unable to fetch page.")
                break

            # Filter out invalid entries
            valid_properties = [p for p in properties if
                                p["Address"] and p["Price"] and p["Bds"] and p["Baths"] and p["Sqft"] and 'None' not in (
                                p["Address"], p["Price"], p["Bds"], p["Baths"], p["Sqft"])]

            all_properties.extend(valid_properties)
            if len(all_properties) >= 20:
                break

            page_number += 1
            await asyncio.sleep(2)  # Sleeping to avoid hitting the server too hard

        # Ensuring we have exactly 20 non-empty listings
        all_properties = all_properties[:20]

        # Save to Apify key-value store
        await apify.Actor.push_data(all_properties)

        logging.info("Scraping completed and data saved to Apify key-value store.")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
