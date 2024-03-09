# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmowebItem(scrapy.Item):
        fields = {
                "ID": scrapy.Field(),
                "Locality": scrapy.Field(),
                "Postal Code": scrapy.Field(),
                "Build Year": scrapy.Field(),
                "Facades": scrapy.Field(),
                'Habitable Surface': scrapy.Field(),  # netHabitableSurface
                'Land Surface': scrapy.Field(),
                'Type': scrapy.Field(),
                'Subtype': scrapy.Field(),
                'Price': scrapy.Field(),
                'Sale Type': scrapy.Field(),
                'Bedroom Count': scrapy.Field(),
                'Bathroom Count': scrapy.Field(),
                'Toilet Count': scrapy.Field(),
                "Room Count": scrapy.Field(),
                "Kitchen Surface": scrapy.Field(),
                "Kitchen": scrapy.Field(),
                "Kitchen Type": scrapy.Field(),
                'Furnished': scrapy.Field(),
                'Openfire': scrapy.Field(),
                'Fireplace Count': scrapy.Field(),
                'Terrace': scrapy.Field(),
                'Terrace Surface': scrapy.Field(),
                'Terrace Orientation': scrapy.Field(),
                'Garden Exists': scrapy.Field(),
                'Garden Surface': scrapy.Field(),
                'Garden Orientation': scrapy.Field(),
                'Swimming Pool': scrapy.Field(),
                'State of Building': scrapy.Field(),
                "Living Surface": scrapy.Field(),
                "EPC": scrapy.Field(),
                'Cadastral Income': scrapy.Field(),
                'Has starting Price': scrapy.Field(),
                'Transaction Subtype': scrapy.Field(),
                'Heating Type': scrapy.Field(),
                'Is Holiday Property': scrapy.Field(),
                'Gas Water Electricity': scrapy.Field(),
                'Sewer': scrapy.Field(),
                'Sea view': scrapy.Field(),
                'Parking count inside': scrapy.Field(),
                'Parking count outside': scrapy.Field(),
                'url': scrapy.Field(),
        }