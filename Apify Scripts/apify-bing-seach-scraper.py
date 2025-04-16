import requests
from bs4 import BeautifulSoup
from apify import Actor

def scrape_bing(query):
    url = f"https://www.bing.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve search results")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for item in soup.find_all("li", class_="b_algo"):
        title = item.find("h2")
        link = title.find("a")["href"] if title else ""
        results.append({
            "title": title.text if title else "No title",
            "link": link
        })
    return results

async def main():
    async with Actor:
        # In this version we use a default query; replace with input handling as needed.
        query = "apify"
        search_results = scrape_bing(query)
        for item in search_results:
            await Actor.push_data(item)

if __name__ == "__main__":
    import asyncio

    # For local testing, print the results:
    results = scrape_bing("apify")
    for idx, item in enumerate(results, 1):
        print(f"{idx}. {item['title']}: {item['link']}\n")
    
# Uncomment the following line when deploying to Apify:
# asyncio.run(main())
