import random
from PheromoneMatrix import PheromoneMatrix
from Ant import Ant
from cities import City
from lodging import Lodging
from DataCollection import get_driving_cost_cached, get_city_population,get_location_cached
from globalDefinition import (
    ALPHA,
    BETA,
    GAS_CONSUMPTION_RATIO,
    PHEROMONE_DEPOSIT,
    INITIAL_PHEROMONE,
    EVAPORATION_RATE,
)
from matplotlib import pyplot as plt

TOTAL_BUDGET = 2500
TOTAL_DAYS = 13
NUM_ANTS = 150
NUM_ITERATIONS = 150

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
best_cost = TOTAL_BUDGET
cov = {}
top_5_itinerary = []

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
                distance, travel_time = get_driving_cost_cached(ant.current_city.name, next_city.name)
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
            # print(
            #     f"current_residual_time: {current_residual_time}, used total time: {ant.total_time}, "
            #     f"used travel time:{ant.total_time_on_route}, used lodging time:{ant.total_time_stays}, "
            #     f"current_residual_budget: {current_residual_budget}, used total cost: {ant.total_cost}"
            #     f"used lodging time:{ant.total_cost},"
            # )
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
            ant.visited[-1].name, ant.visited[0].name)
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

            path_string = '->'.join(city.name for city in ant.current_path())
            itinerary = {
                'best_amenity_score' : amenity_score,
                'best_tour' : ant.current_path(),
                'best_cost' : ant.total_cost,
                'best_ant' : ant,
                'best_tour_path': path_string
            }
            if len(top_5_itinerary)==5 and (amenity_score > top_5_itinerary[-1]['best_amenity_score'] 
                or (amenity_score==top_5_itinerary[-1]['best_amenity_score'] and ant.total_cost<top_5_itinerary[-1]['best_amenity_score'])):
                top_5_itinerary.pop()

            if len(top_5_itinerary)<5 and all(path_string not in itinerary['best_tour_path'] for itinerary in top_5_itinerary):
                top_5_itinerary.append(itinerary)
                top_5_itinerary = sorted(top_5_itinerary,key=lambda x:(-x['best_amenity_score'],x['best_cost']))

            best_amenity_score = top_5_itinerary[0]['best_amenity_score']
            best_tour = top_5_itinerary[0]['best_tour']
            best_cost = top_5_itinerary[0]['best_cost']
            best_ant = top_5_itinerary[0]['best_ant']
            best_tour_path = top_5_itinerary[0]['best_tour_path']

    cov[iteration+1] = best_amenity_score
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
print("Total cost", best_cost)
print("Amenity Score:", best_amenity_score)
print("Top 5 Path:")
for index,itinerary in enumerate(top_5_itinerary):   
    print(index+1," ", itinerary['best_tour_path'], " ", itinerary['best_amenity_score'], " ", itinerary['best_cost'])

#plot the best graph
plt.figure(1)
graph_dict = {}
z_values=[]
for index,city in enumerate(best_ant.current_path()):   
    graph_dict[index] =  get_location_cached(city.name)
    z_values.append(city.name)
x_values, y_values = zip(*graph_dict.values())
plt.plot(x_values,y_values,'k*-')
for index,(x,y,z) in enumerate(list(zip(x_values,y_values,z_values))[:-1]):
    plt.annotate('{},{}'.format(index,z),
                 (x,y), # these are the coordinates to position the label
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center', # horizontal alignment can be left, right or center
                 textcoords="offset points" # how to position the text
    )
for start, end in zip(graph_dict, list(graph_dict.keys())[1:-1] + list(graph_dict.keys())[:1]):
    start_pos, end_pos = graph_dict[start], graph_dict[end]
    mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
    plt.arrow(start_pos[0], start_pos[1], mid_pos[0] - start_pos[0], mid_pos[1] - start_pos[1],
              head_width=0.02, head_length=0.02, fc='blue')
    
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xlabel('latitude')
plt.ylabel('longitude')
plt.title('Path of itinerary')

#plot covergent graph
plt.figure(2)
plt.plot(list(cov.keys()),list(cov.values()))
plt.xlabel('iteration')
plt.ylabel('best amenity score')
plt.title('convergence curve')
plt.show()
