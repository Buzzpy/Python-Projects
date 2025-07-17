import asyncio
import csv
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee.storages import Dataset


async def main() -> None:
    # --- Configuration ---
    START_URLS = [
        'https://en.wikipedia.org/wiki/Category:Programming_paradigms',
        'https://en.wikipedia.org/wiki/Vibe_coding',
        'https://en.wikipedia.org/wiki/Vibe_coding'
    ]
    CSV_FILE_NAME = 'scraped_data.csv'
    # -------------------

    crawler = BeautifulSoupCrawler()
    dataset = await Dataset.open()

    # This handler runs for all URLs in the START_URLS list.
    # It checks if a URL is a category or a single article.
    @crawler.router.default_handler
    async def start_handler(context: BeautifulSoupCrawlingContext):
        url = context.request.url

        # If it's a category, find links and label them for the detail_handler.
        if '/wiki/Category:' in url:
            context.log.info(f"Finding links in category page: {url}")
            await context.enqueue_links(selector='#mw-pages a', label='DETAIL')

        # If it's a regular article, call the detail_handler's logic directly.
        else:
            context.log.info(f"Processing single article from start list: {url}")
            await detail_handler(context)

    # This handler ONLY runs for links that were given the 'DETAIL' label.
    @crawler.router.handler('DETAIL')
    async def detail_handler(context: BeautifulSoupCrawlingContext):
        """This function contains the logic to scrape a single article page."""
        context.log.info(f"Extracting data from article: {context.request.url}")
        soup = context.soup

        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return

        # Extract summary
        summary_paragraphs = []
        parser_output = content_div.find('div', class_='mw-parser-output')
        if parser_output:
            for p in parser_output.find_all('p', recursive=False):
                if p.get('class'):
                    break
                summary_paragraphs.append(p.get_text(separator=' ', strip=True))
        summary = '\n\n'.join(summary_paragraphs)

        # Extract categories
        categories = []
        catlinks = soup.find('div', id='catlinks')
        if catlinks:
            for li in catlinks.find_all('li'):
                categories.append(li.get_text(separator=' ', strip=True))

        scraped_data = {
            'title': soup.find('h1', id='firstHeading').get_text(strip=True),
            'url': context.request.url,
            'summary': summary,
            'categories': ', '.join(categories),
        }

        print(scraped_data)
        await dataset.push_data(scraped_data)

    # You can set a limit to prevent scraping too many pages
    crawler.max_requests_per_crawl = 20

    await crawler.run(START_URLS)

    # --- Save all collected data to a single CSV File ---
    print(f"\nCrawl complete. Saving data to {CSV_FILE_NAME}...")

    dataset_items = (await dataset.get_data()).items
    if not dataset_items:
        print("No data was scraped, CSV file will not be created.")
        return

    headers = dataset_items[0].keys()
    with open(CSV_FILE_NAME, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset_items)

    print(f" Save complete. {len(dataset_items)} articles saved to {CSV_FILE_NAME}.")


if __name__ == '__main__':
    asyncio.run(main())
