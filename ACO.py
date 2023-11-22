import random, requests
from PheromoneMatrix import PheromoneMatrix
from Ant import Ant
from cities import City
from lodging import Lodging

TOTAL_BUDGET = 8000
TOTAL_DAYS = 10
GAS_CONSUMPTION_RATIO = 0.5
NUM_ANTS = 50
NUM_ITERATIONS = 200
INITIAL_PHEROMONE = 0.5
EVAPORATION_RATE = 0.3
PHEROMONE_DEPOSIT = 10
ALPHA = 1.0
BETA = 1.1

cities = [
    City("Ottawa", 45.4215, -75.6972, stays=1, population=994800),
    City("Toronto", 43.65107, -79.347015, stays=2, population=2930000),
    City("Montreal", 45.5017, -73.5673, stays=2, population=1780000),
    City("Vancouver", 49.2827, -123.1207, stays=2, population=662248),
    City("Edmonton", 53.5461, -113.4938, stays=1, population=981300),
    City("Calgary", 51.0447, -114.0719, stays=2, population=1336000),
]

lodging = [
    Lodging("Ottawa", 180),
    Lodging("Toronto", 200),
    Lodging("Montreal", 150),
    Lodging("Vancouver", 210),
    Lodging("Edmonton", 160),
    Lodging("Calgary", 170),
]

city_to_index = {city: i for i, city in enumerate(cities)}
# Initialize the pheromone matrix
pheromone_matrix = PheromoneMatrix(len(cities), INITIAL_PHEROMONE, EVAPORATION_RATE)

tours = list()
best_tour = None
best_amenity_score = 0
api_key = 'AIzaSyDb6GaNOwz0r7whnH885uJTjzRbCkiplZY'

# 初始化一个字典来存储距离
distance_cache = {}


def get_coordinates(city_name, api_key):
    params = {
        'address': city_name,
        'key': api_key
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json", params=params)
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        print(f"Coordinates not found for {city_name}")
        return None, None


def get_driving_cost(origin_name, destination_name, api_key):
    origin_lat, origin_lng = get_coordinates(origin_name, api_key)
    dest_lat, dest_lng = get_coordinates(destination_name, api_key)

    if origin_lat is None or dest_lat is None:
        return 0

    params = {
        'origin': f'{origin_lat},{origin_lng}',
        'destination': f'{dest_lat},{dest_lng}',
        'key': api_key,
        'mode': 'driving'
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json", params=params)
    data = response.json()

    if 'routes' in data and len(data['routes']) > 0:
        distance = data['routes'][0]['legs'][0]['distance']['value'] / 1000  # km
        duration = data['routes'][0]['legs'][0]['duration']['value'] / 3600 / 24  # day
        print(distance, duration)
        return distance, duration
    else:
        print(f"No route found between {origin_name} and {destination_name}.")
        return 0, 0
    

def get_driving_cost_cached(origin_name, destination_name, api_key):
    cache_key = (origin_name, destination_name)

    if cache_key in distance_cache:
        return distance_cache[cache_key]

    distance, duration = get_driving_cost(
        origin_name, destination_name, api_key)
    distance_cache[cache_key] = (distance, duration)
    return distance, duration

# reset visited path for ants but do not change pheromones on paths
for iteration in range(NUM_ITERATIONS):
    random_city = random.choice(cities)
    matching_lodging = next(
        lodge for lodge in lodging if lodge.city == random_city.name
    )
    ants = [Ant(random_city, matching_lodging) for _ in range(NUM_ANTS)]

    for ant in ants:
        while ant.can_travel_more(TOTAL_DAYS, TOTAL_BUDGET):
            probabilities = ant.calculate_probabilities(
                pheromone_matrix, city_to_index, ALPHA, BETA
            )
            if not probabilities:
                break
            next_city = ant.choose_next_city(probabilities)
            distance, travel_time = get_driving_cost_cached(
                ant.current_city.name, next_city.name, api_key)
            travel_cost = distance * GAS_CONSUMPTION_RATIO
            ant.visit_city(next_city, travel_cost, travel_time)
        # record the complete path for each ant
        tours.append(ant.visited)

        amenity_score = ant.get_amenity_score(ant.visited)
        # Check if the new tour has a higher amenity score and satisfies budget and day constraints
        if (
            ant.total_cost <= TOTAL_BUDGET
            and ant.total_day <= TOTAL_DAYS
            and amenity_score > best_amenity_score
        ):
            best_amenity_score = amenity_score
            best_tour = ant.current_path()

    # Update the pheromone matrix
    for ant in ants:
        pheromone_matrix.update_pheromene(ant, PHEROMONE_DEPOSIT, city_to_index)

# print("Tours:", [[city.name for city in tour] for tour in tours])
print("Best Tour:", [city.name for city in best_tour])
print("Stay in days:", [city.stays for city in best_tour])
print("Got scores:", [city.amenity_score_per_day for city in best_tour])
print("Total cost", ant.total_cost)
print("Amenity Score:", best_amenity_score)
