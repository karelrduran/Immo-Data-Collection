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
        self.data = data
        """
        receives the raw data from the window.classified json and returns a dictionary with the fields that we want to keep
        """
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        # logic is not exact as item that are NOTARY_SALE and LIFE_ANNUITY_SALE will only be marked as LIFE_ANNUITY_SALE,
        # but it doesn't matter because we are only interested in NORMAL_SALE and not NORMAL_SALE
        sale_type = "NORMAL_SALE"
        if self.safeget(data, ["flags", "isLifeAnnuitySale"], default=None):
            sale_type = "LIFE_ANNUITY_SALE"
        elif self.safeget(data, ["flags", "isPublicSale"], default=None):
            sale_type = "PUBLIC_SALE"
        elif self.safeget(data, ["flags", "isNotarySale"], default=None):
            sale_type = "NOTARY_SALE"

        new_data = {}
        # do not self.safeget the id, so it will raise an AttributeError if it does not exist
        new_data["ID"] = data["id"]
        new_data["Locality"] = self.safeget(
            data, ["property", "location", "locality"], default=None
        )
        new_data["Postal Code"] = self.safeget(
            data, ["property", "location", "postalCode"], default=None
        )
        new_data["Build Year"] = self.safeget(
            data, ["property", "building", "constructionYear"], default=None
        )
        new_data["Facades"] = self.safeget(
            data, ["property", "building", "facadeCount"], default=None
        )
        new_data["Habitable Surface"] = self.safeget(
            data, ["property", "netHabitableSurface"], default=None
        )
        new_data["Land Surface"] = self.safeget(
            data, ["property", "land", "surface"], default=None
        )  # needs some work
        new_data["Type"] = self.safeget(data, ["property", "type"], default=None)
        new_data["Subtype"] = self.safeget(data, ["property", "subtype"], default=None)
        new_data["Price"] = self.safeget(data, ["price", "mainValue"], default=None)
        new_data["Sale Type"] = sale_type
        new_data["Bedroom Count"] = self.safeget(
            data, ["property", "bedroomCount"], default=None
        )
        new_data["Bathroom Count"] = self.safeget(
            data, ["property", "bathroomCount"], default=None
        )
        new_data["Toilet Count"] = self.safeget(
            data, ["property", "toiletCount"], default=None
        )

        new_data["Room Count"] = 0
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

        new_data["Kitchen"] = (
            True
            if self.safeget(data, ["property", "kitchen", "type"], default=False)
            else False
        )
        new_data["Kitchen Surface"] = self.safeget(
            data, ["property", "kitchen", "surface"], default=None
        )
        new_data["Kitchen Type"] = self.safeget(
            data, ["property", "kitchen", "type"], default=None
        )
        new_data["Furnished"] = (
            True
            if self.safeget(data, ["transaction", "sale", "isFurnished"], default=False)
            else False
        )
        new_data["Openfire"] = (
            True
            if self.safeget(data, ["property", "fireplaceExists"], default=False)
            else False
        )
        new_data["Fireplace Count"] = self.safeget(
            data, ["property", "fireplaceCount"], default=None
        )
        new_data["Terrace"] = (
            True
            if self.safeget(data, ["property", "hasTerrace"], default=False)
            else False
        )
        new_data["Terrace Surface"] = self.safeget(
            data, ["property", "terraceSurface"], default=None
        )
        new_data["Terrace Orientation"] = self.safeget(
            data, ["property", "terraceOrientation"], default=None
        )
        new_data["Garden Exists"] = (
            True
            if self.safeget(data, ["property", "hasGarden"], default=False)
            else False
        )
        new_data["Garden Surface"] = self.safeget(
            data, ["property", "gardenSurface"], default=None
        )
        new_data["Garden Orientation"] = self.safeget(
            data, ["property", "gardenOrientation"], default=None
        )
        new_data["Swimming Pool"] = self.safeget(
            data, ["property", "hasSwimmingPool"], default=None
        )
        new_data["State of Building"] = self.safeget(
            data, ["property", "building", "condition"], default=None
        )
        new_data["Living Surface"] = self.safeget(
            data, ["property", "livingRoom", "surface"], default=None
        )

        new_data["EPC"] = self.safeget(
            data, ["transaction", "certificates", "epcScore"], default=None
        )
        new_data["Consumption Per m2"] = self.safeget(
            data,
            ["transaction", "certificates", "primaryEnergyConsumptionPerSqm"],
            default=None,
        )
        new_data["Cadastral Income"] = self.safeget(
            data, ["transaction", "sale", "cadastralIncome"], default=None
        )
        new_data["Has starting Price"] = self.safeget(
            data, ["transaction", "sale", "hasStartingPrice"], default=None
        )
        new_data["Transaction Subtype"] = self.safeget(
            data, ["transaction", "subtype"], default=None
        )
        new_data["Heating Type"] = self.safeget(
            data, ["property", "energy", "heatingType"], default=None
        )

        new_data["Is Holiday Property"] = self.safeget(
            data, ["property", "isHolidayProperty"], default=None
        )
        new_data["Gas Water Electricity"] = self.safeget(
            data, ["property", "land", "hasGasWaterElectricityConnection"], default=None
        )
        new_data["Sewer"] = self.safeget(
            data, ["property", "land", "sewerConnection"], default=None
        )
        new_data["Sea view"] = self.safeget(
            data, ["property", "location", "hasSeaView"], default=None
        )
        new_data["Parking count inside"] = self.safeget(
            data, ["property", "parkingCountIndoor"], default=None
        )
        new_data["Parking count outside"] = self.safeget(
            data, ["property", "parkingCountOutdoor"], default=None
        )
        new_data["Parking box count"] = self.safeget(
            data, ["property", "parkingCountClosedBox"], default=None
        )
        DataOutput().to_json_file(new_data)
