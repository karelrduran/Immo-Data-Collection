from src.scraper.data_collection import DataCollector


def main():
    data_collector = DataCollector()
    property_urls = data_collector.get_property_links(100)
    for url in property_urls:
        data = data_collector.get_data_from_html(url)
        data_collector.estate_check(data)


if __name__ == "__main__":
    main()
