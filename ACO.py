import random
from PheromoneMatrix import PheromoneMatrix
from Ant import Ant
from cities import City
from lodging import Lodging
from DataCollection import get_driving_cost_cached, get_city_population
from globalDefinition import (
    ALPHA,
    BETA,
    GAS_CONSUMPTION_RATIO,
    PHEROMONE_DEPOSIT,
    INITIAL_PHEROMONE,
    EVAPORATION_RATE,
)

TOTAL_BUDGET = 5000
TOTAL_DAYS = 11
NUM_ANTS = 150
NUM_ITERATIONS = 100

cities = [
    City(name="Tokyo", country="Japan", stays_limit=5),
    City(name="Kamakura", country="Japan", stays_limit=2),
    City(name="Hakone", country="Japan", stays_limit=3),
    City(name="Fujikawaguchiko", country="Japan", stays_limit=3),
    City(name="Numazu", country="Japan", stays_limit=2),
    City(name="Shimoda", country="Japan", stays_limit=2),
    City(name="Atami", country="Japan", stays_limit=2),
]

lodging = [
    Lodging("Tokyo", 150),
    Lodging("Kamakura", 100),
    Lodging("Hakone", 250),
    Lodging("Fujikawaguchiko", 240),
    Lodging("Numazu", 90),
    Lodging("Shimoda", 280),
    Lodging("Atami", 120),
]

city_to_index = {city: i for i, city in enumerate(cities)}
# Initialize the pheromone matrix
pheromone_matrix = PheromoneMatrix(len(cities), INITIAL_PHEROMONE, EVAPORATION_RATE)

# record successful paths
tours = list()
best_tour = None
best_amenity_score = 0

for city in cities:
    city.population = get_city_population(city.name, city.country)
    city.assign_amenity_score()
    # city.assign_random_stays()

# reset visited path for ants but do not change pheromones on paths
for iteration in range(NUM_ITERATIONS):
    random_city = random.choice(cities)
    matching_lodging = next(
        lodge for lodge in lodging if lodge.city == random_city.name
    )
    ants = [Ant(random_city, matching_lodging) for _ in range(NUM_ANTS)]

    for ant in ants:
        while ant.can_travel_more(TOTAL_DAYS, TOTAL_BUDGET) and len(ant.visited) < len(
            cities
        ):
            probabilities = ant.calculate_probabilities(
                pheromone_matrix, city_to_index, ALPHA, BETA
            )
            if not probabilities:
                break
            # decide the next city
            next_city = ant.choose_next_city(probabilities)
            if next_city is not None:
                distance, travel_time = get_driving_cost_cached(
                    ant.current_city.name, next_city.name
                )
            # we assume at least one day stay for cities on the route, therefore + 1
            current_residual_time = TOTAL_DAYS - (ant.total_time + travel_time + 1)
            lodging_next = next(
                lodge for lodge in lodging if lodge.city == next_city.name
            )
            current_residual_budget = TOTAL_BUDGET - (
                ant.total_cost
                + distance * GAS_CONSUMPTION_RATIO
                + lodging_next.price * 1
            )
            print(
                f"current_residual_time: {current_residual_time}, used total time: {ant.total_time}, "
                f"used travel time:{ant.total_time_on_route}, used lodging time:{ant.total_time_stays}, "
                f"current_residual_budget: {current_residual_budget}, used total cost: {ant.total_cost}"
                f"used lodging time:{ant.total_cost},"
            )
            # if we don't have time to get to the next city or can't afford at least one night
            if current_residual_time < 0 or current_residual_budget < 0:
                break
            # if ants can proceed but can not satisfy that day required by random, we decrease stays
            # to limit ants's time and budget under constraints, at least 1 day
            time_constraint = TOTAL_DAYS - (
                ant.total_time + travel_time + ant.stay_in_cities[next_city.name]
            )
            budget_constraint = TOTAL_BUDGET - (
                ant.total_cost
                + distance * GAS_CONSUMPTION_RATIO
                + ant.stay_in_cities[next_city.name] * lodging_next.price
            )

            while (time_constraint < 0 or budget_constraint < 0) and ant.stay_in_cities[
                next_city.name
            ] > 1:
                ant.stay_in_cities[next_city.name] -= 1

            # then update visited city
            # then update lodging cost for the new city
            ant.visit_city(next_city, distance, travel_time)
            ant.update_lodging_cost(next_city, lodging_next)

        # record the complete path for each ant
        distance_back, travel_time_back = get_driving_cost_cached(
            ant.visited[-1].name, ant.visited[0].name
        )
        if len(ant.visited) == len(cities) and ant.can_travel_more(
            TOTAL_DAYS - travel_time_back,
            TOTAL_BUDGET - distance_back * GAS_CONSUMPTION_RATIO,
        ):
            # exclude duplicated scores of the starting point
            amenity_score = ant.get_amenity_score(ant.visited)
            ant.visit_city(
                ant.visited[0],
                distance_back,
                travel_time_back,
            )
            tours.append(ant.visited)
            # Check if the new tour has a higher amenity score and satisfies budget and day constraints
            if amenity_score > best_amenity_score:
                best_amenity_score = amenity_score
                best_tour = ant.current_path()
                best_ant = ant

    # Update the pheromone matrix
    for ant in ants:
        pheromone_matrix.update_pheromene(ant, PHEROMONE_DEPOSIT, city_to_index)

# print("Tours:", [[city.name for city in tour] for tour in tours])
print("Best Tour:", [city.name for city in best_tour])
# please help modify to print the actual stay in days of the best route
print(
    "Stay in days:",
    [best_ant.stay_in_cities[city.name] for city in best_ant.current_path()][:-1],
)
# please help modify to print the scores in days of the best route
print(
    "Got scores:",
    [
        round(city.amenity_score_per_day * best_ant.stay_in_cities[city.name], 2)
        for city in best_ant.current_path()
    ][:-1],
)
print("Total cost", ant.total_cost)
print("Amenity Score:", best_amenity_score)
