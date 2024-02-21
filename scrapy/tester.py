import json
import re
from pprint import pprint

import requests

from immoweb.spiders.immoweb import get_data

put_the_url_to_the_immo_add_here = 'https://www.immoweb.be/en/classified/house/for-sale/woluwe-saint-pierre/1150/11112019'

def get_data_from_html(html: str):
    regex = r'(<script type=\"text/javascript\">\n\s+window\.classified = )(.*)'
    match = re.search(regex, html)
    return json.loads(match.group(2)[:-1])


response = requests.get(put_the_url_to_the_immo_add_here)
data = get_data_from_html(response.text)
if 'media' in data:
    del data['media']
if 'customers' in data:
    del data['customers']
if 'property' in data and 'alternativeDescriptions' in data['property']:
    del data['property']['alternativeDescriptions']
if 'property' in data and 'description' in data['property']:
    del data['property']['description']

new_data = get_data(data)


pprint(data)
pprint(new_data)

