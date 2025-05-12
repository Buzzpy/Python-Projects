import asyncio
from urllib.parse import urljoin
import httpx
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import KeyValueStore, Dataset

START_URL = "https://apify.com/store"

async def main():
    crawler = BeautifulSoupCrawler(
        max_requests_per_crawl=100,
        max_request_retries=2,  # Allow retries for failed requests
    )
    kv_store = await KeyValueStore.open()
    dataset = await Dataset.open()

    # Create single httpx client for reuse
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
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
                    response = await client.get(img_url)
                    response.raise_for_status()

                    # Get file extension from Content-Type
                    content_type = response.headers.get("Content-Type", "image/jpeg")
                    file_extension = content_type.split("/")[-1].split(";")[0]
                    file_name = f"image_{idx}_{context.request.id}.{file_extension}"

                    # Store image in KeyValueStore
                    await kv_store.set_value(file_name, response.content, content_type=content_type)
                    context.log.info(f"Stored: {file_name}")

                    # Store metadata in Dataset
                    dataset_entry = {
                        "image_url": img_url,
                        "file_key": file_name,
                        "source_page": context.request.url
                    }
                    await dataset.push_data(dataset_entry)

                except httpx.HTTPError as e:
                    context.log.error(f"Failed to download {img_url}: {e}")

        # Run the crawler
        await crawler.run([START_URL])

if __name__ == "__main__":
    asyncio.run(main())
