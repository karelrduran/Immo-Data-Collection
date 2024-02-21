class Property(object):

    def __init__(self,
                 property_id: str,
                 locality_name: str,
                 postal_code: str,
                 property_price: float,
                 property_type: str,
                 property_sub_type: str,
                 sale_type: str,
                 number_of_rooms: int,
                 living_area: float,
                 number_of_facades: int,
                 state_of_building: str,
                 equipped_kitchen: bool = False,
                 furnished: bool = False,
                 open_fire: bool = False,
                 terrace: bool = False,
                 garden: bool = False,
                 surface_of_good: bool = False,
                 swimming_pool: bool = False
                 ):
        self.property_id: str = property_id
        self.locality_name: str = locality_name
        self.postal_code: str = postal_code
        self.property_price: float = property_price
        self.property_type: str = property_type
        self.property_sub_type = property_sub_type
        self.sale_type: str = sale_type
        self.number_of_rooms: int = number_of_rooms
        self.living_area: float = living_area
        self.equipped_kitchen: bool = equipped_kitchen
        self.furnished: furnished
        self.openfire = open_fire
        self.terrace: bool = terrace
        self.garden: bool = garden
        self.surface_of_good: bool = surface_of_good
        self.number_of_facades: int = number_of_facades
        self.swimming_pool: bool = swimming_pool
        self.state_of_building: str = state_of_building

    def __str__(self):
        pass