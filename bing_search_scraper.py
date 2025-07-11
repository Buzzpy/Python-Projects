import requests
from bs4 import BeautifulSoup

def scrape_bing(query):
    url = f"https://www.bing.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve search results") # handling errors
        return []

    soup = BeautifulSoup(response.text, "html.parser") # parsing the info
    results = [] # empty list to store data

    for item in soup.find_all("li", class_="b_algo"):
        title = item.find("h2") # extracting the result title
        link = title.find("a")["href"] if title else "" # extracting the link
        results.append((title.text if title else "No title", link))
        # if title is not found, just returns the link with "No title" placeholder
    return results
  

search_results = scrape_bing("apify") # replace your seach query
for title, link in search_results:
    print(f"{title}: {link}")
