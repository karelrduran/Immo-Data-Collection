from requests import Session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pprint import pprint
import multiprocessing
import json
import pandas as pd  # I'm using pandas to save the URLs to a CSV file, as I'm familiar with this package

base_search_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale"

# Specify the number of pages we want to scrape: (each search page contains 60 properties)
total_pages = 1  # 10 search pages (600 unique urls saved) takes
# 10 pages (600 unique URLS saved) takes 10 seconds
# 30 pages (1800 unique URLS saved) takes 25 seconds
# 50 pages (3000 unique URLS saved) takes 50 seconds
# 100 pages (6000 unique URLS saved) takes 90 seconds
# 200 pages (12000 unique URLS saved) takes 180 seconds
# Get property URLs from the specified number of pages


class Scraper:
    def __init__(self):
        self.session = Session()
        self.page = 1
        self.url = f"https://www.immoweb.be/en/classified/apartment/for-sale/Sint-Denijs-Westrem/9051/11149067"

    def get_property_links(self, base_url, pages):
        self.base_url = base_url
        self.pages = pages
        all_urls = []
        for page in range(1, pages + 1):
            search_url = f"{base_url}?countries=BE&page={page}"
            response = self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                property_links = soup.find_all("a", class_="card__title-link")
                urls = [link["href"] for link in property_links if "href" in link.attrs]
                all_urls.extend(urls)
            else:
                print(
                    f"Failed to retrieve the search results page: {response.status_code}"
                )
        urls_df = pd.DataFrame(all_urls, columns=["URL"])
        urls_df.to_csv("property_urls.csv", index=False)
        return all_urls

    def scrape(self, url):
        self.url = url
        with sync_playwright() as p:
            dict = {}
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            for i in soup.find_all("table", class_="classified-table"):
                table_data = {}
                for row in i.find_all("tr"):
                    for j, k in zip(row.find_all("td"), row.find_all("th")):
                        jfix = " ".join(
                            j.text.replace("\n", "")
                            .replace("kWh/", "")
                            .replace("m²", "")
                            .replace("€", "")
                            .split()
                        )
                        if k.text.strip() == "":
                            continue
                        if (
                            "Price" in k.text.strip()
                            or "Cadastral income" in k.text.strip()
                        ):
                            list = jfix.split()
                            jfix = f"{list[0]}€"
                        table_data[k.text.strip()] = jfix
                    dict.update(table_data)
            pprint(dict)
            with open("data.json", "a", encoding="utf-8") as file:
                json.dump(dict, file)
                file.write("\n")

    def scrapesession(self, urls):
        with multiprocessing.Pool() as pool:
            pool.map(self.scrape, urls)


def main():
    scraper = Scraper()
    property_urls = scraper.get_property_links(base_search_url, total_pages)
    scraper.scrapesession(property_urls)


if __name__ == "__main__":
    main()
