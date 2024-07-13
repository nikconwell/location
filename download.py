#!/home/nik/github/location/venv/bin/python



# pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup
import os
import re

def download_links_from_page(url, download_folder):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the links on the page
        links = soup.find_all('a', href=True)
        
        # Create the download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        # Download each link
        for link in links:
            href = link['href']
            url = f'https://natickma.gov{href}'
            # print(f'>>>>> Examining {url}')
            if (match := re.search(r'Daily-Log-([^/]+)$',url)):
                print(f'Found good URL {url}')
                file_name = f'{match.group(1)}.pdf'
                print(f'Will download {url} to {file_name}')
                try:
                    with requests.get(url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_name, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f'Downloaded {url} to {file_name}')
                except Exception as e:
                    print(f'Failed to download {url}: {e}')
    else:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')

# Example usage
url = 'https://www.natickma.gov/2052/2024-Daily-Log'
download_folder = './'
download_links_from_page(url, download_folder)
