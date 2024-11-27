import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
import json
from random import uniform

# Set up logging to capture detailed errors and save logs to a file
log_filename = "log-scrapping.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Display log on console
        logging.FileHandler(log_filename, mode='w', encoding='utf-8')  # Save log to file
    ]
)

# Fungsi untuk membuat ringkasan dari konten artikel
def generate_summary(content, num_sentences=1):
    sentences = content.split('\n')  # Pisahkan berdasarkan baris
    summary = ' '.join(sentences[:num_sentences])
    if len(sentences) > num_sentences:
        summary += "..."
    return summary

async def fetch(session, url, semaphore):
    async with semaphore:  # Batasi koneksi bersamaan
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logging.error(f"Failed to fetch {url}: {e}")
            return None

async def extract_article_data(url, session, semaphore):
    try:
        html_content = await fetch(session, url, semaphore)
        if html_content is None:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracting title
        title_tag = soup.find('h1', {'class': 'read__title'})
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        # Extracting date
        date_tag = soup.find('div', {'class': 'read__time'})
        date = date_tag.get_text(strip=True) if date_tag else 'No date'

        # Extracting image
        image_tag = soup.find('div', {'class': 'photo__wrap'}).find('img') if soup.find('div', {'class': 'photo__wrap'}) else None
        image_url = image_tag['src'] if image_tag else 'No image'

        # Extracting content from read_content class
        content = []
        content_tag = soup.find('div', {'class': 'read__content'})
        if content_tag:
            content_tags = content_tag.find_all(['p', 'ul'])
            for tag in content_tags:
                if tag.name == 'p':
                    em_tag = tag.find('em')
                    if em_tag:
                        unwanted_text_1 = "Dapatkan update berita teknologi dan gadget pilihan setiap hari"
                        unwanted_text_2 = "Anda harus install aplikasi WhatsApp terlebih dulu di ponsel"
                        if unwanted_text_1 in em_tag.get_text() or unwanted_text_2 in em_tag.get_text():
                            continue  # Skip this <p> tag if the unwanted text is in <em>

                if tag.find('a', {'class': 'inner-link-baca-juga'}):
                    continue  # Skip if it contains the inner link

                content.append(tag.get_text(strip=False))  # Do not strip content to keep original formatting

        full_content = '\n'.join(content)

        # Generate the summary for the article
        summary = generate_summary(full_content)

        # Data yang diekstrak
        article_data = {
            'url': url,
            'title': title,
            'date': date,
            'image_url': image_url,
            'content': full_content,
            'summary': summary,
        }

        logging.info(f"Extracted data for: {title}")
        return article_data
    
    except Exception as e:
        logging.error(f"Failed to extract data from {url}: {e}")
        return None

async def extract_data_in_batches(urls, batch_size=100):
    results = []
    failed_urls = []
    semaphore = asyncio.Semaphore(50)  # Batasi maksimal 50 koneksi bersamaan
    timeout = aiohttp.ClientTimeout(total=30)  # Atur waktu timeout

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logging.info(f"Processing batch {i // batch_size + 1} ({len(batch)} URLs)")
            
            tasks = [extract_article_data(url, session, semaphore) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results
            for url, result in zip(batch, batch_results):
                if isinstance(result, Exception) or result is None:
                    logging.error(f"Failed to process URL: {url}")
                    failed_urls.append(url)  # Track failed URLs
                else:
                    results.append(result)

            await asyncio.sleep(uniform(2, 5))  # Delay antar batch

    return results, failed_urls

async def retry_failed_urls(failed_urls):
    logging.info(f"Retrying {len(failed_urls)} failed URLs...")
    results, failed_after_retry = await extract_data_in_batches(failed_urls, batch_size=50)
    logging.info(f"Retry completed. {len(failed_after_retry)} URLs still failed after retry.")
    return results, failed_after_retry

async def save_extracted_data_to_json(articles_data, output_filename="./data/extracted_articles.json"):
    try:
        with open(output_filename, mode='w', encoding='utf-8') as file:
            json.dump(articles_data, file, ensure_ascii=False, indent=4)
        logging.info(f"Extracted data saved to {output_filename}")
    except Exception as e:
        logging.error(f"Failed to save extracted data to {output_filename}: {e}")

# Example usage
import os

async def main():
    try:
        file_path = "../data/articles.txt"
        if not os.path.exists(file_path):
            logging.error(f"The input file '{file_path}' was not found.")
            return  # Hentikan eksekusi jika file tidak ditemukan
        
        with open(file_path, mode='r', encoding='utf-8') as file:
            urls = [url.strip() for url in file.readlines()]

        logging.info(f"Extracting data from {len(urls)} URLs...")
        articles_data, failed_urls = await extract_data_in_batches(urls, batch_size=500)

        # Retry failed URLs
        if failed_urls:
            retry_results, still_failed = await retry_failed_urls(failed_urls)
            articles_data.extend(retry_results)  # Add successful retries to the main data

            # Log remaining failed URLs
            if still_failed:
                with open("./data/failed_urls.txt", mode='w', encoding='utf-8') as file:
                    file.writelines(url + '\n' for url in still_failed)
                logging.warning(f"{len(still_failed)} URLs still failed. Saved to './data/failed_urls.txt'.")

        if articles_data:
            await save_extracted_data_to_json(articles_data, output_filename="../data/extracted_articles.json")

    except FileNotFoundError:
        logging.error("The input file '../data/articles.txt' was not found.")
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")


# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())
