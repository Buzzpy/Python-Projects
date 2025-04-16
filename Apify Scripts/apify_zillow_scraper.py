"""This module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from apify import Actor
import httpx
from lxml import html
import asyncio

async def fetch_properties(url, headers):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            Actor.log.error(f"Failed to fetch the HTML content. Status code: {response.status_code}")
            return []

        # Parsing the response content using lxml
        tree = html.fromstring(response.content)

        properties = []
        # Using XPath to select property cards
        property_cards = tree.xpath('//li[contains(@class, "ListItem-c11n-8-105-0")]')

        for card in property_cards:
            obj = {}
            try:
                # Address
                obj["Address"] = card.xpath('.//a/address/text()')[0].strip()
            except IndexError:
                obj["Address"] = None

            try:
                # Price
                obj["Price"] = card.xpath('.//span[@data-test="property-card-price"]/text()')[0].strip()
            except IndexError:
                obj["Price"] = None

            # Extracting and splitting Bds, Baths, and Sqft data
            try:
                details = card.xpath('.//ul[contains(@class, "StyledPropertyCardHomeDetailsList-c11n-8-105-0__sc-1j0som5-0 ldtVy")]')
                if details:
                    details_list = details[0].xpath('.//li/b/text()')
                    obj["Bds"] = details_list[0].strip() if len(details_list) > 0 else None
                    obj["Baths"] = details_list[1].strip() if len(details_list) > 1 else None
                    obj["Sqft"] = details_list[2].strip() if len(details_list) > 2 else None
                else:
                    obj["Bds"] = obj["Baths"] = obj["Sqft"] = None
            except IndexError:
                obj["Bds"] = obj["Baths"] = obj["Sqft"] = None

            properties.append(obj)

        return properties

async def main() -> None:
    """Main entry point for the Apify Actor."""
    async with Actor:
        Actor.log.info('Starting the Zillow scraping actor...')

        base_url = "https://www.zillow.com/new-york-ny/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "upgrade-insecure-requests": "1"
        }

        all_properties = []
        page_number = 1
        properties_to_collect = 20

        while True:
            url = f"{base_url}?page={page_number}"
            Actor.log.info(f"Fetching page {page_number}...")
            properties = await fetch_properties(url, headers)

            if not properties:
                Actor.log.info("No more properties found or unable to fetch page.")
                break

            valid_properties = [p for p in properties if p["Address"] and p["Price"] and p["Bds"] and p["Baths"] and p["Sqft"]]
            all_properties.extend(valid_properties)

            if len(all_properties) >= properties_to_collect:
                break

            page_number += 1
            await asyncio.sleep(2)

        # Log the total number of properties scraped
        Actor.log.info(f"Successfully scraped {len(all_properties)} properties.")

# Running the script
if __name__ == "__main__":
    asyncio.run(main())
