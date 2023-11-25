TRAVEL_TARGET_RATIO = 0.01


class City:
    def __init__(self, name, country, stays_limit):
        self.name = name
        self.country = country
        self.stays_limit = stays_limit
        self.population = 0
        self.amenity_score_per_day = 0

    def assign_amenity_score(self):
        self.amenity_score_per_day = round(self.population * TRAVEL_TARGET_RATIO, 2)
