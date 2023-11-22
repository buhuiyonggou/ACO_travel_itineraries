import random
from DataCollection import get_driving_cost_cached
from globalDefinition import GAS_CONSUMPTION_RATIO


class Ant:
    def __init__(self, start_city, matching_lodging):
        self.current_city = start_city
        self.visited = [start_city]
        self.total_cost = matching_lodging.price * start_city.actual_stays
        self.total_distance = 0
        # count the total time expenditure on the route
        self.total_time_on_route = 0
        # count the total time expenditure on accommodations
        self.total_time_stays = start_city.actual_stays
        self.total_time = self.get_total_time()

    def visit_city(self, city, distance, current_travel_time):
        self.total_cost += distance * GAS_CONSUMPTION_RATIO
        self.total_time_on_route += current_travel_time
        self.total_distance += distance
        self.current_city = city
        self.visited.append(city)

    def update_lodging_cost(self, city, lodging):
        # Find the corresponding lodging cost for the city
        lodging_cost = next(lodge.price for lodge in lodging if lodge.city == city.name)
        self.total_cost += city.actual_stays * lodging_cost
        self.total_time_stays += city.actual_stays

    def can_travel_more(self, maximum_day, budget):
        return self.total_cost < budget and self.total_time < maximum_day

    # the probablity equals: pheromone_level of current path/total probabilities of all unvisited path
    def calculate_probabilities(self, pheromone_matrix, city_to_index, alpha, beta):
        probabilities = {}
        total = 0
        for city in city_to_index.keys():
            if city not in self.visited:
                index_current = city_to_index[self.current_city]
                index_target = city_to_index[city]
                pheromone_level = pheromone_matrix.get_pheromone_level(
                    index_current, index_target
                )
                distance, durantion = get_driving_cost_cached(
                    self.current_city.name, city.name
                )
                probabilities[city] = (pheromone_level**alpha) * (
                    (1.0 / distance) ** beta
                )
                total += probabilities[city]
        # get prob = next_chosen_path/total prob of unvisited cities
        probabilities = {city: prob / total for city, prob in probabilities.items()}
        return probabilities

    def choose_next_city(self, probabilities):
        if not probabilities:  # Check if the probabilities dictionary is empty
            return None  # or handle this case as needed
        cities, probs = zip(*probabilities.items())
        next_city = random.choices(cities, weights=probs, k=1)[0]
        return next_city

    def get_amenity_score(self, ant_path):
        amenity_score = 0
        for city in ant_path:
            amenity_score += city.amenity_score_per_day * city.actual_stays
        return amenity_score

    def get_total_time(self):
        return self.total_time_on_route + self.total_time_stays

    def hasVisited(self, city):
        return city in self.visited

    def current_path(self):
        return self.visited

    def reset(self, start_city):
        self.current_city = start_city
        self.visited = [start_city]
        self.total_cost = 0
        self.total_distance = 0
