import requests
from bs4 import BeautifulSoup
from apify import Actor

async def main():
    async with Actor:
        # Initialize the Apify Actor
        news_items = get_google_news()
        
        # Push each news item into the dataset
        for item in news_items:
            await Actor.push_data(item)

def get_google_news():
    url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?ceid=US:en&oc=3"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    news_items = []
    containers = soup.find_all('div', class_='W8yrY')

    for container in containers:
        try:
            article = container.find('article')
            if not article:
                continue

            headline_elem = article.find('a', class_='gPFEn')
            headline = headline_elem.get_text(strip=True) if headline_elem else 'No headline'

            source_elem = article.find('div', class_='vr1PYe')
            source = source_elem.get_text(strip=True) if source_elem else 'Unknown source'

            relative_link = headline_elem['href'] if headline_elem else ''
            absolute_link = f'https://news.google.com{relative_link.split("?")[0]}' if relative_link else ''

            news_items.append({
                'source': source,
                'headline': headline,
                'link': absolute_link
            })

            if len(news_items) >= 10:
                break

        except Exception as e:
            print(f"Error processing article: {str(e)}")
            continue

    return news_items

if __name__ == "__main__":
    import asyncio
    # For local testing (prints results)
    news = get_google_news()
    for idx, item in enumerate(news, 1):
        print(f"{idx}. {item['source']}: {item['headline']}")
        print(f"   Link: {item['link']}\n")
# Uncomment below for Apify deployment
#asyncio.run(main())
