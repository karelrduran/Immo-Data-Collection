from requests import Session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pprint import pprint


class Scraper:
    def __init__(self):
        self.session = Session()
        self.page = 1
        self.url = f"https://www.immoweb.be/en/classified/apartment/for-sale/Sint-Denijs-Westrem/9051/11149067"

    def scrape(self):
        with sync_playwright() as p:
            dict = {}
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
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


Scraper().scrape()
