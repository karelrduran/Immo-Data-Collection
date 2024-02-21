import re
from requests import Session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import multiprocessing
import json
import pandas as pd  # I'm using pandas to save the URLs to a CSV file, as I'm familiar with this package
from time import sleep

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

    def get_data_from_html(self, html: str):
        response = self.session.get(html)
        regex = r"(<script type=\"text/javascript\">\n\s+window\.classified = )(.*)"
        match = re.search(regex, response.text)
        with open("testing.json", "a", encoding="utf-8") as file:
            json.dump(
                json.loads(match.group(2)[:-1]), file, ensure_ascii=False, indent=4
            )
            file.write("\n")
        return json.loads(match.group(2)[:-1])

    def safeget(self, nested_dict, keys: list[str], default=None):
        """
        Safely get a value from a nested dictionary using a list of keys.
        If an intermediate key leads to None, treat it as an empty dict for the purpose of continuing the path traversal.
        """
        self.nested_dict = nested_dict
        self.keys = keys
        current_level = nested_dict
        for i, key in enumerate(keys):
            # If current_level is None but not at the last key, simulate it as an empty dict
            if current_level is None and i < len(keys) - 1:
                current_level = {}

            # Check if the current level is a dictionary and the key exists in it.
            if isinstance(current_level, dict) and key in current_level:
                current_level = current_level[key]
            else:
                return default
        return current_level if current_level is not None else default

    def estate_check(self, data: dict):
        """
        Checks if the property is a new real estate project or not
        """
        self.data = data
        cluster = data.get("cluster")
        if cluster is None:
            self.get_data(data)
        else:
            unitlist = []
            units = data.get("cluster").get("units")[0].get("items")
            for item in units:
                salestatus = self.safeget(item, ["saleStatus"])
                if salestatus == "AVAILABLE":
                    locality = self.safeget(
                        data, ["cluster", "units", "items", "locality"], default=None
                    )
                    postalcode = self.safeget(
                        data, ["property", "location", "postalCode"], default=None
                    )
                    id = item.get("id")
                    housetype = self.safeget(item, ["subtype"], default=None)
                    baseurl = f"https://www.immoweb.be/en/classified/{housetype}/for-sale/{locality}/{postalcode}/{id}"
                    unitlist.append(baseurl)
            for unit in unitlist:
                self.get_data(self.get_data_from_html(unit))

    def get_data(self, data: dict) -> dict:
        """
        receives the raw data from the window.classified json and returns a dictionary with the fields that we want to keep
        """
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        # logic is not exact as item that are NOTARY_SALE and LIFE_ANNUITY_SALE will only be marked as LIFE_ANNUITY_SALE,
        # but it doesn't matter because we are only interested in NORMAL_SALE and not NORMAL_SALE
        sale_type = "NORMAL_SALE"
        if self.safeget(data, ["flags", "isLifeAnnuitySale"], default=None):
            sale_type = "LIFE_ANNUITY_SALE"
        elif self.safeget(data, ["flags", "isPublicSale"], default=None):
            sale_type = "PUBLIC_SALE"
        elif self.safeget(data, ["flags", "isNotarySale"], default=None):
            sale_type = "NOTARY_SALE"

        new_data = {}
        # do not self.safeget the id, so it will raise an AttributeError if it does not exist
        new_data["ID"] = data["id"]
        new_data["Locality"] = self.safeget(
            data, ["property", "location", "locality"], default=None
        )
        new_data["Postal Code"] = self.safeget(
            data, ["property", "location", "postalCode"], default=None
        )
        new_data["Build Year"] = self.safeget(
            data, ["property", "building", "constructionYear"], default=None
        )
        new_data["Facades"] = self.safeget(
            data, ["property", "building", "facadeCount"], default=None
        )
        new_data["Habitable Surface"] = self.safeget(
            data, ["property", "netHabitableSurface"], default=None
        )
        new_data["Land Surface"] = self.safeget(
            data, ["property", "land", "surface"], default=None
        )  # needs some work
        new_data["Type"] = self.safeget(data, ["property", "type"], default=None)
        new_data["Subtype"] = self.safeget(data, ["property", "subtype"], default=None)
        new_data["Price"] = self.safeget(data, ["price", "mainValue"], default=None)
        new_data["Sale Type"] = sale_type
        new_data["Bedroom Count"] = self.safeget(
            data, ["property", "bedroomCount"], default=None
        )
        new_data["Bathroom Count"] = self.safeget(
            data, ["property", "bathroomCount"], default=None
        )
        new_data["Toilet Count"] = self.safeget(
            data, ["property", "toiletCount"], default=None
        )

        new_data["Room Count"] = 0
        new_data["Room Count"] += (
            new_data["Bedroom Count"] if new_data["Bedroom Count"] else 0
        )
        new_data["Room Count"] += (
            new_data["Bathroom Count"] if new_data["Bathroom Count"] else 0
        )
        new_data["Room Count"] += (
            new_data["Toilet Count"] if new_data["Toilet Count"] else 0
        )
        new_data["Room Count"] = (
            new_data["Room Count"] if new_data["Room Count"] else None
        )

        new_data["Kitchen"] = (
            True
            if self.safeget(data, ["property", "kitchen", "type"], default=False)
            else False
        )
        new_data["Kitchen Surface"] = self.safeget(
            data, ["property", "kitchen", "surface"], default=None
        )
        new_data["Kitchen Type"] = self.safeget(
            data, ["property", "kitchen", "type"], default=None
        )
        new_data["Furnished"] = (
            True
            if self.safeget(data, ["transaction", "sale", "isFurnished"], default=False)
            else False
        )
        new_data["Openfire"] = (
            True
            if self.safeget(data, ["property", "fireplaceExists"], default=False)
            else False
        )
        new_data["Fireplace Count"] = self.safeget(
            data, ["property", "fireplaceCount"], default=None
        )
        new_data["Terrace"] = (
            True
            if self.safeget(data, ["property", "hasTerrace"], default=False)
            else False
        )
        new_data["Terrace Surface"] = self.safeget(
            data, ["property", "terraceSurface"], default=None
        )
        new_data["Terrace Orientation"] = self.safeget(
            data, ["property", "terraceOrientation"], default=None
        )
        new_data["Garden Exists"] = (
            True
            if self.safeget(data, ["property", "hasGarden"], default=False)
            else False
        )
        new_data["Garden Surface"] = self.safeget(
            data, ["property", "gardenSurface"], default=None
        )
        new_data["Garden Orientation"] = self.safeget(
            data, ["property", "gardenOrientation"], default=None
        )
        new_data["Swimming Pool"] = self.safeget(
            data, ["property", "hasSwimmingPool"], default=None
        )
        new_data["State of Building"] = self.safeget(
            data, ["property", "building", "condition"], default=None
        )
        new_data["Living Surface"] = self.safeget(
            data, ["property", "livingRoom", "surface"], default=None
        )

        new_data["EPC"] = self.safeget(
            data, ["transaction", "certificates", "epcScore"], default=None
        )
        new_data["Consumption Per m2"] = self.safeget(
            data,
            ["transaction", "certificates", "primaryEnergyConsumptionPerSqm"],
            default=None,
        )
        new_data["Cadastral Income"] = self.safeget(
            data, ["transaction", "sale", "cadastralIncome"], default=None
        )
        new_data["Has starting Price"] = self.safeget(
            data, ["transaction", "sale", "hasStartingPrice"], default=None
        )
        new_data["Transaction Subtype"] = self.safeget(
            data, ["transaction", "subtype"], default=None
        )
        new_data["Heating Type"] = self.safeget(
            data, ["property", "energy", "heatingType"], default=None
        )

        new_data["Is Holiday Property"] = self.safeget(
            data, ["property", "isHolidayProperty"], default=None
        )
        new_data["Gas Water Electricity"] = self.safeget(
            data, ["property", "land", "hasGasWaterElectricityConnection"], default=None
        )
        new_data["Sewer"] = self.safeget(
            data, ["property", "land", "sewerConnection"], default=None
        )
        new_data["Sea view"] = self.safeget(
            data, ["property", "location", "hasSeaView"], default=None
        )
        new_data["Parking count inside"] = self.safeget(
            data, ["property", "parkingCountIndoor"], default=None
        )
        new_data["Parking count outside"] = self.safeget(
            data, ["property", "parkingCountOutdoor"], default=None
        )
        new_data["Parking box count"] = self.safeget(
            data, ["property", "parkingCountClosedBox"], default=None
        )
        with open("testing2.json", "a", encoding="utf-8") as file:
            json.dump(new_data, file, ensure_ascii=False)
            file.write("\n")

    def scrapesession(self, urls):
        with multiprocessing.Pool() as pool:
            pool.map(self.scrape, urls)

    def write_to_csv(self, json_file, csv_file):
        self.json_file = json_file
        self.csv_file = csv_file
        df = pd.DataFrame(json.load(open(json_file)))
        df.to_csv(csv_file, index=False)


def main():
    scrape = Scraper()
    urls = scrape.get_property_links(base_search_url, total_pages)
    for u in urls:
        scrape.estate_check(scrape.get_data_from_html(u))


if __name__ == "__main__":
    main()
