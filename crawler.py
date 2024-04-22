from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pymongo

START = "https://www.cpp.edu/sci/computer-science/"
TARGET = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
TARGET_HEADING = "Permanent Faculty"
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]
collection = db["pages"]

def retrieve_html(url):
    try:
        html = urlopen(url)
        resource_type = html.info().get_content_type()
        if "text/html" in resource_type or "text/shtml" in resource_type:
            html = html.read().decode('utf-8', errors='ignore')
            return html
        else:
            return None
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} - {url}")
        return None
    except URLError as e:
        print(f"Error accessing {url}: {e.reason}")
        return None

    

def store_page(url, html):
    if html:
        collection.insert_one({"url": url, "html": html})

def parse(html, start):
    visited = set()
    bs = BeautifulSoup(html, 'html.parser')

    for link in bs.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(start, href)
        if full_url.startswith(start) and full_url not in visited:
            visited.add(full_url)
    return visited

def crawler_thread(frontier, target, target_heading):
    while not frontier.done():
        url = frontier.next_url()
        html = retrieve_html(url)
        if html:
            store_page(url, html)
            if target in url: 
                print(f"Target page {target} found")
                break
            parsed = parse(html, url)
            for new in parsed:
                frontier.add_url(new)
class Frontier:
    def __init__(self, start):
        self.urls_to_visit = [start]
        self.visited_urls = set()

    def next_url(self):
        return self.urls_to_visit.pop(0)
    def add_url(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)
    def done(self):
        return len(self.urls_to_visit) == 0
    def clear_frontier(self):
        self.urls_to_visit.clear()
        self.visited_urls.clear()

if __name__ == "__main__":
    frontier = Frontier(START)
    crawler_thread(frontier, TARGET, TARGET_HEADING)
    


