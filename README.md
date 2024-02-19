# Immo-Data-Colection

- Property ID ["id"]
- Locality name ["property"]["location"]["locality"]
- Postal code ["property"]["postalCode"]
- Price ["transaction"]["sale"]["price"]
- Type of property (house or apartment) ["property"]["type"]
- Subtype of property (bungalow, chalet, mansion, ...) ["property"]["subtype"]
- Type of sale (_note_: exclude life sales)
- Number of rooms
- Living area (area in m²) ["property"]["netHabitableSurface"]
- Equipped kitchen (0/1)
- Furnished (0/1)
- Open fire (0/1)
- Terrace (area in m² or null if no terrace)
- Garden (area in m² or null if no garden)
- Surface of good  
- Number of facades
- Swimming pool (0/1)
- State of building (new, to be renovated, ...)