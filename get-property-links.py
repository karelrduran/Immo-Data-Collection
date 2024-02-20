import requests
from bs4 import BeautifulSoup
import pandas as pd # I'm using pandas to save the URLs to a CSV file, as I'm familiar with this package


# This function retrieves the URLs of the properties listed on the Immoweb search results page
# When called, it and the list variable
# It also saves the results to a csv file

def get_property_links(base_url, pages):
    all_urls = []
    for page in range(1, pages + 1):
        search_url = f"{base_url}?countries=BE&page={page}"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            property_links = soup.find_all('a', class_='card__title-link')
            urls = [link['href'] for link in property_links if 'href' in link.attrs]
            all_urls.extend(urls)
        else:
            print(f"Failed to retrieve the search results page: {response.status_code}")
    urls_df = pd.DataFrame(all_urls, columns=['URL'])
    urls_df.to_csv('property_urls.csv', index=False)
    return all_urls

# Define the base URL for the search results:
base_search_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale'
# Specify the number of pages we want to scrape: (each search page contains 60 properties)
total_pages = 200 # 10 search pages (600 unique urls saved) takes
# 10 pages (600 unique URLS saved) takes 10 seconds
# 30 pages (1800 unique URLS saved) takes 25 seconds
# 50 pages (3000 unique URLS saved) takes 50 seconds
# 100 pages (6000 unique URLS saved) takes 90 seconds
# 200 pages (12000 unique URLS saved) takes 180 seconds
# Get property URLs from the specified number of pages
property_urls = get_property_links(base_search_url, total_pages)
print(len(property_urls)) # print the length of the list, to see how many page URLS we have
print(property_urls[:10]) #print the first 10 urls, change this to print more if you want to see more
