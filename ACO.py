import random
from PheromoneMatrix import PheromoneMatrix
from Ant import Ant
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
from Greedy import greedy
from test_cases import Case1, Case2, Case3
from matplotlib import pyplot as plt

TOTAL_BUDGET = Case3[2]
TOTAL_DAYS = Case3[3]
NUM_ANTS = 200
NUM_ITERATIONS = 100

cities = Case3[0]

lodging = Case3[1]

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

# reset visited path for ants but do not change pheromones on paths
for iteration in range(NUM_ITERATIONS):
    ants = []
    for _ in range(NUM_ANTS):
        random_city = random.choice(cities)
        matching_lodging = next(
            lodge for lodge in lodging if lodge.city == random_city.name
        )
        ants.append(Ant(random_city, matching_lodging))

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
            amenity_score = round(ant.get_amenity_score(ant.visited))
            ant.visit_city(
                ant.visited[0],
                distance_back,
                travel_time_back,
            )
            tours.append(ant.visited)

            path_string = "->".join(city.name for city in ant.current_path())
            itinerary = {
                "best_amenity_score": amenity_score,
                "best_tour": ant.current_path(),
                "best_cost": round(ant.total_cost),
                "best_ant": ant,
                "best_tour_path": path_string,
                "best_distance" :ant.total_distance,

            }
            if len(top_5_itinerary) == 5 and (
                amenity_score > top_5_itinerary[-1]["best_amenity_score"]
                or (
                    amenity_score == top_5_itinerary[-1]["best_amenity_score"]
                    and ant.total_cost < top_5_itinerary[-1]["best_amenity_score"]
                )
            ):
                top_5_itinerary.pop()

            if len(top_5_itinerary) < 5 and all(
                isinstance(itinerary["best_cost"], (int, float))
                and itinerary["best_cost"] != existing_itinerary["best_cost"]
                for existing_itinerary in top_5_itinerary
            ):
                top_5_itinerary.append(itinerary)
                top_5_itinerary = sorted(
                    top_5_itinerary,
                    key=lambda x: (-x["best_amenity_score"], x["best_cost"]),
                )

            best_amenity_score = top_5_itinerary[0]["best_amenity_score"]
            best_tour = top_5_itinerary[0]["best_tour"]
            best_cost = top_5_itinerary[0]["best_cost"]
            best_ant = top_5_itinerary[0]["best_ant"]
            best_tour_path = top_5_itinerary[0]["best_tour_path"]
            best_distance = top_5_itinerary[0]["best_distance"]

    cov[iteration + 1] = best_distance/best_amenity_score
    # Update the pheromone matrix
    for ant in ants:
        pheromone_matrix.update_pheromene(ant, PHEROMONE_DEPOSIT, city_to_index)
try:
    print("Top 5 Path:")
    for index, itinerary in enumerate(top_5_itinerary):
        print(
            index + 1,
            " ",
            itinerary["best_tour_path"],
            " ",
            itinerary["best_amenity_score"],
            " ",
            itinerary["best_cost"],
            " ",
            itinerary["best_ant"].total_time,
            " ",
            itinerary["best_ant"].total_time_on_route,
            " ",
            itinerary["best_ant"].total_time_stays
        )
        print(
            "Stay in days:",
            [itinerary["best_ant"].stay_in_cities[city.name] for city in itinerary["best_ant"].current_path()][:-1],
        )
    # Greedy Result
    greedy_start_city = best_ant.visited[0]
    greedy_matching_lodging = next(
        lodge for lodge in lodging if lodge.city == greedy_start_city.name
    )
    greedy_ant = Ant(greedy_start_city, greedy_matching_lodging)
    # Follow the same stay in each city as best ant
    greedy_ant.stay_in_cities = best_ant.stay_in_cities
    greedy_ant.total_cost = greedy_matching_lodging.price * greedy_ant.stay_in_cities[greedy_start_city.name]
    greedy_ant.total_time_stays = greedy_ant.stay_in_cities[greedy_start_city.name]
    greedy_ant.total_time = greedy_ant.total_time_on_route + greedy_ant.total_time_stays
    greedy(greedy_ant)

    # plot the best graph
    figure, axis = plt.subplots(2, 1, figsize=(7, 8))
    figure.tight_layout(pad=5)
    selected_ant = None
    for i in range(2):
        if i == 0:
            selected_ant = best_ant
        else:
            selected_ant = greedy_ant

        graph_dict = {}
        z_values = []
        for index, city in enumerate(selected_ant.current_path()):
            graph_dict[index] = get_location_cached(city.name)
            z_values.append(city.name)
        x_values, y_values = zip(*graph_dict.values())
        axis[i].plot(x_values, y_values, "k*-")
        for index, (x, y, z) in enumerate(list(zip(x_values, y_values, z_values))[:-1]):
            axis[i].annotate(
                "{},{}".format(index, z),
                (x, y),  # these are the coordinates to position the label
                xytext=(0, 10),  # distance from text to points (x,y)
                ha="center",  # horizontal alignment can be left, right or center
                textcoords="offset points",  # how to position the text
            )
        for start, end in zip(
            graph_dict, list(graph_dict.keys())[1:-1] + list(graph_dict.keys())[:1]
        ):
            start_pos, end_pos = graph_dict[start], graph_dict[end]
            mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
            axis[i].arrow(
                start_pos[0],
                start_pos[1],
                mid_pos[0] - start_pos[0],
                mid_pos[1] - start_pos[1],
                head_width=0.2,
                head_length=0.2,
                fc="black",
            )
        ax = axis[i]
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        axis[i].set_xlabel("longitude")
        axis[i].set_ylabel("latitude")
        axis[i].text(
            0.90,
            0.95,
            f"Distance: {round(selected_ant.total_distance)} km",
            fontsize=8,
            color="black",
            ha="left",
            va="top",
            transform=ax.transAxes,
        )
        axis[i].text(
            0.90,
            0.90,
            f"Cost: {round(selected_ant.total_cost)}",
            fontsize=8,
            color="black",
            ha="left",
            va="top",
            transform=ax.transAxes,
        )
        if i == 0:
            axis[i].set_title("Path of itinerary using ant colony algorithm", pad=20)
        else:
            axis[i].set_title("Path of itinerary using greedy algorithm", pad=20)

    # plot covergent graph
    plt.figure(2)
    plt.plot(list(cov.keys()), list(cov.values()))
    plt.xlabel("iteration")
    plt.ylabel("Distance/Amenity score")
    plt.title("convergence curve")
    plt.show()

except TypeError:
    print(
        "No optimal tour found within the given constraints. Consider extending the time span or increasing the budget."
    )
