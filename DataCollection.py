import requests
import matplotlib.pyplot as plt
from globalDefinition import GOOGLE_MAP_API
from test_3_dataset import distance_cache, location_cache

# distance_cache = {}
# location_cache = {}

def get_coordinates(city_name):
    params = {"address": city_name, "key": GOOGLE_MAP_API}
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json", params=params
    )
    data = response.json()
    if "results" in data and len(data["results"]) > 0:
        latitude = data["results"][0]["geometry"]["location"]["lat"]
        longitude = data["results"][0]["geometry"]["location"]["lng"]
        return latitude, longitude
    else:
        print(f"Coordinates not found for {city_name}")
        return None, None


def get_driving_cost(origin_name, destination_name):
    origin_lat, origin_lng = get_coordinates(origin_name)
    dest_lat, dest_lng = get_coordinates(destination_name)

    if origin_lat is None or dest_lat is None:
        return 0

    location_cache[origin_name]= (origin_lng,origin_lat)
    location_cache[destination_name]= (dest_lng,dest_lat)

    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "key": GOOGLE_MAP_API,
        "mode": "driving",
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json", params=params
    )
    data = response.json()

    if "routes" in data and len(data["routes"]) > 0:
        distance = data["routes"][0]["legs"][0]["distance"]["value"] / 1000  # km
        duration = data["routes"][0]["legs"][0]["duration"]["value"] / 3600 / 24  # day
        return distance, duration
    else:
        print(f"No route found between {origin_name} and {destination_name}.")
        return 0, 0


def get_driving_cost_cached(origin_name, destination_name):
    cache_key = (origin_name, destination_name)

    if cache_key in distance_cache:
        return distance_cache[cache_key]

    # distance, duration = get_driving_cost(origin_name, destination_name)
    # print(
    #     f"distance between {origin_name} and {destination_name} is {distance}, spending {round(24* duration, 2)} hours"
    # )
    # distance_cache[cache_key] = (distance, duration)
    # return distance, duration

def get_location_cached(location):
    cache_key = location
    if cache_key in location:
        return location_cache[cache_key]
    return None,None

def get_city_population(city_name, country_name):
    base_url = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-1000/records"

    params = {"where": f"name='{city_name}' AND cou_name_en='{country_name}'"}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            city_data = results[0]  # suppose the first result is what we need
            population = city_data.get("population", "unknown")
            return population
        else:
            print(f"Can't find data from {city_name}, {country_name}")
            return None
    else:
        print(f"request failed: {response.status_code}")
        return None


# def test_get_coordinates(cities):
#     coords = {}
#     for city in cities:
#         lat, lon = get_coordinates(city)
#         coords[city] = (lat, lon)
#     return coords


# def test_get_driving_cost(routes):
#     costs = {}
#     for origin, destination in routes:
#         distance, duration = get_driving_cost(origin, destination)
#         costs[(origin, destination)] = (distance, duration)
#     return costs


# test_cities = ["New York", "London", "Tokyo"]
# test_routes = [("New York", "Washington"), ("London", "Manchester")]

# city_coords = test_get_coordinates(test_cities)
# route_costs = test_get_driving_cost(test_routes)

# plt.figure(figsize=(10, 5))
# plt.bar(city_coords.keys(), [coord[0]
#         for coord in city_coords.values()], label='Latitude')
# plt.bar(city_coords.keys(), [
#         coord[1] for coord in city_coords.values()], label='Longitude', alpha=0.7)
# plt.xlabel('City')
# plt.ylabel('Coordinates')
# plt.title('City Geographical Coordinates')
# plt.legend()
# plt.show()

# plt.figure(figsize=(10, 5))
# plt.bar(range(len(route_costs)), [
#         cost[0] for cost in route_costs.values()], label='Distance (km)')
# plt.xticks(range(len(route_costs)), labels=[
#            f"{k[0]} to {k[1]}" for k in route_costs.keys()])
# plt.ylabel('Distance')
# plt.title('Driving Distance Between Cities')
# plt.legend()
# plt.show()


# def test_get_city_population(cities):
#     populations = {}
#     for city, country in cities:
#         pop = get_city_population(city, country)
#         populations[(city, country)] = pop
#     return populations


# test_cities_countries = [
#     ("Tokyo", "Japan"), ("New York City", "United States"), ("London", "United Kingdom")]

# city_populations = test_get_city_population(test_cities_countries)

# plt.figure(figsize=(10, 5))
# plt.bar([f"{k[0]}, {k[1]}" for k in city_populations.keys()],
#         city_populations.values())
# plt.xlabel('City, Country')
# plt.ylabel('Population')
# plt.title('City Populations')
# plt.show()
