TRAVEL_TARGET_RATIO = 0.01


class City:
    def __init__(self, name, latitude, longitude, stays, population):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.stays = stays
        self.population = population
        self.amenity_score_per_day = round(population * TRAVEL_TARGET_RATIO, 2)
