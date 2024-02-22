from enum import Enum


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