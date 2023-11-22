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

TOTAL_BUDGET = 3000
TOTAL_DAYS = 5
NUM_ANTS = 100
NUM_ITERATIONS = 100

cities = [
    City(name="Tokyo", country="Japan", stays_limit=5),
    City(name="Kamakura", country="Japan", stays_limit=2),
    City(name="Hakone", country="Japan", stays_limit=3),
    # City(name="Fujikawaguchiko", country="Japan", stays_limit=3),
    # City(name="Numazu", country="Japan", stays_limit=2),
    # City(name="Shimoda", country="Japan", stays_limit=2),
    # City(name="Atami", country="Japan", stays_limit=2),
]

lodging = [
    Lodging("Tokyo", 150),
    Lodging("Kamakura", 100),
    Lodging("Hakone", 250),
    # Lodging("Fujikawaguchiko", 240),
    # Lodging("Numazu", 90),
    # Lodging("Shimoda", 280),
    # Lodging("Atami", 120),
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

# reset visited path for ants but do not change pheromones on paths
for iteration in range(NUM_ITERATIONS):
    random_city = random.choice(cities)
    matching_lodging = next(
        lodge for lodge in lodging if lodge.city == random_city.name
    )
    ants = [Ant(random_city, matching_lodging) for _ in range(NUM_ANTS)]

    for ant in ants:
        probabilities = ant.calculate_probabilities(
            pheromone_matrix, city_to_index, ALPHA, BETA
        )
        if not probabilities:
            continue
        next_city = ant.choose_next_city(probabilities)
        if next_city is not None:
            distance, travel_time = get_driving_cost_cached(
                ant.current_city.name, next_city.name
            )

        while ant.can_travel_more(TOTAL_DAYS, TOTAL_BUDGET) and len(ant.visited) < len(
            cities
        ):
            probabilities = ant.calculate_probabilities(
                pheromone_matrix, city_to_index, ALPHA, BETA
            )
            if not probabilities:
                break
            next_city = ant.choose_next_city(probabilities)
            if next_city is not None:
                distance, travel_time = get_driving_cost_cached(
                    ant.current_city.name, next_city.name
                )
                # then update visited city
                # then update lodging cost for the new city
                ant.visit_city(next_city, distance, travel_time)
                ant.update_lodging_cost(next_city, lodging)
        # record the complete path for each ant
        distance_back, travel_time_back = get_driving_cost_cached(
            ant.visited[len(cities) - 1].name, ant.visited[0].name
        )
        if len(ant.visited) == len(cities) and ant.can_travel_more(
            TOTAL_DAYS - travel_time_back,
            TOTAL_BUDGET - distance_back * GAS_CONSUMPTION_RATIO,
        ):
            # exclude duplicated scores of the starting point
            amenity_score = ant.get_amenity_score(ant.visited[:-1])
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

    # Update the pheromone matrix
    for ant in ants:
        pheromone_matrix.update_pheromene(ant, PHEROMONE_DEPOSIT, city_to_index)

# print("Tours:", [[city.name for city in tour] for tour in tours])
print("Best Tour:", [city.name for city in best_tour])
print("Stay in days:", [city.actual_stays for city in best_tour])
print(
    "Got scores:",
    [round(city.amenity_score_per_day * city.actual_stays, 2) for city in best_tour][
        :-1
    ],
)
print("Total cost", ant.total_cost)
print("Amenity Score:", best_amenity_score)
