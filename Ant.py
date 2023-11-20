import random


class Ant:
    def __init__(self, start_city, lodging):
        self.current_city = start_city
        self.visited = [start_city]
        self.total_cost = start_city.stays * lodging.price
        self.total_distance = 0
        self.total_day = self.get_total_days()
        self.amenity_score = self.get_amenity_score()

    def visit_city(self, city, travel_cost):
        self.total_cost += travel_cost
        self.total_distance += self.current_city.distance_to(city)
        self.current_city = city
        self.visited.append(city)

    def can_travel_more(self, maximum_day, budget):
        return self.total_cost < budget and self.total_day < maximum_day

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
                distance = self.current_city.distance_to(city)
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

    def get_amenity_score(self):
        amenity_score = 0
        for city in self.visited:
            amenity_score += city.amenity_score_per_day * city.stays
        return amenity_score

    def get_total_days(self):
        days = 0
        for each in self.visited:
            days += each.stays
        return days

    def hasVisited(self, city):
        return city in self.visited

    def current_path(self):
        return self.visited

    def reset(self, start_city):
        self.current_city = start_city
        self.visited = [start_city]
        self.total_cost = 0
        self.total_distance = 0
