import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Starting URL
start_url = "https://yap.deznov.space"

# Keep track of visited pages to avoid repeats
visited = set()

def crawl(url, depth=1):
    if depth > 2 or url in visited:   # limit depth to avoid going too deep
        return
    visited.add(url)
    
    print(f"\nVisiting: {url}")
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract and print the page title
        title = soup.title.string if soup.title else "No title"
        print("Title:", title)

        # Extract and print all links on the page
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        print("Found", len(links), "links")

        # Recursively crawl the first few links
        for link in links[:3]:  # limit to first 3 links to keep it small
            crawl(link, depth + 1)
            
    except Exception as e:
        print("Error:", e)

# Start crawling
crawl(start_url)
