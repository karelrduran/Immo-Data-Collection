from requests import Session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pprint import pprint
import multiprocessing
import json
import pandas as pd  # I'm using pandas to save the URLs to a CSV file, as I'm familiar with this package
from time import sleep
import csv

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
            my_dict = {}
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            soup = BeautifulSoup(content, "html.parser")
            if "new-real-estate-project" in url:
                urls = []
                for list in soup.find_all(
                    "ul", class_="classified__list classified__list--striped"
                ):
                    for i in list.find_all("li"):
                        href = i.find("a")
                        if href:
                            urls.append(href.get("href"))
                    for u in urls:
                        page.goto(u)
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
                                table_data["URL"] = u
                                my_dict.update(table_data)
                                propertyid = u.split("/")[-1]
                                postalcode = u.split("/")[-2]
                                locality = u.split("/")[-3].capitalize()
                                type_of_property = u.split("/")[-5].capitalize()
                                useful_dict = {
                                    "Property ID": propertyid,
                                    "Locality": locality,
                                    "Postal Code": postalcode,
                                    "Price": my_dict.get("Price"),
                                    "Type of property": type_of_property,
                                    "Subtype of property": my_dict.get(
                                        "Subtype of property"
                                    ),
                                    "Type of sale": my_dict.get("Type of sale"),
                                    "Number of rooms": my_dict.get("Bedrooms"),
                                    "Living area": my_dict.get("Living area"),
                                    "Surface of good": my_dict.get(
                                        "Living area", ""
                                    ).replace(" square meters", ""),
                                    "Number of facades": my_dict.get(
                                        "Number of frontages"
                                    ),
                                    "State of the building": my_dict.get(
                                        "Building condition"
                                    ),
                                    "Energy class": my_dict.get("Energy class"),
                                    "Construction year": my_dict.get(
                                        "Construction year"
                                    ),
                                    "URL": my_dict.get("URL"),
                                }

                                if my_dict.get("Kitchen style") == "Not installed":
                                    useful_dict["Equipped kitchen"] = 0
                                else:
                                    useful_dict["Equipped kitchen"] = 1

                                if my_dict.get("Swimming pool"):
                                    if my_dict.get("Swimming pool") == "Yes":
                                        useful_dict["Swimming pool"] = 1
                                    else:
                                        useful_dict["Swimming pool"] = 0
                                else:
                                    useful_dict["Swimming pool"] = 0

                                if my_dict.get("Furnished"):
                                    if my_dict.get("Furnished") == "Yes":
                                        useful_dict["Furnished"] = 1
                                    else:
                                        useful_dict["Furnished"] = 0
                                else:
                                    useful_dict["Furnished"] = 0

                                if my_dict.get("How many fireplaces?"):
                                    if int(my_dict.get("How many fireplaces?")) > 0:
                                        useful_dict["Open fire"] = 1
                                    else:
                                        useful_dict["Open fire"] = 0
                                else:
                                    useful_dict["Open fire"] = 0

                                if my_dict.get("Garden surface"):
                                    useful_dict["Garden"] = my_dict.get(
                                        "Garden surface", ""
                                    ).replace(" square meters", "")
                                else:
                                    useful_dict["Garden"] = None

                                if my_dict.get("Terrace surface"):
                                    useful_dict["Terrace"] = my_dict.get(
                                        "Terrace surface", ""
                                    ).replace(" square meters", "")
                                else:
                                    useful_dict["Terrace"] = None
                        with open("useful_data.json", "a", encoding="utf-8") as file:
                            json.dump(useful_dict, file, ensure_ascii=False)
                            file.write("\n")
                        sleep(1)

            else:
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

                        table_data["URL"] = url
                        my_dict.update(table_data)
                        propertyid = url.split("/")[-1]
                        postalcode = url.split("/")[-2]
                        locality = url.split("/")[-3].capitalize()
                        type_of_property = url.split("/")[-5].capitalize()
                        useful_dict = {
                            "Property ID": propertyid,
                            "Locality": locality,
                            "Postal Code": postalcode,
                            "Price": my_dict.get("Price"),
                            "Type of property": type_of_property,
                            "Subtype of property": my_dict.get("Subtype of property"),
                            "Type of sale": my_dict.get("Type of sale"),
                            "Number of rooms": my_dict.get("Bedrooms"),
                            "Living area": my_dict.get("Living area"),
                            "Surface of good": my_dict.get("Living area", "").replace(
                                " square meters", ""
                            ),
                            "Number of facades": my_dict.get("Number of frontages"),
                            "State of the building": my_dict.get("Building condition"),
                            "Energy class": my_dict.get("Energy class"),
                            "Construction year": my_dict.get("Construction year"),
                            "URL": my_dict.get("URL"),
                        }

                        if my_dict.get("Kitchen style") == "Not installed":
                            useful_dict["Equipped kitchen"] = 0
                        else:
                            useful_dict["Equipped kitchen"] = 1

                        if my_dict.get("Swimming pool"):
                            if my_dict.get("Swimming pool") == "Yes":
                                useful_dict["Swimming pool"] = 1
                            else:
                                useful_dict["Swimming pool"] = 0
                        else:
                            useful_dict["Swimming pool"] = 0

                        if my_dict.get("Furnished"):
                            if my_dict.get("Furnished") == "Yes":
                                useful_dict["Furnished"] = 1
                            else:
                                useful_dict["Furnished"] = 0
                        else:
                            useful_dict["Furnished"] = 0

                        if my_dict.get("How many fireplaces?"):
                            if int(my_dict.get("How many fireplaces?")) > 0:
                                useful_dict["Open fire"] = 1
                            else:
                                useful_dict["Open fire"] = 0
                        else:
                            useful_dict["Open fire"] = 0

                        if my_dict.get("Garden surface"):
                            useful_dict["Garden"] = my_dict.get(
                                "Garden surface", ""
                            ).replace(" square meters", "")
                        else:
                            useful_dict["Garden"] = None

                        if my_dict.get("Terrace surface"):
                            useful_dict["Terrace"] = my_dict.get(
                                "Terrace surface", ""
                            ).replace(" square meters", "")
                        else:
                            useful_dict["Terrace"] = None
                with open("useful_data.json", "a", encoding="utf-8") as file:
                    json.dump(useful_dict, file, ensure_ascii=False)
                    file.write("\n")
                sleep(1)

    def scrapesession(self, urls):
        with multiprocessing.Pool() as pool:
            pool.map(self.scrape, urls)

    def write_to_csv(self, json_file, csv_file):
        self.json_file = json_file
        self.csv_file = csv_file
        df = pd.DataFrame(json.load(open(json_file)))
        df.to_csv(csv_file, index=False)


def main():
    scraper = Scraper()
    property_urls = scraper.get_property_links(base_search_url, total_pages)
    scraper.scrapesession(property_urls)


if __name__ == "__main__":
    main()
