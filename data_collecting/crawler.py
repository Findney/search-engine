import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import concurrent.futures

# Function to crawl articles from a single page for a given date
def crawl_articles(date_str, max_pages=10):
    url = f"https://tekno.kompas.com/search/{date_str}"
    page_num = 1
    articles = []
    
    print(f"Starting to crawl articles for {date_str}...")

    while page_num <= max_pages:
        print(f"  - Crawling page {page_num} for {date_str}...")
        try:
            response = requests.get(f"{url}/{page_num}")
            response.raise_for_status()  # Will raise an error for bad responses (e.g., 404 or 500)
        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Failed to fetch page {page_num}: {e}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article links
        article_links = soup.find_all('a', {'class': 'article__link'})
        if not article_links:
            print(f"    [INFO] No articles found on page {page_num}.")
            break
        
        for link in article_links:
            article_url = link['href']
            articles.append({'url': article_url, 'date': date_str})
        
        # Check for pagination (next page)
        next_page = soup.find('a', {'class': 'paging__link--next'})
        if next_page:
            page_num += 1
        else:
            print(f"    [INFO] No next page. Finished crawling for {date_str}.")
            break
        
        time.sleep(1)  # Reduced sleep time between page requests

    return articles

# Function to save only URLs to a text file
def save_urls_to_txt(articles, filename="articles.txt"):
    print(f"[INFO] Saving {len(articles)} URLs to {filename}...")
    try:
        with open(filename, mode='a', encoding='utf-8') as file:
            for article in articles:
                file.write(f"{article['url']}\n")  # Write only the URL to the file
    except Exception as e:
        print(f"[ERROR] Failed to save URLs to {filename}: {e}")

# Function to crawl n months back, from today moving backward day by day
def crawl_n_months_back(n_months):
    today = datetime.today()
    start_date = today - timedelta(days=n_months * 30)
    
    # Loop through each day from the start date to today (backwards)
    date = today
    total_articles = 0

    print(f"Starting crawl for the last {n_months} months, from {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}.")

    articles_to_save = []
    
    # Use ThreadPoolExecutor to crawl articles concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {executor.submit(crawl_articles, date.strftime("%Y-%m-%d")): date for date in (today - timedelta(days=i) for i in range((today - start_date).days + 1))}
        
        for future in concurrent.futures.as_completed(future_to_date):
            date = future_to_date[future]
            try:
                articles = future.result()
                if articles:
                    articles_to_save.extend(articles)
                    total_articles += len(articles)
                print(f"Found {len(articles)} articles for {date.strftime('%Y-%m-%d')}. Total articles so far: {total_articles}")
            except Exception as e:
                print(f"Error processing date {date.strftime('%Y-%m-%d')}: {e}")
    
    # After crawling, save the collected article URLs
    if articles_to_save:
        save_urls_to_txt(articles_to_save, filename="../data/articles.txt")
    print(f"Finished crawling. Total articles found: {total_articles}")

# Example usage: crawl articles for the past 12 months and save to txt
crawl_n_months_back(12)
