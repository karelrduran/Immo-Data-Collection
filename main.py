import os

from src.scraper.data_collection import DataCollector
from src.scraper.data_output import DataOutput


def main():
    data_collector = DataCollector()
    property_urls = data_collector.get_property_links(50)
    with open(
        os.path.join("data", "already_parsed.json"), "a", encoding="utf-8"
    ) as file:
        for url in property_urls:
            id_ = url.split("/")[-1]
            print(url)
            if id_ in file.read():
                if data_collector.check_existant(id_) == False:
                    print("new property found")
                    file.write(id_ + "\n")
                    data = data_collector.get_data_from_html(url)
                    data_collector.estate_check(data)
            else:
                print("property already exists")
                file.write(id_ + "\n")
    DataOutput().to_csv_file(os.path.join("data", "data.csv"))


if __name__ == "__main__":
    main()
