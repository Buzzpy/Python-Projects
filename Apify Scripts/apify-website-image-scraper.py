import asyncio
import os
from urllib.parse import urljoin
import httpx
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import KeyValueStore, Dataset
from apify import Actor

# Configuration
START_URL = "https://apify.com/store"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

async def main():
    async with Actor:
        # Initialize crawler
        crawler = BeautifulSoupCrawler(
            max_requests_per_crawl=100,
            max_request_retries=0,
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
                    async with httpx.AsyncClient() as client:
                        response = await client.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
                        response.raise_for_status()

                    # Get file extension from Content-Type
                    content_type = response.headers.get("Content-Type", "image/jpeg")
                    file_extension = content_type.split("/")[-1].split(";")[0]
                    file_name = f"image_{idx}_{context.request.id}.{file_extension}"

                    # Store image in KeyValueStore
                    await kv_store.set_value(file_name, response.content, content_type=content_type)

                    # Store metadata in Dataset
                    dataset_entry = {
                        "image_url": img_url,
                        "file_key": f"images/{file_name}",
                        "source_page": context.request.url,
                        "status": "success"
                    }
                    context.log.info(f"Pushing data: {dataset_entry}")
                    await dataset.push_data(dataset_entry)

                    context.log.info(f"Processed: {file_name}")

                except httpx.HTTPError as e:
                    context.log.error(f"Failed to download {img_url}: {e}")
                    dataset_entry = {
                        "image_url": img_url,
                        "file_key": None,
                        "source_page": context.request.url,
                        "status": "failed_download",
                        "error": str(e)
                    }
                    context.log.info(f"Pushing data: {dataset_entry}")
                    await dataset.push_data(dataset_entry)

        # Run the crawler
        await crawler.run([START_URL])

if __name__ == "__main__":
    asyncio.run(main())
