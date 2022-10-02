# pip install requests beautifulsoup4
import os
import sys
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


start_url = sys.argv[1]
total_depth = int(sys.argv[2])
print(f"Start url = {start_url}, depth = {total_depth}")

directory_to_save = 'data'
if not os.path.exists(directory_to_save):
    os.makedirs(directory_to_save)

max_timeout = 5  # some sites like Twitter don't respond
num_saved_links = 0
cur_depth_links = {start_url}
saved_links = {}
internal_urls = set()
external_urls = set()
print(cur_depth_links)
for depth in range(total_depth + 1):
    print(f"Current depth = {depth}")
    print(f"Crawl links: {cur_depth_links}")
    new_depth_links = set()
    for link in cur_depth_links:
        if link not in saved_links.keys():
            # print(f"Testing link {link}")
            try:
                page = requests.get(link, timeout=max_timeout)
            except requests.exceptions.RequestException as e:
                print(f"{link} does not work, exception {e}")
                continue
            # print(f"Connected to {link}")
            num_saved_links += 1
            saved_links[link] = num_saved_links
            path_to_html = os.path.join(directory_to_save, str(num_saved_links) + '.html')
            print(f"Saving {path_to_html}")
            with open(path_to_html, 'w') as file:
                file.write(page.text)
            domain_name = urlparse(link).netloc
            soup = BeautifulSoup(page.content, "html.parser")
            for anchor_tag in soup.findAll("a", href=True):
                href = anchor_tag.attrs.get("href")
                # print(f"Find new link {href} on page {link}")
                if href == "" or href is None:
                    # href empty tag
                    continue
                href = urljoin(link, href)
                parsed_href = urlparse(href)
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                if is_valid(href) and domain_name in href:
                    # internal link
                    if href not in saved_links.keys():
                        new_depth_links.add(href)
    cur_depth_links = sorted(new_depth_links)
    print("------------------")
path_to_urls = 'urls.txt'
with open(path_to_urls, 'w') as file:
    for link in saved_links.keys():
        line_to_save = str(saved_links[link]) + " " + link + "\n"
        file.write(line_to_save)
print(f"Done! Total num of links = {len(saved_links)}")
