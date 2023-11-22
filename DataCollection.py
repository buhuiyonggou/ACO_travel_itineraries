import requests
from globalDefinition import GOOGLE_MAP_API

distance_cache = {}


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
        print(distance, duration)
        return distance, duration
    else:
        print(f"No route found between {origin_name} and {destination_name}.")
        return 0, 0


def get_driving_cost_cached(origin_name, destination_name):
    cache_key = (origin_name, destination_name)

    if cache_key in distance_cache:
        return distance_cache[cache_key]

    distance, duration = get_driving_cost(origin_name, destination_name)
    distance_cache[cache_key] = (distance, duration)
    return distance, duration


def get_city_population(city_name, country_name):
    base_url = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-1000/records"

    params = {
        'where': f"name='{city_name}' AND cou_name_en='{country_name}'"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        if results:
            city_data = results[0] # suppose the first result is what we need
            population = city_data.get('population', '未知')
            return population
        else:
            print(f"未找到{city_name}, {country_name}的数据")
            return None
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return None
