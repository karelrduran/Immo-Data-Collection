import json
from pprint import pprint
from typing import List
import requests
from os import path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .property import Property


class DataCollector:
    def __init__(self):
        pass

    def get_property(self, num_properties: int = 10000) -> dict:
        pass

    def get_property_details(self, property_id: int) -> dict:
        pass

    def collect(self) -> None:
        pass

    def do_scrap(self) -> None:
        pass
    
