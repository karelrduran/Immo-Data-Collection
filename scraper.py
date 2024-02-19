from requests import Session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class Scraper:
    def __init__(self):
        self.session = Session()
        self.page = 1
        self.url = f"https://www.immoweb.be/en/classified/apartment/for-sale/Sint-Denijs-Westrem/9051/11149067"

    def scrape(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            for i in soup.find_all("table", class_="classified-table"):
                for j in i.find_all("td"):
                    print(j.get_text().strip())


Scraper().scrape()
