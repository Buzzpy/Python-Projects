import asyncio
import os
from urllib.parse import urljoin
import httpx
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import KeyValueStore, Dataset
from apify import Actor
import re # Added import for regular expressions

# Configuration
START_URL = "https://apify.com/store"
# PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # This line is not used in the provided logic

async def main():
    async with Actor:
        # Initialize crawler
        crawler = BeautifulSoupCrawler(
            max_requests_per_crawl=100,
            max_request_retries=2, # Changed to 2 as per your "Then we made some changes" config
        )
        # Open Crawlee's storage
        kv_store = await KeyValueStore.open()
        dataset = await Dataset.open()

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
            context.log.info(f"Processing {context.request.url}")
            soup = context.soup
            image_urls = []

            # Extract image URLs
            for img_tag in soup.find_all("img"):
                img_src = img_tag.get("src")
                if img_src:
                    absolute_url = urljoin(context.request.url, img_src)
                    image_urls.append(absolute_url)

            context.log.info(f"Found {len(image_urls)} images on {context.request.url}")

            # Process images
            for idx, img_url in enumerate(image_urls):
                try:
                    # Retaining the httpx.AsyncClient instantiation within the loop
                    # as it was in your "code that worked" version.
                    async with httpx.AsyncClient() as client:
                        response = await client.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
                        response.raise_for_status()

                    # Get file extension from Content-Type
                    content_type = response.headers.get("Content-Type", "image/jpeg")
                    file_extension = content_type.split("/")[-1].split(";")[0]
                    # Sanitize file extension for Apify Key-Value Store compatibility
                    file_extension = re.sub(r"[^a-zA-Z0-9]", "_", file_extension) # Added sanitization
                    
                    # The key for the Key-Value Store should be flat (no slashes).
                    # The 'images/' prefix will be part of the 'file_key' in the Dataset entry for metadata.
                    file_name_for_kv_store = f"image_{idx}_{context.request.id}.{file_extension}"

                    # Store image in KeyValueStore (using the flat key)
                    await kv_store.set_value(file_name_for_kv_store, response.content, content_type=content_type)

                    # Store metadata in Dataset (where 'file_key' can include the prefix)
                    dataset_entry = {
                        "image_url": img_url,
                        "file_key": f"images/{file_name_for_kv_store}", # file_key now includes "images/" prefix
                        "source_page": context.request.url,
                        "status": "success" # Added status field
                    }
                    context.log.info(f"Pushing data: {dataset_entry}")
                    await dataset.push_data(dataset_entry)

                    context.log.info(f"Processed and Stored: {file_name_for_kv_store}")

                except httpx.HTTPError as e:
                    context.log.error(f"Failed to download {img_url}: {e}")
                    dataset_entry = {
                        "image_url": img_url,
                        "file_key": None, # No file stored on failure
                        "source_page": context.request.url,
                        "status": "failed_download", # Added status field for failed downloads
                        "error": str(e) # Added error details
                    }
                    context.log.info(f"Pushing data: {dataset_entry}")
                    await dataset.push_data(dataset_entry)

        # Run the crawler
        await crawler.run([START_URL])

if __name__ == "__main__":
    asyncio.run(main())
