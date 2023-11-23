TRAVEL_TARGET_RATIO = 0.01
import random


class City:
    def __init__(self, name, country, stays_limit):
        self.name = name
        self.country = country
        self.stays_limit = stays_limit
        # self.actual_stays = 1
        self.population = 0
        self.amenity_score_per_day = 0
        # record travel time from the prior city
        # self.travel_time_from_prior = travel_time_from_prior

    def assign_amenity_score(self):
        self.amenity_score_per_day = round(self.population * TRAVEL_TARGET_RATIO, 2)

    # def assign_random_stays(self):
    #     self.actual_stays = random.randint(1, self.stays_limit)

    # def update_actual_stays(self, allow_days):
    #     self.actual_stays = allow_days
