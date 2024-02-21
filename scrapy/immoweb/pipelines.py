# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["id"] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter["id"])
            return item


class ImmowebPipeline:
    def process_item(self, item, spider):
        # drop items with to many bedrooms > 10
        if isinstance(item['bedroom_count'], int) and item['bedroom_count'] > 10:
            raise DropItem(f"Too many bedrooms: {item!r}")

        # set wall counts of higher than 4 to 4 and lower than 2 to 2
        if isinstance(item['wall_count'], int):
            if item['wall_count'] > 4:
                item['wall_count'] = 4
            if item ['wall_count'] < 2:
                item['wall_count'] = 2

        # drop subtypes
        subtype_to_drop = [
            "APARTMENT_BLOCK",
            "APARTMENT_GROUP",
            "HOUSE_GROUP",
            "CASTLE",
            "MIXED_USE_BUILDING",  # with commercial space
        ]
        if item['subtype'] in subtype_to_drop:
            raise DropItem(f"Subtype to drop: {item!r}")

        # drop weird build years
        if len(item['build_year']) < 4:
            raise DropItem(f"Build year too short: {item!r}")

        # fix very low cadastral incomes
        if isinstance(item['cadastral_income'], int) and item['cadastral_income'] < 100:
            item['cadastral_income'] = None
        if isinstance(item['cadastral_income'], int) and item['cadastral_income'] > 15000:
            item['cadastral_income'] = 15000

        # change negative fireplace to None
        if isinstance(item['fireplace_count'], int) and item['fireplace_count'] < 0:
            item['fireplace_count'] = None




