from typing import Iterable, Dict
from pathlib import Path
import re

import scrapy
from scrapy import Request
import json

from ..src.immoweb_data_collector import IMMOWebDataCollector


class ImmowebSpider(scrapy.Spider):
    name = "immoweb"
    allowed_domains = ["www.immoweb.be"]

    # start_urls = [
    #     "https://www.immoweb.be/en/classified/house/for-sale/kortrijk/8500/11150724"]

    def __init__(self):
        super().__init__()
        # self.start_urls = [
        #     "https://www.immoweb.be/en/classified/house/for-sale/kortrijk/8500/11150724",
        #     "https://www.immoweb.be/en/classified/country-cottage/for-sale/villers-le-bouillet/4530/11143714"
        # ]
        self.start_urls = IMMOWebDataCollector.get_properties_link(
            base_url='https://www.immoweb.be/en/search/house-and-apartment/for-sale', pages=2)

    def start_requests(self) -> Iterable[Request]:
        urls = self.start_urls
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = f"raw_data.json"
        raw_data = [IMMOWebDataCollector.get_properties_data(response=response)]

        IMMOWebDataCollector.save_to_csv(data=raw_data)

        self.log(f"Saved file {filename}")
