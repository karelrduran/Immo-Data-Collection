import json

from src.scraper.data_output import DataOutput


class DataManipulation:
    """
    A class to manipulate and clean data extracted from Immoweb.

    Methods:
    clean_data(cls) -> None: A class method to clean data (not implemented).
    safeget(nested_dict, keys: list[str], default=None): Safely gets a value from a nested dictionary using a list of keys.
    get_data(data: dict) -> dict: Extracts relevant fields from raw data and returns a dictionary.
    """

    def safeget(self, nested_dict, keys: list[str], default=None):
        """
        Safely get a value from a nested dictionary using a list of keys.

        Args:
        nested_dict (dict): The nested dictionary to retrieve value from.
        keys (list[str]): List of keys to traverse the nested dictionary.
        default: The default value to return if the key is not found.

        Returns:
        The value corresponding to the keys in the nested dictionary, or default if not found.
        """
        nested_dict = nested_dict
        keys = keys
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
        Receives the raw data from the window.classified JSON and returns a dictionary with the desired fields.

        Args:
        data (dict): The raw data extracted from Immoweb.

        Returns:
        dict: Extracted and processed data.
        """
        # logic is not exact as item that are NOTARY_SALE and LIFE_ANNUITY_SALE will only be marked as LIFE_ANNUITY_SALE,
        # but it doesn't matter because we are only interested in NORMAL_SALE and not NORMAL_SALE
        sale_type = "NORMAL_SALE"
        if self.safeget(data, ["flags", "isLifeAnnuitySale"], default=None):
            sale_type = "LIFE_ANNUITY_SALE"
        elif self.safeget(data, ["flags", "isPublicSale"], default=None):
            sale_type = "PUBLIC_SALE"
        elif self.safeget(data, ["flags", "isNotarySale"], default=None):
            sale_type = "NOTARY_SALE"

        new_data = {
            "ID": data["id"],
            "Locality": self.safeget(
                data, ["property", "location", "locality"], default=None
            ),
            "Postal Code": self.safeget(
                data, ["property", "location", "postalCode"], default=None
            ),
            "Build Year": self.safeget(
                data, ["property", "building", "constructionYear"], default=None
            ),
            "Facades": self.safeget(
                data, ["property", "building", "facadeCount"], default=None
            ),
            "Habitable Surface": self.safeget(
                data, ["property", "netHabitableSurface"], default=None
            ),
            "Land Surface": self.safeget(
                data, ["property", "land", "surface"], default=None
            ),
            "Type": self.safeget(data, ["property", "type"], default=None),
            "Subtype": self.safeget(data, ["property", "subtype"], default=None),
            "Price": self.safeget(data, ["price", "mainValue"], default=None),
            "Sale Type": sale_type,
            "Bedroom Count": self.safeget(
                data, ["property", "bedroomCount"], default=None
            ),
            "Bathroom Count": self.safeget(
                data, ["property", "bathroomCount"], default=None
            ),
            "Toilet Count": self.safeget(
                data, ["property", "toiletCount"], default=None
            ),
            "Room Count": 0,
            "Kitchen": (
                True
                if self.safeget(data, ["property", "kitchen", "type"], default=False)
                else False
            ),
            "Kitchen Surface": self.safeget(
                data, ["property", "kitchen", "surface"], default=None
            ),
            "Kitchen Type": self.safeget(
                data, ["property", "kitchen", "type"], default=None
            ),
            "Furnished": (
                True
                if self.safeget(
                    data, ["transaction", "sale", "isFurnished"], default=False
                )
                else False
            ),
            "Openfire": (
                True
                if self.safeget(data, ["property", "fireplaceExists"], default=False)
                else False
            ),
            "Fireplace Count": self.safeget(
                data, ["property", "fireplaceCount"], default=None
            ),
            "Terrace": (
                True
                if self.safeget(data, ["property", "hasTerrace"], default=False)
                else False
            ),
            "Terrace Surface": self.safeget(
                data, ["property", "terraceSurface"], default=None
            ),
            "Terrace Orientation": self.safeget(
                data, ["property", "terraceOrientation"], default=None
            ),
            "Garden Exists": (
                True
                if self.safeget(data, ["property", "hasGarden"], default=False)
                else False
            ),
            "Garden Surface": self.safeget(
                data, ["property", "gardenSurface"], default=None
            ),
            "Garden Orientation": self.safeget(
                data, ["property", "gardenOrientation"], default=None
            ),
            "Swimming Pool": self.safeget(
                data, ["property", "hasSwimmingPool"], default=None
            ),
            "State of Building": self.safeget(
                data, ["property", "building", "condition"], default=None
            ),
            "Living Surface": self.safeget(
                data, ["property", "livingRoom", "surface"], default=None
            ),
            "EPC": self.safeget(
                data, ["transaction", "certificates", "epcScore"], default=None
            ),
            "Consumption Per m2": self.safeget(
                data,
                ["transaction", "certificates", "primaryEnergyConsumptionPerSqm"],
                default=None,
            ),
            "Cadastral Income": self.safeget(
                data, ["transaction", "sale", "cadastralIncome"], default=None
            ),
            "Has starting Price": self.safeget(
                data, ["transaction", "sale", "hasStartingPrice"], default=None
            ),
            "Transaction Subtype": self.safeget(
                data, ["transaction", "subtype"], default=None
            ),
            "Heating Type": self.safeget(
                data, ["property", "energy", "heatingType"], default=None
            ),
            "Is Holiday Property": self.safeget(
                data, ["property", "isHolidayProperty"], default=None
            ),
            "Gas Water Electricity": self.safeget(
                data,
                ["property", "land", "hasGasWaterElectricityConnection"],
                default=None,
            ),
            "Sewer": self.safeget(
                data, ["property", "land", "sewerConnection"], default=None
            ),
            "Sea view": self.safeget(
                data, ["property", "location", "hasSeaView"], default=None
            ),
            "Parking count inside": self.safeget(
                data, ["property", "parkingCountIndoor"], default=None
            ),
            "Parking count outside": self.safeget(
                data, ["property", "parkingCountOutdoor"], default=None
            ),
            "Parking box count": self.safeget(
                data, ["property", "parkingCountClosedBox"], default=None
            ),
        }

        new_data["Room Count"] += (
            new_data["Bedroom Count"] if new_data["Bedroom Count"] else 0
        )
        new_data["Room Count"] += (
            new_data["Bathroom Count"] if new_data["Bathroom Count"] else 0
        )
        new_data["Room Count"] += (
            new_data["Toilet Count"] if new_data["Toilet Count"] else 0
        )
        new_data["Room Count"] = (
            new_data["Room Count"] if new_data["Room Count"] else None
        )

        DataOutput().to_json_file(new_data)
