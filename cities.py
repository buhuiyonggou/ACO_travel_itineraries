import math

RADIUS_EARTH = 6371
TRAVEL_TARGET_RATIO = 0.05


class City:
    def __init__(self, name, latitude, longitude, stays, population):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.stays = stays
        self.population = population
        self.ammenity_score_per_day = population * TRAVEL_TARGET_RATIO

    def distance_to(self, other_city):
        lat1, lon1 = map(math.radians, [self.latitude, self.longitude])
        lat2, lon2 = map(math.radians, [other_city.latitude, other_city.longitude])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = RADIUS_EARTH * c

        return distance
