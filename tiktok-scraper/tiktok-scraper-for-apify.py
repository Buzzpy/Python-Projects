import os
import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import apify

# Initialize the WebDriver using webdriver-manager
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run headless for Apify
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=service, options=options)

# Function to scrape trending videos
def scrape_trending_videos_with_selenium(url):
    driver.get(url)
    time.sleep(5)  # Waiting for the page to load

    videos = []
    scroll_pause_time = 2  # Pausing to allow content to load

    while len(videos) < 50:
        video_description = driver.find_elements(By.CSS_SELECTOR, 'div.tiktok-1anth1x-DivVideoDescription.e1aajktk10')

        for video in video_description[len(videos):]:
            video_data = {}
            description_element = video.find_element(By.XPATH, '..')
            description_text = video.text
            video_data['Description'] = description_text  # Capture description with hashtags

            # Extracting views
            if description_element.find_elements(By.CSS_SELECTOR, 'strong.tiktok-ksk56u-StrongLikes.e1aajktk9'):
                video_data['Views'] = description_element.find_element(By.CSS_SELECTOR, 'strong.tiktok-ksk56u-StrongLikes.e1aajktk9').text
            else:
                video_data['Views'] = 'N/A'

            # Extracting username
            try:
                user_element = description_element.find_element(By.XPATH, '..//a/p[@data-e2e="video-user-name"]')
                video_data['User'] = user_element.text
            except Exception as e:
                video_data['User'] = 'N/A'

            # Extracting likes
            try:
                likes_element = description_element.find_element(By.XPATH, '..//span[contains(@class, "tiktok-10tcisz-SpanLikes") and contains(@class, "e1aajktk13")]')
                video_data['Likes'] = likes_element.text.split()[-1]  # Extract the last part assuming it's the like count
            except Exception as e:
                video_data['Likes'] = 'N/A'

            videos.append(video_data)

            if len(videos) >= 50:
                break

        # Scrolling down to load more videos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Wait for new videos to load

    return videos

# Function to scrape user pages
def scrape_user_page_with_selenium(url):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    user_data = {}

    # Extract follower count
    try:
        follower_count = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]').text
        user_data['Follower Count'] = follower_count
    except Exception as e:
        user_data['Follower Count'] = 'N/A'

    # Extract following count
    try:
        following_count = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="following-count"]').text
        user_data['Following Count'] = following_count
    except Exception as e:
        user_data['Following Count'] = 'N/A'

    # Extract likes count
    try:
        likes_count = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]').text
        user_data['Likes Count'] = likes_count
    except Exception as e:
        user_data['Likes Count'] = 'N/A'

    # Extract bio
    try:
        bio = driver.find_element(By.CSS_SELECTOR, 'h2[data-e2e="user-bio"]').text
        user_data['Bio'] = bio
    except Exception as e:
        user_data['Bio'] = 'N/A'

    # Extract username
    try:
        username = driver.find_element(By.CSS_SELECTOR, 'h1[data-e2e="user-title"]').text
        user_data['Username'] = username
    except Exception as e:
        user_data['Username'] = 'N/A'

    return user_data

async def main():
    # Read input from the key-value store
    input = await apify.get_input()
    trending_videos_url = input.get('trending_videos_url', 'https://www.tiktok.com/channel/trending-now?lang=en')
    user_page_urls = input.get('user_page_urls', [
        'https://www.tiktok.com/@edsheeran',
        'https://www.tiktok.com/@nba',
    ])

    # Scrape data for trending videos
    trending_videos = scrape_trending_videos_with_selenium(trending_videos_url)

    # Save trending videos data to key-value store
    with open('trending_videos_selenium.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(trending_videos[0].keys())  # Write header
        for video in trending_videos:
            writer.writerow(video.values())

    await apify.set_value('trending_videos_selenium.csv', 'trending_videos_selenium.csv')

    # Scrape data for each user page
    user_data_list = []
    for url in user_page_urls:
        user_data = scrape_user_page_with_selenium(url)
        user_data['URL'] = url  # Add URL to the data for reference
        user_data_list.append(user_data)

    # Save user pages data to key-value store
    with open('user_pages_selenium.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header_written = False
        for user_data in user_data_list:
            if not header_written:
                writer.writerow(user_data.keys())  # Write header
                header_written = True
            writer.writerow(user_data.values())

    await apify.set_value('user_pages_selenium.csv', 'user_pages_selenium.csv')

    driver.quit()

await main()
