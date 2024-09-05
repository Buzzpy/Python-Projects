import requests
from bs4 import BeautifulSoup
import logging
from apify_client import ApifyClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def fetch_properties(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch the HTML content. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    properties = []
    property_cards = soup.find_all('li', class_='ListItem-c11n-8-102-0__sc-13rwu5a-0')
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
            details_list = details.find_all('li') if details else []
            obj["Bds"] = details_list[0].text.strip() if len(details_list) > 0 else None
            obj["Baths"] = details_list[1].text.strip() if len(details_list) > 1 else None
            obj["Sqft"] = details_list[2].text.strip() if len(details_list) > 2 else None
        except AttributeError:
            obj["Bds"] = obj["Baths"] = obj["Sqft"] = None

        properties.append(obj)

    return properties

async def main():
    client = ApifyClient('your-apify-token')
    input_data = await client.key_value_store('default').get('input')
    base_url = input_data.get('base_url', 'https://www.zillow.com/new-york-ny/')
    headers = input_data.get('headers', {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "upgrade-insecure-requests": "1"
    })

    request_queue = await client.request_queue('default')
    await request_queue.add_request({'url': base_url})
    
    all_properties = []
    page_number = 1

    while len(all_properties) < 20:
        url = f"{base_url}?page={page_number}"
        logger.info(f"Fetching page {page_number}...")
        properties = fetch_properties(url, headers)

        if not properties:
            logger.info("No more properties found or unable to fetch page.")
            break

        valid_properties = [p for p in properties if
                            p["Address"] and p["Price"] and p["Bds"] and p["Baths"] and p["Sqft"] and 'None' not in (
                            p["Address"], p["Price"], p["Bds"], p["Baths"], p["Sqft"])]

        all_properties.extend(valid_properties)
        if len(all_properties) >= 20:
            break

        page_number += 1
        await asyncio.sleep(2)  # Sleeping to avoid hitting the server too hard

    all_properties = all_properties[:20]

    # Save to Apify Key-Value Store
    await client.key_value_store('default').set('output', all_properties)
    logger.info("Scraping completed and data saved to Apify Key-Value Store.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
