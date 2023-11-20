import numpy as np


class PheromoneMatrix:
    def __init__(self, num_cities, initial_pheromone, evaporation_rate):
        self.matrix = np.full((num_cities, num_cities), initial_pheromone)
        self.evaporation_rate = evaporation_rate

    def update_pheromene(self, ant, pheromone_deposit, city_to_index):
        self.matrix *= 1 - self.evaporation_rate

        for i in range(len(ant.visited) - 1):
            from_index = city_to_index[ant.visited[i]]
            to_index = city_to_index[ant.visited[i + 1]]
            self.matrix[from_index][to_index] += pheromone_deposit / ant.total_distance

    def get_pheromone_level(self, from_city, to_city):
        return self.matrix[from_city][to_city]
