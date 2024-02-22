from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import json
import re
from requests import Session
from bs4 import BeautifulSoup
from .data_manipulation import DataManipulation


class DataCollector:
    def __init__(self):
        self.session = Session()

    def get_links_from_page(self, page):
        self.page = page
        base_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale"
        search_url = f"{base_url}?countries=BE&page={page}"
        response = self.session.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            property_links = soup.find_all("a", class_="card__title-link")
            return [link["href"] for link in property_links if "href" in link.attrs]
        else:
            print(f"Failed to retrieve page {page}: {response.status_code}")
            return []

    # This function retrieves the URLs of the properties listed on the Immoweb search results page
    # It now uses concurrent requests to speed up the process
    def get_property_links(self, pages):
        self.pages = pages
        all_urls = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.get_links_from_page, page)
                for page in range(1, pages + 1)
            ]
            for future in concurrent.futures.as_completed(futures):
                all_urls.extend(future.result())
        return all_urls

    def get_data_from_html(self, html: str):
        response = self.session.get(html)
        regex = r"(<script type=\"text/javascript\">\n\s+window\.classified = )(.*)"
        match = re.search(regex, response.text)
        return json.loads(match.group(2)[:-1])

    def estate_check(self, data: dict):
        """
        Checks if the property is a new real estate project or not
        """
        self.data = data
        cluster = data.get("cluster")
        if cluster is None:
            DataManipulation().get_data(data)
        else:
            unitlist = []
            units = data.get("cluster").get("units")[0].get("items")
            for item in units:
                salestatus = DataManipulation().safeget(item, ["saleStatus"])
                if salestatus == "AVAILABLE":
                    locality = DataManipulation().safeget(
                        data, ["cluster", "units", "items", "locality"], default=None
                    )
                    postalcode = DataManipulation().safeget(
                        data, ["property", "location", "postalCode"], default=None
                    )
                    id = item.get("id")
                    housetype = DataManipulation().safeget(
                        item, ["subtype"], default=None
                    )
                    baseurl = f"https://www.immoweb.be/en/classified/{housetype}/for-sale/{locality}/{postalcode}/{id}"
                    unitlist.append(baseurl)
            for unit in unitlist:
                DataManipulation().get_data(self.get_data_from_html(unit))
