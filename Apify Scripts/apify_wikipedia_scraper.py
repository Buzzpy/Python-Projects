from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from apify import Actor

async def main() -> None:

    async with Actor:
        Actor.log.info('Starting Actor...')

        actor_input = await Actor.get_input() or {}
        
        start_urls_from_input = actor_input.get('start_urls', [])
        max_pages = actor_input.get('max_pages', 20)

        
        start_urls = [item['url'] for item in start_urls_from_input]

        crawler = BeautifulSoupCrawler()

        # --- Crawler Router Handlers ---

        @crawler.router.default_handler
        async def start_handler(context: BeautifulSoupCrawlingContext):
            url = context.request.url
            if '/wiki/Category:' in url:
                context.log.info(f"Queueing links from category page: {url}")
                await context.enqueue_links(selector='#mw-pages a', label='DETAIL')
            else:
                context.log.info(f"Processing single article from start list: {url}")
                await detail_handler(context)

        @crawler.router.handler('DETAIL')
        async def detail_handler(context: BeautifulSoupCrawlingContext):
            context.log.info(f"Extracting data from: {context.request.url}")
            soup = context.soup

            title = soup.find('h1', id='firstHeading').get_text(strip=True)

            summary_paragraphs = []
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                for p in content_div.find_all('p', recursive=False):
                    if p.get('class'):
                        break
                    summary_paragraphs.append(p.get_text(separator=' ', strip=True))
            summary = '\n\n'.join(summary_paragraphs)

            categories = []
            catlinks = soup.find('div', id='catlinks')
            if catlinks:
             
                category_links = catlinks.select('ul li a')
                categories = [li.get_text(strip=True) for li in category_links]

            scraped_data = {
                'title': title,
                'url': context.request.url,
                'summary': summary,
                'categories': categories,
            }
            
            await Actor.push_data(scraped_data)

        # --- Run the Crawler ---
        crawler.max_requests_per_crawl = max_pages

        Actor.log.info("Starting the crawl...")
        await crawler.run(start_urls)
        Actor.log.info("Crawl finished.")
