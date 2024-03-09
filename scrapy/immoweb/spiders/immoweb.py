import json
import logging
import os
import traceback

import scrapy

from scrapy.exceptions import CloseSpider

from immoweb.items import ImmowebItem
from immoweb.utils import get_data_from_html, get_data, next_page, get_property_url


class ImmoSpider(scrapy.Spider):
    name = 'immoweb'

    start_urls = [
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/east-flanders/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/west-flanders/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/antwerpen/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/limburg/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/vlaams-brabant/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/brussels/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/waals-brabant/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/henegouwen/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/luxembourg/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/namen/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale/luik/province?countries=BE&isALifeAnnuitySale=false&isAPublicSale=false&page=1&orderBy=most_expensive",  # &minPrice=2000000
    ]

    def __init__(self, *args, **kwargs):
        super(ImmoSpider, self).__init__(*args, **kwargs)
        self.counter = 0

    def start_requests(self):
        """
        this function is automatically called when the spider is started.
        it will loop over the  start_urls and make a request for each url
        than call the parse_page_search_result_list function when the
        response of that request is received
        """
        for start_url in self.start_urls:
            logging.info(f'loading: {start_url}')
            yield scrapy.Request(
                start_url,
                # when the response is received for start_url, the parse_page_search_result_list
                # function is called and the response object is passed as an argument
                callback=self.parse_page_search_result_list,
                errback=self.errback,
            )

    async def parse_page_search_result_list(self, response):
        """
        it receives the responses that are made by the start_requests function,
        and it will extract json data from those responses and build individual
        property urls. Then it will make a request for each property url and call
        the parse_property function when the response of that request is received
        """
        json_response = response.json()
        properties = json_response.get('results', {})

        # yield the properties
        for property in properties:
            url = get_property_url(property)
            logging.info(f'\tloading property url: {url}')
            yield scrapy.Request(  # load a search list and call back parse_my_search_lists
                url,
                # when the response is received for url, the parse_page_search_result_list
                # function is called and the response object is passed as an argument
                callback=self.parse_property,
                errback=self.errback,
            )

        # yield the next page
        if len(properties) != 0:
            next_page_url = next_page(response.url)
            logging.info(f'NEXT PAGE: {next_page_url}')
            yield scrapy.Request(
                next_page_url,
                # when the response is received for next_page_url, the parse_page_search_result_list
                # function is called and the response object is passed as an argument.
                # so this is a recursive call to parse_page_search_result_list
                callback=self.parse_page_search_result_list,
                errback=self.errback,
            )

    async def parse_property(self, response):
        """
        it receives the responses that are made by the parse_page_search_result_list function,
        and it will extract json data from the window.classified variable in the script tag,
        it will then call the get_data function to clean the data and yield an ImmowebItem,
        if there is an error, it will write the raw json data to a file together with the error,
        so it can be inspected later. If there is an error, it will also stop the spider
        """
        self.counter += 1
        raw_data = get_data_from_html(response.text)
        try:
            cleaned_data = get_data(raw_data)
            # yield an ImmowebItem
            logging.info('\t\t' + 'YIELD' * 5 + ' url:' + response.url)
            yield ImmowebItem(**cleaned_data, url=response.url)
        except Exception as e:
            # get the full error message
            full_traceback = traceback.format_exc()

            # build the error dump file path
            error_dump_path = os.path.join('errors', str(raw_data.get("id")) + '.json')

            logging.error('\t\t' + 'ERROR ' * 5 + ' error_dump:' + error_dump_path + ' url:' + response.url)

            # write the error to a file
            with open(error_dump_path, 'w') as f:
                # write the raw json from immoweb to a file
                f.writelines(json.dumps(raw_data, indent=4, sort_keys=True))
                # append the full error message to the file
                f.writelines('\n' + full_traceback)
                # append the url of the property to the file
                f.writelines('\n' + response.url)

            # raise an exception to stop the spider
            raise CloseSpider(reason=f'Error, stopping the spider. look at dump file: {error_dump_path}')

        logging.info(f"\t\t#{self.counter} id: {cleaned_data.get('ID')} price: {cleaned_data.get('Price')} location: {cleaned_data.get('Locality')}")

    async def errback(self, failure):
        logging.error('FAILED')