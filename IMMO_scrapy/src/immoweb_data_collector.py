import csv
import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from bs4 import BeautifulSoup
from typing import List


class IMMOWebDataCollector(object):
    def __init__(self):
        pass
    @classmethod
    def get_links_from_page(cls, base_url: str, page: int) -> List[str]:
        search_url = f"{base_url}?countries=BE&page={page}"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            property_links = soup.find_all('a', class_='card__title-link')
            return [link['href'] for link in property_links if 'href' in link.attrs]
        else:
            print(f"Failed to retrieve page {page}: {response.status_code}")
            return []

    @classmethod
    def get_properties_link(cls, base_url: str, pages: int) -> List[str]:
        all_urls = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(cls.get_links_from_page, base_url, page) for page in range(1, pages + 1)]
            for future in concurrent.futures.as_completed(futures):
                all_urls.extend(future.result())
        # urls_df = pd.DataFrame(all_urls, columns=['URL'])
        # urls_df.to_csv('property_urls.csv', index=False)
        # print(all_urls)
        return all_urls

    @classmethod
    def get_properties_data(cls, response):
        script_content = response.xpath('//script[contains(text(),"window.dataLayer")]/text()').get()
        # script_content = response.xpath('//script[contains(text(),"window.classified")]/text()').get()pwd

        data_layer = []
        av_items = []
        if script_content:
            start_index = script_content.find('[')
            end_index = script_content.rfind(']') + 1
            data_layer_json = script_content[start_index:end_index]

            try:
                data_layer = json.loads(data_layer_json)
            except json.JSONDecodeError as e:
                print('Error parsing JSON from window.dataLayer: %s', e)

            match = re.search(r'const\s+av_items\s*=\s*({[^}]+})', script_content)
            if match is not None:
                av_items_json = match.group(1)
                av_items = json.loads(av_items_json)


        split_url = response.url.split('/')

        if av_items.get('id', ''):
            property_id = av_items.get('id', '')
        else:
            property_id = data_layer[0].get('classified', {}).get('id', '')

        locality_name = split_url[-3]
        postal_code = split_url[-2]

        if av_items.get('price', ''):
            price = av_items.get('price', '')
        else:
            price = data_layer[0].get('classified', {}).get('price', '')

        type_of_property = data_layer[0].get('classified', {}).get('type', '')

        if av_items.get('subtype', ''):
            subtype_of_property = av_items.get('subtype', '')
        else:
            subtype_of_property = data_layer[0].get('classified', {}).get('subtype', '')

        type_of_sale = data_layer[0].get('classified', {}).get('transactionType', '')

        if av_items.get('nb_bedrooms', ''):
            number_of_bedrooms = av_items.get('nb_bedrooms', '')
        else:
            number_of_bedrooms = data_layer[0].get('classified', {}).get('bedroom', {}).get('count', 0)

        living_area = 0

        equiped_kitchen = 1 if (
                av_items.get('kitchen_type', '')
                or data_layer[0].get('classified', {}).get('kitchen', {}).get('type', '')) else 0

        furnished = 0
        open_fire = 0

        terrace = 0
        if data_layer[0].get('classified', {}).get('outdoor', {}).get('garden', {}).get('surface', ''):
            terrace = data_layer[0].get('classified', {}).get('outdoor', {}).get('garden', {}).get('surface', '')

        garden = 0
        if data_layer[0].get('classified', {}).get('outdoor', {}).get('terrace', {}).get('exists', ''):
            garden = data_layer[0].get('classified', {}).get('outdoor', {}).get('terrace', {}).get('exists', '')

        surface_of_good = ''
        number_of_facades = 0
        swimming_pool = 0

        if av_items.get('building_state', ''):
            state_of_building = av_items.get('building_state', '')
        else:
            state_of_building = data_layer[0].get('building', {}).get('condition', '')

        return {
            'property_id': property_id,
            'locality_name': locality_name,
            'postal_code': postal_code,
            'price': price,
            'type_of_property': type_of_property,
            'subtype_of_property': subtype_of_property,
            'type_of_sale': type_of_sale,
            'number_of_bedrooms': number_of_bedrooms,
            'living_area': living_area,
            'equiped_kitchen': equiped_kitchen,
            'furnished': furnished,
            'open_fire': open_fire,
            'terrace': terrace,
            'garden': garden,
            'surface_of_good': surface_of_good,
            'number_of_facades': number_of_facades,
            'swimming_pool': swimming_pool,
            'state_of_building': state_of_building
        }

    @classmethod
    def save_to_csv(cls, data: List):
        output_file_name = './IMMO_scrapy/data/output/raw_data.csv'

        try:
            columns = data[0].keys()
            with open(output_file_name, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                if csvfile.tell() == 0:
                    writer.writeheader()

                for elem in data:
                    writer.writerow(elem)
        except Exception as e:
            print("Error exporting to CSV: ", e)
