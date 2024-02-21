import json
import logging
import re
from enum import Enum
from typing import List

regex_json_data = re.compile(r'(<script type=\"text/javascript\">\n\s+window\.classified = )(.*)')


def get_data_from_html(html: str) -> dict:
    """
    Extracts the JSON data from the HTML page from the variable window.classified
    that is inside the <script type="text/javascript">
    """
    match = re.search(regex_json_data, html)
    return json.loads(match.group(2)[:-1])


def safeget(nested_dict, keys: List[str], default=None):
    """
    Safely get a value from a nested dictionary using a list of keys.
    If an intermediate key leads to None, treat it as an empty dict for the purpose of continuing the path traversal.
    """
    current_level = nested_dict
    for i, key in enumerate(keys):
        # If current_level is None but not at the last key, simulate it as an empty dict
        if current_level is None and i < len(keys) - 1:
            current_level = {}

        # Check if the current level is a dictionary and the key exists in it.
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        else:
            return default
    return current_level if current_level is not None else default


def get_data(data: dict) -> dict:
    """
    receives the raw data from the window.classified json and returns a dictionary with the fields that we want to keep
    """
    if not isinstance(data, dict):
        raise ValueError('data must be a dictionary')

    # logic is not exact as item that are NOTARY_SALE and LIFE_ANNUITY_SALE will only be marked as LIFE_ANNUITY_SALE,
    # but it doesn't matter because we are only interested in NORMAL_SALE and not NORMAL_SALE
    sale_type = 'NORMAL_SALE'
    if safeget(data, ["flags", "isLifeAnnuitySale"], default=None):
        sale_type = 'LIFE_ANNUITY_SALE'
    elif safeget(data, ["flags", "isPublicSale"], default=None):
        sale_type = 'PUBLIC_SALE'
    elif safeget(data, ["flags", "isNotarySale"], default=None):
        sale_type = 'NOTARY_SALE'

    new_data = {}
    # do not safeget the id, so it will raise an AttributeError if it does not exist
    new_data['immoweb_id'] = data['id']
    new_data['location'] = safeget(data, ["property", "location", "locality"], default=None)
    new_data['postal_code'] = safeget(data, ["property", "location", "postalCode"], default=None)
    new_data['build_year'] = safeget(data, ["property", "building", "constructionYear"], default=None)
    new_data['wall_count'] = safeget(data, ["property", "building", "facadeCount"], default=None)
    new_data['habitable_surface'] = safeget(data, ["property", "netHabitableSurface"], default=None)
    new_data['land_surface'] = safeget(data, ["property", "land", "surface"], default=None)  # needs some work
    new_data['property_type'] = safeget(data, ["property", "type"], default=None)
    new_data['subtype'] = safeget(data, ["property", "subtype"], default=None)
    new_data['price'] = safeget(data, ["price", "mainValue"], default=None)
    new_data['sale_type'] = sale_type
    new_data['bedroom_count'] = safeget(data, ["property", "bedroomCount"], default=None)
    new_data['bathroom_count'] = safeget(data, ["property", "bathroomCount"], default=None)
    new_data['toilet_count'] = safeget(data, ["property", "toiletCount"], default=None)

    new_data['room_count'] = 0
    new_data['room_count'] += new_data['bedroom_count'] if new_data['bedroom_count'] else 0
    new_data['room_count'] += new_data['bathroom_count'] if new_data['bathroom_count'] else 0
    new_data['room_count'] += new_data['toilet_count'] if new_data['toilet_count'] else 0
    new_data['room_count'] = new_data['room_count'] if new_data['room_count'] else None

    new_data["kitchen_exists"] = True if safeget(data, ["property", "kitchen", "type"], default=False) else False
    new_data['kitchen_surface'] = safeget(data, ["property", "kitchen", "surface"], default=None)
    new_data['kitchen_type'] = safeget(data, ["property", "kitchen", "type"], default=None)
    new_data['furnish_exists'] = True if safeget(data, ["transaction", "sale", "isFurnished"], default=False) else False
    new_data['fireplace_exists'] = True if safeget(data, ["property", "fireplaceExists"], default=False) else False
    new_data['fireplace_count'] = safeget(data, ["property", "fireplaceCount"], default=None)
    new_data['terrace_exists'] = True if safeget(data, ["property", "hasTerrace"], default=False) else False
    new_data['terrace_surface'] = safeget(data, ["property", "terraceSurface"], default=None)
    new_data['terrace_orientation'] = safeget(data, ["property", "terraceOrientation"], default=None)
    new_data['garden_exists'] = True if safeget(data, ["property", "hasGarden"], default=False) else False
    new_data['garden_surface'] = safeget(data, ["property", "gardenSurface"], default=None)
    new_data['garden_orientation'] = safeget(data, ["property", "gardenOrientation"], default=None)
    new_data['swimming_pool'] = safeget(data, ["property", "hasSwimmingPool"], default=None)
    new_data['state_of_building'] = safeget(data, ["property", "building", "condition"], default=None)
    new_data["living_surface"] = safeget(data, ["property", "livingRoom", "surface"], default=None)

    new_data["epc"] = safeget(data, ["transaction", "certificates", "epcScore"], default=None)
    new_data['consumption_per_m2'] = safeget(data,
                                             ["transaction", "certificates", "primaryEnergyConsumptionPerSqm"],
                                             default=None)
    new_data['cadastral_income'] = safeget(data, ["transaction", "sale", "cadastralIncome"], default=None)
    new_data['has_starting_price'] = safeget(data, ["transaction", "sale", "hasStartingPrice"], default=None)
    new_data['transaction_subtype'] = safeget(data, ["transaction", "subtype"], default=None)
    new_data['heating_type'] = safeget(data, ["property", "energy", "heatingType"], default=None)

    new_data['is_holiday_property'] = safeget(data, ["property", "isHolidayProperty"], default=None)
    new_data['gas_water_electricity_exists'] = safeget(data,
                                                       ["property", "land", "hasGasWaterElectricityConnection"],
                                                       default=None)
    new_data['sewer_exists'] = safeget(data, ["property", "land", "sewerConnection"], default=None)
    new_data['sea_view_exists'] = safeget(data, ["property", "location", "hasSeaView"], default=None)
    new_data['parking_count_inside'] = safeget(data, ["property", "parkingCountIndoor"], default=None)
    new_data['parking_count_outside'] = safeget(data, ["property", "parkingCountOutdoor"], default=None)
    new_data['parking_box_count'] = safeget(data, ["property", "parkingCountClosedBox"], default=None)
    return new_data


def next_page(url: str) -> str:
    """
    find page=n in the url and replace it with page=n+1
    :param url: "https://...&page=1&..."
    :return: "https://...&page=2&..."
    """
    pattern = r"(page=)(\d+)"

    def replace(match):
        page_num = int(match.group(2))
        incremented_page_num = page_num + 1
        return match.group(1) + str(incremented_page_num)

    next_page_url = re.sub(pattern, replace, url)

    return next_page_url


def get_property_url(raw_property_data: dict) -> str:
    """get the url of a property from the raw immoweb json data of a property page"""
    type = raw_property_data["property"]["type"]
    postalcode = raw_property_data["property"]["location"]["postalCode"]
    locality = raw_property_data["property"]["location"]["locality"]
    id = raw_property_data["id"]
    url = f'https://www.immoweb.be/en/classified/{type.lower()}/for-sale/{locality.replace(" ", "-")}/{postalcode}/{id}'
    return url


class EPC(Enum):
    NONE = -1
    G = 0
    F = 1
    E = 2
    D = 3
    C = 4
    B = 5
    A = 6
    A_PLUS = 7
    A_PLUS_PLUS = 8


class WindOrientation(Enum):
    NONE = -1
    NORTH = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH = 5
    SOUTH_WEST = 6
    WEST = 7
    NORTH_WEST = 8


class HeatingType(Enum):
    NONE = -1
    ELECTRIC = 1
    GAS = 2
    FUELOIL = 3
    PELLET = 4
    WOOD = 5
    CARBON = 6
    SOLAR = 7


class KitchenType(Enum):
    NONE = -1
    NOT_INSTALLED = 1
    SEMI_EQUIPPED = 2
    INSTALLED = 3
    USA_UNINSTALLED = 4
    USA_SEMI_EQUIPPED = 5
    USA_INSTALLED = 6
    HYPER_EQUIPPED = 7
    USA_HYPER_EQUIPPED = 8


class PropertyType(Enum):
    APARTMENT = 1
    HOUSE = 2
    APARTMENT_GROUP = 3
    HOUSE_GROUP = 4


class SaleType(Enum):
    NORMAL_SALE = 1
    NOTARY_SALE = 2
    LIFE_ANNUITY_SALE = 3


class SeaViewExists(Enum):
    FALSE = 0
    TRUE = 1


class StateOfBuilding(Enum):
    NONE = -1
    TO_RESTORE = 1
    TO_RENOVATE = 2
    TO_BE_DONE_UP = 3
    GOOD = 4
    JUST_RENOVATED = 5
    AS_NEW = 6
    # NEW ???


class Subtype(Enum):
    OTHER_PROPERTY = 1
    APARTMENT = 2
    HOUSE = 3
    APARTMENT_GROUP = 4
    HOUSE_GROUP = 5
    APARTMENT_BLOCK = 6
    BUNGALOW = 7
    CASTLE = 8
    CHALET = 9
    COUNTRY_COTTAGE = 10
    DUPLEX = 11
    EXCEPTIONAL_PROPERTY = 12
    FARMHOUSE = 13
    FLAT_STUDIO = 14
    GROUND_FLOOR = 15
    KOT = 16
    LOFT = 17
    MANOR_HOUSE = 18
    MANSION = 19
    MIXED_USE_BUILDING = 20
    PENTHOUSE = 21
    SERVICE_FLAT = 22
    TOWN_HOUSE = 23
    TRIPLEX = 24
    VILLA = 25