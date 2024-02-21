# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmowebItem(scrapy.Item):
        immoweb_id = scrapy.Field()
        location = scrapy.Field()
        postal_code = scrapy.Field()
        build_year = scrapy.Field()
        wall_count = scrapy.Field()
        habitable_surface = scrapy.Field()  # netHabitableSurface
        land_surface = scrapy.Field()
        property_type = scrapy.Field()
        subtype = scrapy.Field()
        price = scrapy.Field()
        sale_type = scrapy.Field()
        bedroom_count = scrapy.Field()
        bathroom_count = scrapy.Field()
        toilet_count = scrapy.Field()
        room_count = scrapy.Field()
        kitchen_surface = scrapy.Field()
        kitchen_exists = scrapy.Field()
        kitchen_type = scrapy.Field()
        furnish_exists = scrapy.Field()
        fireplace_exists = scrapy.Field()
        fireplace_count = scrapy.Field()
        terrace_exists = scrapy.Field()
        terrace_surface = scrapy.Field()
        terrace_orientation = scrapy.Field()
        garden_exists = scrapy.Field()
        garden_surface = scrapy.Field()
        garden_orientation = scrapy.Field()
        swimming_pool = scrapy.Field()
        state_of_building = scrapy.Field()
        living_surface = scrapy.Field()
        url = scrapy.Field()
        epc = scrapy.Field()
        consumption_per_m2 = scrapy.Field()  # drop this item
        parking_count_inside = scrapy.Field()
        parking_count_outside = scrapy.Field()
        parking_box_count = scrapy.Field()

        # extra fields
        cadastral_income = scrapy.Field()
        has_starting_price = scrapy.Field()  # what is this?
        transaction_subtype = scrapy.Field()  # what is this? 'BUY_REGULAR'
        heating_type = scrapy.Field()
        is_holiday_property = scrapy.Field()
        gas_water_electricity_exists = scrapy.Field()
        sewer_exists = scrapy.Field()
        sea_view_exists = scrapy.Field()