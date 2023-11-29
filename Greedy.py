import random
from PheromoneMatrix import PheromoneMatrix
from Ant import Ant
from cities import City
from lodging import Lodging
from DataCollection import (
    get_driving_cost_cached,
    get_city_population,
    get_location_cached,
)
from globalDefinition import (
    ALPHA,
    BETA,
    GAS_CONSUMPTION_RATIO,
    PHEROMONE_DEPOSIT,
    INITIAL_PHEROMONE,
    EVAPORATION_RATE,
)
from test_cases import Case1, Case2, Case3
from matplotlib import pyplot as plt

cities = Case3[0]
lodging = Case3[1]


         

def greedy(greedy_ant):
    start_city = greedy_ant.visited[0]
    avaliable_cities= [city for city in cities if city.name != start_city.name]
    while len(avaliable_cities) > 0:
        next_city,distance,travel_time = greedy_ant.choose_closest_city(start_city,avaliable_cities)
       
        greedy_ant.visit_city(next_city, distance, travel_time)
        lodging_next = next(
            lodge for lodge in lodging if lodge.city == next_city.name
        )
        greedy_ant.update_lodging_cost(next_city, lodging_next)
        start_city = next_city
        avaliable_cities = [city for city in avaliable_cities if city.name != next_city.name]

    amenity_score = greedy_ant.get_amenity_score(greedy_ant.visited)
    distance_back, travel_time_back = get_driving_cost_cached(
        greedy_ant.visited[-1].name, greedy_ant.visited[0].name
    )
    greedy_ant.visit_city(
        greedy_ant.visited[0],
        distance_back,
        travel_time_back,
    )
    print("Greedy Tour:", [city.name for city in greedy_ant.current_path()])
    print(
        "Greedy Stay in days:",
        [greedy_ant.stay_in_cities[city.name] for city in greedy_ant.current_path()][:-1],
    )
    print("Greedy cost", greedy_ant.total_cost)
    print("Greedy distance:", greedy_ant.total_distance)
    print("Greedy Amenity Score:", amenity_score)      
