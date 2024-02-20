import json
from pprint import pprint
from typing import List
import requests
from os import path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .property import Property


class DataCollector:
    def __init__(self):
        self.properties: List[Property] = []
        self.output_directory = path.join(path.join(path.realpath('data'), 'output'), 'data_output')
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "www.immoweb.be",
            "Sec-Fetch-Dest": "document",
        }
        self.pages = 2

    def get_property(self, num_properties: int = 10000) -> dict:
        pass

    def get_property_details(self, property_id: int) -> dict:
        pass

    def collect(self) -> None:
        pass

    def do_scrap(self) -> None:
        for page in range(self.pages):
            payload = {}
            response = requests.request(
                "GET",
                f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale?countries=BE&page={page}&orderBy=relevance",
                headers=self.headers,
                data=payload,
            )
            filtered = response.json().pop("results")
            pprint(filtered)
            with open(f"{self.output_directory}{page}.json", "w", encoding="utf-8") as file:
                json.dump(filtered, file, ensure_ascii=False, indent=1)

            print(len(filtered))
            for result in filtered:
                # result = filtered[result]
                type = result["property"]["type"]
                postalcode = result["property"]["location"]["postalCode"]
                locality = result["property"]["location"]["locality"]
                id = result["id"]
                url = f"https://www.immoweb.be/en/classified/{type.lower()}/for-sale/{locality.replace(' ', '-')}/{postalcode}/{id}"
                print(url)

    def scrape(self):
        self.session = requests.Session()
        self.page = 1
        self.url = f"https://www.immoweb.be/en/classified/apartment/for-sale/Sint-Denijs-Westrem/9051/11149067"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            for i in soup.find_all("table", class_="classified-table"):
                for j in i.find_all("td"):
                    print(j.get_text().strip())
