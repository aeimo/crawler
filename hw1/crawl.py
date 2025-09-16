import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import matplotlib.pyplot as plt
import pandas as pd  

crawl_times = [] 
url_count = []  
keyword_counts = [] 
titles_extracted = []  
urls_crawled = 0

base_url = 'https://cc.gatech.edu'
visited_urls = set()

#store titles and URLs for exporting
web_archive = []

def crawl(url, max_pages=1000):
    global urls_crawled, crawl_times
    url_count, titles_extracted

    #return if visited or the max page limit
    if url in visited_urls or len(visited_urls) >= max_pages:
        return

    #mark visited
    visited_urls.add(url)
    urls_crawled += 1
    start_time = time.time()
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return

        #parse page
        soup = BeautifulSoup(response.content, 'html.parser')

        #get crawl time
        crawl_time = time.time() - start_time
        crawl_times.append(crawl_time + crawl_times[-1] if crawl_times else crawl_time)
        url_count.append(urls_crawled)

        #extract and process title(keyword)
        title = process_page(soup)
        word_count = count_title(soup)
        titles_extracted.append(title) 
        if not keyword_counts:
            keyword_counts.append(word_count)
        else:
            keyword_counts.append(keyword_counts[-1] + word_count)
        #store
        web_archive.append({'title': title, 'url': url})

        #recurse
        links = find_links(soup, url)
        for link in links:
            crawl(link, max_pages)
        time.sleep(1) 

    except Exception as e:
        print(f"Error while crawling {url}: {e}")

def find_links(soup, current_url):
    links = []
    for anchor in soup.find_all('a', href=True):
        link = anchor['href']
        full_url = urljoin(current_url, link)

        #add internal links that haven't been visited
        if full_url.startswith(base_url) and full_url not in visited_urls:
            links.append(full_url)
    return links

def count_title(soup):
    title = soup.find('title').get_text()
    word_count = len(title.split())  
    return word_count  

def process_page(soup):
    title = soup.find('title').get_text()
    print(f"Title: {title}")
    return title  

# plots crawl time against number of urls
def url_time():
    plt.figure(figsize=(10, 6))
    plt.plot(crawl_times, url_count, label="Cumulative Time", color="b")  
    plt.xlabel("Total Crawl Time (seconds)")  
    plt.ylabel("Number of URLs Crawled") 
    plt.title("Crawl Speed: Total Time vs URLs Crawled")
    plt.tight_layout()
    plt.show()
    print("\nsucess!")

# plots crawl time and keyword count
def keyword_time():
    plt.figure(figsize=(10, 6))
    plt.plot(crawl_times, keyword_counts, label="Keyword Count vs Crawl Time", color="r")  
    plt.xlabel("Total Crawl Time (seconds)") 
    plt.ylabel("Keyword Count (Number of Titles Extracted)")  
    plt.title("Keyword Count vs Crawl Time")
    plt.tight_layout()
    plt.show()
    print("\nsucess!")

def export_to_excel():
    df = pd.DataFrame(web_archive)
    df.to_excel('web_archive.xlsx', index=False, engine='openpyxl')
    print("\nWeb archive has been successfully exported to 'web_archive.xlsx'.")
    
crawl(base_url)
export_to_excel() 
url_time()
keyword_time()