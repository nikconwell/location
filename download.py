#!/home/nik/github/location/venv/bin/python

import requests
from bs4 import BeautifulSoup
import os
import re
import argparse


#
# Download all Town of Natick Police Logs from the base URL.
#




#
# Todo - Do not download if file already exists. Maybe add flag --redownload to make it download again.
#



#
# Args
#
argParser = argparse.ArgumentParser(prog="download.py",
                                    description="Download Town of Natick Police Logs")
                                    
argParser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Debug mode for various things')
argParser.add_argument('--baseurl', dest='baseurl', default="https://natickma.gov/2052/2024-Daily-Log", help='Base URL to download from')

args = argParser.parse_args()

args.debug and print(f'>>>>> Using args.baseurl {args.baseurl}')


#
# Return a list of URLs on a page that match the given regex
#
def get_urls_from_page(baseurl,regex):

    urls = []
    
    # First get the base page where we will look for URLs to download
    args.debug and print(f'>>>>> Accessing {baseurl}')
    response = requests.get(baseurl)
    if response.status_code != 200:
        print(f'>>>>> Failed to retrieve the page. Status code: {response.status_code}')
        return None

    # Find all the links on the page
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)
        
    # Look at each link
    for link in links:
        href = link['href']
        url = f'https://natickma.gov{href}'
        args.debug and print(f'>>>>> Examining {url}')
        if (match := re.search(regex,url)):
            args.debug and print(f'>>>>> Found matching URL {url}')
            urls.append(url)
        else:
            args.debug and print('>>>>> No match')

    return(urls)


        
#
# Function to download all URLs on a page.
#
def download_url(url, download_folder):

    match = re.search(r'/([^/]+)$',url)
    file_name = f'{download_folder}/{match.group(1)}.pdf'
    args.debug and print(f'Will download {url} to {file_name}')
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    args.debug and print(f'Downloaded {url} to {file_name}')
    except Exception as e:
        print(f'Failed to download {url}: {e}')


urls = get_urls_from_page(args.baseurl,r'Daily-Log-([^/]+)$')
for url in urls:
    download_url(url, "./")
