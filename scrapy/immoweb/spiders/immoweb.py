import logging
from pprint import pprint

import scrapy
import re

from scrapy_playwright.page import PageMethod


class QuotesSpider(scrapy.Spider):
    name = 'immoweb'
    start_urls = [
        "https://www.immoweb.be/en/search-results/house/for-sale/east-flanders/province?countries=BE&page=1&orderBy=most_expensive",
        # "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=2&orderBy=relevance",
    ]
    handle_httpstatus_list = [403]

    def next_page(self, url):
        """get the next page for a given page"""
        pattern = r"(page=)(\d+)"

        def replace(match):
            page_num = int(match.group(2))
            incremented_page_num = page_num + 1
            return match.group(1) + str(incremented_page_num)

        next_page_url = re.sub(pattern, replace, url)

        return next_page_url

    def get_property_url(self, property: dict) -> str:
        type = property["property"]["type"]
        postalcode = property["property"]["location"]["postalCode"]
        locality = property["property"]["location"]["locality"]
        id = property["id"]
        url = f'https://www.immoweb.be/en/classified/{type.lower()}/for-sale/{locality.replace(" ", "-")}/{postalcode}/{id}'
        return url

    def start_requests(self):
        for start_url in self.start_urls:
            logging.info(f'loading: {start_url}')
            yield scrapy.Request(
                start_url,
                callback=self.parse_page_searh_result_list
            )

    async def parse_page_searh_result_list(self, response):
        # if response.get('playwright_page'):
        #     page = response.meta["playwright_page"]
        #     await page.close()

        json_response = response.json()
        logging.info(f"json_response = type: {type(json_response)}")
        properties = json_response.get('results', {})

        for property in properties:
            url = self.get_property_url(property)
            logging.info(f'loading property url: {url}')
            yield scrapy.Request(  # load a search list and call back parse_my_search_lists
                url,
                callback=self.parse_property,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_timeout', 1000),
                    ],
                    errback=self.errback,
                )
            )

        # recursively call parse if there was a full page of items
        if len(properties) != 29:
            next_page_url = self.next_page(response.url)
            logging.info(f'Loading next page {next_page_url}')
            yield scrapy.Request(
                next_page_url,
                callback=self.parse_page_searh_result_list,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_timeout', 1000),
                    ],
                    errback=self.errback,
                )
            )

    async def parse_property(self, response):
        with open('output.html', 'w') as f:
            f.write(response.text)
        page = response.meta["playwright_page"]
        await page.close()

        css_selector_price = '.classified__price .sr-only'

        result = response.css(css_selector_price)
        logging.info(result)

    async def errback(self, failure):
        logging.info('FAILED')
        # Check if the failure is because of a 403 response
        if failure.value.response.status == 403:
            logging.info(f"Got a 403 response: {failure.value.response.text}")
        logging.error(f"Error callback An error occurred: {failure.getErrorMessage()}, closing playwright page.")
        page = failure.request.meta["playwright_page"]
        await page.close()
