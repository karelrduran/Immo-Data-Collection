from src.scraper.data_collection import DataCollector
from src.scraper.data_output import DataOutput


def main():
    DataOutput().to_csv_file("data.csv")
    """data_collector = DataCollector()
    property_urls = data_collector.get_property_links(100)
    with open("data.json", "r", encoding="utf-8") as file:
        for url in property_urls:
            id = url.split("/")[-1]
            print(url)
            if str(id) not in file.read():
                data = data_collector.get_data_from_html(url)
                data_collector.estate_check(data)
"""


if __name__ == "__main__":
    main()
