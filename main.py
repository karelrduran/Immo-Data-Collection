import os

from src.scraper.data_collection import DataCollector
from src.scraper.data_output import DataOutput


def main():
    data_collector = DataCollector()
    property_urls = data_collector.get_property_links(2)
    with open(os.path.join("data", "data.json"), "r", encoding="utf-8") as file:
        for url in property_urls:
            id_ = url.split("/")[-1]
            print(url)
            if str(id_) not in file.read():
                data = data_collector.get_data_from_html(url)
                data_collector.estate_check(data)
    DataOutput().to_csv_file(os.path.join("data", "data.csv"))


if __name__ == "__main__":
    main()
