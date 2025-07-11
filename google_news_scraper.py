import requests
from bs4 import BeautifulSoup

def get_google_news():
    url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?ceid=US:en&oc=3"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    news_items = []

    # Finding all story containers
    containers = soup.find_all('div', class_='W8yrY')

    # Scraping at least 10 headlines
    for container in containers:
        try:
            # Getting the primary article in each container
            article = container.find('article')
            if not article:
                continue

            # Extracting headline
            headline_elem = article.find('a', class_='gPFEn')
            headline = headline_elem.get_text(strip=True) if headline_elem else 'No headline'

            # Extracting source
            source_elem = article.find('div', class_='vr1PYe')
            source = source_elem.get_text(strip=True) if source_elem else 'Unknown source'

            # Extracting and converting the URLs
            relative_link = headline_elem['href'] if headline_elem else ''
            absolute_link = f'<https://news.google.com>{relative_link.split("?")[0]}' if relative_link else ''

            news_items.append({
                'source': source,
                'headline': headline,
                'link': absolute_link
            })

            # Stop if you have 10 items
            if len(news_items) >= 10:
                break

        except Exception as e:
            print(f"Error processing article: {str(e)}")
            continue

    return news_items

# Running and printing the results
if __name__ == "__main__":
    news = get_google_news()
    for idx, item in enumerate(news, 1):
        print(f"{idx}. {item['source']}: {item['headline']}")
        print(f"   Link: {item['link']}\\n")

