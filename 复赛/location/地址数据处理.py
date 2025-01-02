import os
import requests
import json
import time
import random
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 设置 GitHub Token（推荐使用环境变量）
GITHUB_TOKEN = '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'

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

geolocator = Nominatim(user_agent="openmonitor_geocoder")

def clean_location(location):
    if not location:
        return None
    location = location.strip()

    # 标准化常见模糊描述
    fuzzy_locations = {
        "Worldwide": None,
        "Earth": None,
        "The Internet": None,
        "Global": None,
        "GitHub": None,
        "Not provided": None,
        "SG": "Singapore",
        "Your home": None,
        "Ethereum Blockchain": None,
        "@argoproj": None,
        "pkg.devDependencies": None,
        "The clouds": None,
        "Git Earth": None,
        "Everywhere": None,
        "GitHub": None
    }

    if location in fuzzy_locations:
        return fuzzy_locations[location]

    return location

def clean_data(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        entry['location'] = clean_location(entry.get('location'))

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Cleaned data saved to {output_file}")

def get_github_user_info(username, retries=3):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        # 处理速率限制
        if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            wait_seconds = reset_time - int(time.time()) + 5  # 增加5秒缓冲
            print(f"Rate limit exceeded. Waiting for {wait_seconds} seconds.")
            time.sleep(wait_seconds)
            response = requests.get(url, headers=HEADERS, timeout=10, verify=False)  # 重试请求
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as ssl_err:
        if retries > 0:
            print(f"SSL error occurred: {ssl_err} for user {username}. Retrying ({retries})...")
            time.sleep(5)
            return get_github_user_info(username, retries - 1)
        else:
            print(f"Failed to get user info for {username} after retries due to SSL error.")
            return None
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP error occurred: {errh} for user {username}")
    except requests.exceptions.RequestException as err:
        print(f"Request failed: {err} for user {username}")
    return None

def update_missing_locations(data, output_file):
    user_cache = {}
    for entry in data:
        if entry['location'] is None:
            owner = entry['owner']
            if owner in user_cache:
                location = user_cache[owner]
            else:
                user_info = get_github_user_info(owner)
                if user_info:
                    location = user_info.get('location', None)
                else:
                    location = None
                user_cache[owner] = location
                time.sleep(1)  # 避免触发速率限制

            # 清理位置
            location = clean_location(location)
            entry['location'] = location

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated data with missing locations saved to {output_file}")

def refine_location(location):
    if not location:
        return None

    # 标准化常见国家或城市名称
    country_centers = {
        "United States of America": "Washington, D.C., USA",
        "USA": "Washington, D.C., USA",
        "United States": "Washington, D.C., USA",
        "China": "Beijing, China",
        "Cyprus": "Nicosia, Cyprus",
        "Singapore": "Singapore",
        "San Francisco, CA": "San Francisco, California, USA",
        "San Francisco": "San Francisco, California, USA",
        "Redmond, WA": "Redmond, Washington, USA",
        "Germany": "Berlin, Germany",
        "Czech Republic": "Prague, Czech Republic",
        "The Netherlands": "Amsterdam, Netherlands",
        "Finland": "Helsinki, Finland",
        "South Africa": "Cape Town, South Africa",
        "Israel": "Tel Aviv, Israel",
        "Brazil": "Brasília, Brazil",
        "Antarctica": None,
        "Paris": "Paris, France",
        "Berlin & Worldwide": "Berlin, Germany",
        "NYC + Paris": "New York City, USA; Paris, France",
        "San Francisco, Ironwood, Denver, London, Berlin, Melbourne, Portland": "San Francisco, CA, USA; Denver, CO, USA; London, England; Berlin, Germany; Melbourne, Australia; Portland, OR, USA",
        "Not provided": None,
        "Git Earth": None,
        "Earth": None,
        "Global": None,
        "The clouds": None,
        "The Internet": None
        # 添加更多的标准化地点
    }

    if location in country_centers:
        return country_centers[location]

    return location

def refine_locations(data, output_file):
    for entry in data:
        location = entry.get('location')
        refined = refine_location(location)
        if refined:
            entry['location'] = refined
        else:
            entry['location'] = None  # 或者保持原样，根据需要处理

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Refined location data saved to {output_file}")

def load_country_geodata(geojson_path=r'location\国家边界.json'):
    # 加载国家边界 GeoJSON
    countries = gpd.read_file(geojson_path)
    print("GeoDataFrame 列名:", countries.columns)  # 添加这一行以检查列名
    return countries

def get_country_polygon(countries, country_name):
    # 直接使用 'name' 列进行匹配
    country = countries[countries['name'].str.lower() == country_name.lower()]
    if not country.empty:
        return country.iloc[0].geometry
    else:
        print(f"未找到国家边界: {country_name}")
        return None

def generate_random_point_within_polygon(polygon):
    min_x, min_y, max_x, max_y = polygon.bounds
    while True:
        random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if polygon.contains(random_point):
            return random_point.y, random_point.x  # 返回 (latitude, longitude)

def randomize_country_locations(data, countries, output_file):
    for entry in data:
        location = entry.get('location')
        if location and entry.get('latitude') is None and entry.get('longitude') is None:
            # 判断是否为国家级别的位置
            # 这里假设已经细化到具体国家名称
            country_polygon = get_country_polygon(countries, location)
            if country_polygon:
                lat, lon = generate_random_point_within_polygon(country_polygon)
                entry['latitude'] = lat
                entry['longitude'] = lon
                print(f"Randomized location for {entry['repo']} in {location}: ({lat}, {lon})")
                time.sleep(1)  # 避免触发速率限制
            else:
                # 无法找到国家边界，保持原样或处理为 None
                entry['latitude'] = None
                entry['longitude'] = None
                print(f"Could not randomize location for {entry['repo']} in {location}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Randomized country locations saved to {output_file}")

def geocode_location(location, geolocator, cache):
    if not location:
        return None, None
    if location in cache:
        cached = cache[location]
        return cached.get('latitude'), cached.get('longitude')
    try:
        geo = geolocator.geocode(location, timeout=10)
        if geo:
            cache[location] = {'latitude': geo.latitude, 'longitude': geo.longitude}
            return geo.latitude, geo.longitude
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error for location {location}: {e}")
    cache[location] = {'latitude': None, 'longitude': None}
    return None, None

def geocode_data_with_cache(data, output_file, cache_file='geocode_cache.json'):
    # 加载缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

    for entry in data:
        location = entry.get('location')
        if location and (entry.get('latitude') is None or entry.get('longitude') is None):
            lat, lon = geocode_location(location, geolocator, cache)
            entry['latitude'] = lat
            entry['longitude'] = lon
            if lat and lon:
                print(f"Geocoded: {location} -> ({lat}, {lon})")
            else:
                print(f"Failed to geocode: {location}")
            time.sleep(1)  # 避免触发速率限制

    # 保存缓存
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Geocoded data saved to {output_file}")

def main():
    # 文件路径
    input_file = r'location\repo_locations.json'
    cleaned_file = r'location\repo_locations_cleaned.json'
    updated_file = 'repo_locations_updated.json'
    refined_file = 'repo_locations_refined.json'
    randomized_file = 'repo_locations_randomized.json'
    geocoded_file = 'repo_locations_final.json'

    # 步骤 1: 清理数据
    clean_data(input_file, cleaned_file)

    # 步骤 2: 更新缺失的位置信息
    with open(cleaned_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    update_missing_locations(data, updated_file)

    # 步骤 3: 细化位置
    with open(updated_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    refine_locations(data, refined_file)

    # 步骤 4: 随机分布国家级别的项目位置
    countries = load_country_geodata()
    with open(refined_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    randomize_country_locations(data, countries, randomized_file)

    # 步骤 5: 获取经纬度（对于已随机分配的国家级别位置，此步骤可能已经完成）
    with open(randomized_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    geocode_data_with_cache(data, geocoded_file, 'geocode_cache.json')

    print("All processing steps completed.")

if __name__ == "__main__":
    main()
