from .data_output import DataOutput



class DataManipulation:
    def __init__(self):
        pass

    @classmethod
    def clean_data(cls) -> None:
        pass

    def safeget(self, nested_dict, keys: list[str], default=None):
        """
        Safely get a value from a nested dictionary using a list of keys.
        If an intermediate key leads to None, treat it as an empty dict for the purpose of continuing the path traversal.
        """
        self.nested_dict = nested_dict
        self.keys = keys
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

    def get_data(self, data: dict) -> dict:
        """
        receives the raw data from the window.classified json and returns a dictionary with the fields that we want to keep
        """
        # logic is not exact as item that are NOTARY_SALE and LIFE_ANNUITY_SALE will only be marked as LIFE_ANNUITY_SALE,
        # but it doesn't matter because we are only interested in NORMAL_SALE and not NORMAL_SALE
        sale_type = 'NORMAL_SALE'
        if self.safeget(data, ["flags", "isLifeAnnuitySale"], default=None):
            sale_type = 'LIFE_ANNUITY_SALE'
        elif self.safeget(data, ["flags", "isPublicSale"], default=None):
            sale_type = 'PUBLIC_SALE'
        elif self.safeget(data, ["flags", "isNotarySale"], default=None):
            sale_type = 'NOTARY_SALE'

        new_data = {
            'immoweb_id': data['id'], 'location': self.safeget(data, ["property", "location", "locality"], default=None),
            'postal_code': self.safeget(data, ["property", "location", "postalCode"], default=None),
            'build_year': self.safeget(data, ["property", "building", "constructionYear"], default=None),
            'wall_count': self.safeget(data, ["property", "building", "facadeCount"], default=None),
            'habitable_surface': self.safeget(data, ["property", "netHabitableSurface"], default=None),
            'land_surface': self.safeget(data, ["property", "land", "surface"], default=None),
            'property_type': self.safeget(data, ["property", "type"], default=None),
            'subtype': self.safeget(data, ["property", "subtype"], default=None),
            'price': self.safeget(data, ["price", "mainValue"], default=None), 'sale_type': sale_type,
            'bedroom_count': self.safeget(data, ["property", "bedroomCount"], default=None),
            'bathroom_count': self.safeget(data, ["property", "bathroomCount"], default=None),
            'toilet_count': self.safeget(data, ["property", "toiletCount"], default=None),
            "kitchen_exists": True if self.safeget(data, ["property", "kitchen", "type"], default=False) else False,
            'kitchen_surface': self.safeget(data, ["property", "kitchen", "surface"], default=None),
            'kitchen_type': self.safeget(data, ["property", "kitchen", "type"], default=None),
            'furnish_exists': True if self.safeget(data, ["transaction", "sale", "isFurnished"],
                                              default=False) else False,
            'fireplace_exists': True if self.safeget(data, ["property", "fireplaceExists"], default=False) else False,
            'fireplace_count': self.safeget(data, ["property", "fireplaceCount"], default=None),
            'terrace_exists': True if self.safeget(data, ["property", "hasTerrace"], default=False) else False,
            'terrace_surface': self.safeget(data, ["property", "terraceSurface"], default=None),
            'terrace_orientation': self.safeget(data, ["property", "terraceOrientation"], default=None),
            'garden_exists': True if self.safeget(data, ["property", "hasGarden"], default=False) else False,
            'garden_surface': self.safeget(data, ["property", "gardenSurface"], default=None),
            'garden_orientation': self.safeget(data, ["property", "gardenOrientation"], default=None),
            'swimming_pool': self.safeget(data, ["property", "hasSwimmingPool"], default=None),
            'state_of_building': self.safeget(data, ["property", "building", "condition"], default=None),
            "living_surface": self.safeget(data, ["property", "livingRoom", "surface"], default=None),
            "epc": self.safeget(data, ["transaction", "certificates", "epcScore"], default=None),
            'cadastral_income': self.safeget(data, ["transaction", "sale", "cadastralIncome"], default=None),
            'has_starting_price': self.safeget(data, ["transaction", "sale", "hasStartingPrice"], default=None),
            'transaction_subtype': self.safeget(data, ["transaction", "subtype"], default=None),
            'heating_type': self.safeget(data, ["property", "energy", "heatingType"], default=None),
            'is_holiday_property': self.safeget(data, ["property", "isHolidayProperty"], default=None),
            'gas_water_electricity_exists': self.safeget(data, ["property", "land", "hasGasWaterElectricityConnection"],
                                                    default=None),
            'sewer_exists': self.safeget(data, ["property", "land", "sewerConnection"], default=None),
            'sea_view_exists': self.safeget(data, ["property", "location", "hasSeaView"], default=None),
            'parking_count_inside': self.safeget(data, ["property", "parkingCountIndoor"], default=None),
            'parking_count_outside': self.safeget(data, ["property", "parkingCountOutdoor"], default=None),
            'room_count': 0
        }

        new_data['room_count'] += new_data['bedroom_count'] if new_data['bedroom_count'] else 0
        new_data['room_count'] += new_data['bathroom_count'] if new_data['bathroom_count'] else 0
        new_data['room_count'] += new_data['toilet_count'] if new_data['toilet_count'] else 0
        new_data['room_count'] = new_data['room_count'] if new_data['room_count'] else None

        with open("testing2.json", "a", encoding="utf-8") as file:
            json.dump(new_data, file, ensure_ascii=False)
            file.write("\n")
