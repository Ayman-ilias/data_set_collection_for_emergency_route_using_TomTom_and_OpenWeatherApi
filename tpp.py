import requests
import csv
import time
import json
import math
import os
import random
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    print("⚠️ zoneinfo not found, using local time instead")
    ZoneInfo = None

API_KEY = "dzoitEbLZYaUL1axN8JOnaRNVuacAgHq" 
BACKUP_API_KEY = "B1gAH88VEbZLsLdCfy9Qw8gEkk07TPwc"  
INCIDENT_API_KEY = "gvkzEaCnR712L5zl9SwYxSs2QLkWqhNe"
WEATHER_API_KEY = "5cab911c7bcf3c8fc5be53b7224574e4"  

NY_TZ = ZoneInfo("America/New_York") if ZoneInfo else None

NY_HOLIDAYS = {
    '2024-01-01': 'New Year\'s Day',
    '2024-01-15': 'Martin Luther King Jr. Day',
    '2024-02-19': 'Presidents\' Day',
    '2024-05-27': 'Memorial Day',
    '2024-07-04': 'Independence Day',
    '2024-09-02': 'Labor Day',
    '2024-10-14': 'Columbus Day',
    '2024-11-11': 'Veterans Day',
    '2024-11-28': 'Thanksgiving',
    '2024-12-25': 'Christmas Day',
    '2025-01-01': 'New Year\'s Day',
    '2025-01-20': 'Martin Luther King Jr. Day',
    '2025-02-17': 'Presidents\' Day',
    '2025-05-26': 'Memorial Day',
    '2025-07-04': 'Independence Day',
    '2025-09-01': 'Labor Day',
    '2025-10-13': 'Columbus Day',
    '2025-11-11': 'Veterans Day',
    '2025-11-27': 'Thanksgiving',
    '2025-12-25': 'Christmas Day'
}

MAJOR_EVENTS = {
    '2024-12-25': 'Christmas Day',
    '2025-01-01': 'New Year\'s Day',
    '2025-02-14': 'Valentine\'s Day',
    '2025-03-17': 'St. Patrick\'s Day Parade',
    '2025-07-04': 'July 4th Fireworks',
    '2025-09-01': 'US Open Tennis',
    '2025-11-28': 'Thanksgiving Day Parade',
    '2025-12-31': 'New Year\'s Eve Times Square'
}

RELEVANT_ROADS = [
    "3rd Avenue", "3rd Ave", "Third Avenue",
    "W 42nd St", "West 42nd Street", "42nd Street",
    "E 77th St", "East 77th Street", "77th Street",
    "5th Avenue", "5th Ave", "Fifth Avenue",
    "Park Avenue",
    "Lexington Avenue", "Lexington Ave", "Lex Ave"
]

def check_api_status():
    print("🔍 Checking API key statuses...")
    statuses = {}
    
    # OpenWeatherMap Weather API
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'lat': 40.7536, 'lon': -73.9832, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        statuses['OpenWeather'] = f"{response.status_code} {'OK' if response.status_code == 200 else 'Error'}"
        print(f"   OpenWeatherMap Weather: {statuses['OpenWeather']}")
    except Exception as e:
        statuses['OpenWeather'] = f"Error: {e}"
        print(f"   OpenWeatherMap Weather: {statuses['OpenWeather']}")
    
    # OpenWeatherMap Air Quality API
    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {'lat': 40.7536, 'lon': -73.9832, 'appid': WEATHER_API_KEY}
    try:
        response = requests.get(air_url, params=air_params, timeout=5)
        statuses['AirQuality'] = f"{response.status_code} {'OK' if response.status_code == 200 else 'Error'}"
        print(f"    OpenWeatherMap Air Quality: {statuses['AirQuality']}")
    except Exception as e:
        statuses['AirQuality'] = f"Error: {e}"
        print(f"   OpenWeatherMap Air Quality: {statuses['AirQuality']}")
    
    # TomTom Traffic Flow API (API_KEY)
    flow_url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    flow_params = {'key': API_KEY, 'point': '40.7536,-73.9832', 'unit': 'KMPH'}
    try:
        response = requests.get(flow_url, params=flow_params, timeout=5)
        statuses['Flow_API_KEY'] = f"{response.status_code} {'OK' if response.status_code == 200 else 'Error'}"
        print(f"  TomTom Traffic Flow (API_KEY): {statuses['Flow_API_KEY']}")
    except Exception as e:
        statuses['Flow_API_KEY'] = f"Error: {e}"
        print(f"   🚦 TomTom Traffic Flow (API_KEY): {statuses['Flow_API_KEY']}")
    
    # TomTom Traffic Flow API (BACKUP_API_KEY)
    flow_params['key'] = BACKUP_API_KEY
    try:
        response = requests.get(flow_url, params=flow_params, timeout=5)
        statuses['Flow_BACKUP_API_KEY'] = f"{response.status_code} {'OK' if response.status_code == 200 else 'Error'}"
        print(f"   TomTom Traffic Flow (BACKUP_API_KEY): {statuses['Flow_BACKUP_API_KEY']}")
    except Exception as e:
        statuses['Flow_BACKUP_API_KEY'] = f"Error: {e}"
        print(f"   TomTom Traffic Flow (BACKUP_API_KEY): {statuses['Flow_BACKUP_API_KEY']}")
    
    # TomTom Incidents API
    incidents_url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    bbox = "-73.990,40.745,-73.955,40.785"
    incident_params = {'key': INCIDENT_API_KEY, 'bbox': bbox, 'categoryFilter': '0,1,2,3', 'timeValidityFilter': 'present'}
    try:
        response = requests.get(incidents_url, params=incident_params, timeout=10)
        statuses['Incidents'] = f"{response.status_code} {'OK' if response.status_code == 200 else 'Error'}"
        if response.status_code != 200:
            statuses['Incidents_Error'] = response.text[:200]
            print(f"   TomTom Incidents Key: {statuses['Incidents']} (Details: {statuses['Incidents_Error']})")
        else:
            print(f"   TomTom Incidents Key: {statuses['Incidents']}")
    except Exception as e:
        statuses['Incidents'] = f"Error: {e}"
        print(f"   TomTom Incidents: {statuses['Incidents']}")
    
    return statuses

def is_holiday(date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    return date_str in NY_HOLIDAYS

def get_holiday_name(date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    return NY_HOLIDAYS.get(date_str, "None")

def check_major_event(date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    if date_str in MAJOR_EVENTS:
        return 1, MAJOR_EVENTS[date_str]
    return 0, "None"

def get_road_type(street_name):
    street_lower = street_name.lower()
    if 'ave' in street_lower or 'avenue' in street_lower:
        return 'Avenue'
    elif 'st' in street_lower or 'street' in street_lower:
        return 'Street'
    elif 'blvd' in street_lower or 'boulevard' in street_lower:
        return 'Boulevard'
    elif 'pkwy' in street_lower or 'parkway' in street_lower:
        return 'Parkway'
    elif 'hospital' in street_lower:
        return 'Hospital Area'
    elif 'park' in street_lower:
        return 'Park Area'
    else:
        return 'Street'

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2) * math.sin(delta_lon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_weather_data(lat, lon):
    try:
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        
        air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
        air_params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY
        }
        air_response = requests.get(air_url, params=air_params, timeout=10)
        
        temperature_celsius = 15.0
        weather_condition = 'Clear'
        is_raining = 0
        is_snowing = 0
        precipitation_mm = 0.0
        wind_speed_kmh = 10.0
        visibility_km = 10.0
        humidity_percent = 50
        air_quality_index = 50
        has_wildfire_smoke = 0
        
        if weather_response.status_code == 200:
            data = weather_response.json()
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            rain = data.get('rain', {})
            snow = data.get('snow', {})
            precipitation_mm = rain.get('1h', 0) + snow.get('1h', 0)
            weather_condition = weather.get('main', 'Clear')
            is_raining = 1 if 'rain' in weather_condition.lower() else 0
            is_snowing = 1 if 'snow' in weather_condition.lower() else 0
            temperature_celsius = main.get('temp', 15.0)
            wind_speed_kmh = wind.get('speed', 0) * 3.6
            visibility_km = data.get('visibility', 10000) / 1000
            humidity_percent = main.get('humidity', 50)
        
        if air_response.status_code == 200:
            air_data = air_response.json()
            if 'list' in air_data and len(air_data['list']) > 0:
                aqi_data = air_data['list'][0]
                if 'main' in aqi_data:
                    air_quality_index = aqi_data['main']['aqi'] * 20
                if 'components' in aqi_data:
                    pm25 = aqi_data['components'].get('pm2_5', 0)
                    pm10 = aqi_data['components'].get('pm10', 0)
                    if (pm25 > 35 or pm10 > 50) and visibility_km < 8:
                        has_wildfire_smoke = 1
                        weather_condition = f"{weather_condition} with Smoke"
        
        return {
            'temperature_celsius': temperature_celsius,
            'weather_condition': weather_condition,
            'is_raining': is_raining,
            'is_snowing': is_snowing,
            'precipitation_mm': precipitation_mm,
            'wind_speed_kmh': wind_speed_kmh,
            'visibility_km': visibility_km,
            'humidity_percent': humidity_percent,
            'air_quality_index': air_quality_index,
            'has_wildfire_smoke': has_wildfire_smoke
        }
    except Exception as e:
        print(f"Weather API Error: {e}")
        return get_default_weather()

def get_default_weather():
    return {
        'temperature_celsius': 15.0,
        'weather_condition': 'Clear',
        'is_raining': 0,
        'is_snowing': 0,
        'precipitation_mm': 0.0,
        'wind_speed_kmh': 10.0,
        'visibility_km': 10.0,
        'humidity_percent': 50,
        'air_quality_index': 50,
        'has_wildfire_smoke': 0
    }

def simulate_incidents(lat, lon, congestion_level, is_rush_hour):
    accident_prob = 0.05
    if congestion_level >= 4:
        accident_prob += 0.1
    if is_rush_hour:
        accident_prob += 0.1
    if random.random() < accident_prob:
        severity = random.choice(["Minor", "Moderate", "Major"])
        road = random.choice(RELEVANT_ROADS)
        return {
            'major_accidents_count': 1,
            'accident_severity': severity,
            'accident_roads': road,
            'is_accident_nearby': 1,
            'accident_type': severity
        }
    return {
        'major_accidents_count': 0,
        'accident_severity': "None",
        'accident_roads': "None",
        'is_accident_nearby': 0,
        'accident_type': "None"
    }

def get_traffic_incidents(lat, lon, congestion_level, is_rush_hour):
    incidents_url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    min_lat, max_lat = 40.745, 40.785
    min_lon, max_lon = -73.990, -73.955
    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    params = {
        'key': INCIDENT_API_KEY,
        'bbox': bbox,
        'categoryFilter': '0,1,2,3',
        'timeValidityFilter': 'present'
    }
    
    try:
        response = requests.get(incidents_url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Incidents API Error Details: {response.text[:200]}")
            print("Using simulated incidents as fallback")
            return simulate_incidents(lat, lon, congestion_level, is_rush_hour)
        
        major_accidents_count = 0
        accident_roads = []
        accident_severity = "None"
        
        incidents_data = response.json()
        if 'incidents' in incidents_data:
            for incident in incidents_data['incidents']:
                if incident.get('categoryName', '').lower() in ['accident', 'dangerous conditions']:
                    incident_desc = incident.get('description', '').lower()
                    incident_road = incident.get('roadName', '').lower()
                    is_relevant = any(road.lower() in incident_desc or road.lower() in incident_road for road in RELEVANT_ROADS)
                    if is_relevant:
                        major_accidents_count += 1
                        road_name = incident.get('roadName', 'Unknown Road')
                        if road_name not in accident_roads:
                            accident_roads.append(road_name)
                        desc_lower = incident_desc
                        if any(word in desc_lower for word in ['major', 'severe', 'serious', 'fatal', 'blocked', 'closed']):
                            accident_severity = "Major"
                        elif accident_severity != "Major" and any(word in desc_lower for word in ['minor', 'fender', 'lane']):
                            accident_severity = "Minor"
                        elif accident_severity == "None":
                            accident_severity = "Moderate"
        
        return {
            'major_accidents_count': major_accidents_count,
            'accident_severity': accident_severity,
            'accident_roads': ', '.join(accident_roads[:3]) if accident_roads else "None",
            'is_accident_nearby': 1 if major_accidents_count > 0 else 0,
            'accident_type': accident_severity if major_accidents_count > 0 else "None"
        }
    except Exception as e:
        print(f"Traffic incidents API error: {e}")
        print("Using simulated incidents as fallback")
        return simulate_incidents(lat, lon, congestion_level, is_rush_hour)

def get_persistent_filename(use_timestamp=False):
    if use_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"bryant_park_lenox_hill_traffic_dataset_{timestamp}.csv"
    return "bryant_park_lenox_hill_traffic_dataset.csv"

def load_existing_data(filename):
    if os.path.exists(filename):
        try:
            existing_data = []
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing_data.append(row)
            print(f"📂 Loaded {len(existing_data)} existing records from {filename}")
            return existing_data
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return []
    print(f"📝 Creating new dataset file: {filename}")
    return []

def save_data_to_csv(data, filename, headers):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in data:
                row = {k: str(v) for k, v in row.items()}
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")
        return False

def wait_until_ny_time(hour, minute, timezone="America/New_York"):
    if not NY_TZ:
        print("⚠️ Cannot schedule NY time without zoneinfo, starting immediately")
        return
    now = datetime.now(NY_TZ)
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_time <= now:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    print(f"⏳ Waiting until {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ({wait_seconds/3600:.1f} hours)...")
    time.sleep(wait_seconds)

def get_traffic_data(lat, lon, location_name, road_type="Street"):
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {
        'key': API_KEY,
        'point': f'{lat},{lon}',
        'unit': 'KMPH'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 403:
            print(f"Primary flow key (API_KEY) failed with 403, trying backup key...")
            params['key'] = BACKUP_API_KEY
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"Flow API Error Details: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            flow_data = data.get('flowSegmentData', {})
            current_speed = flow_data.get('currentSpeed', 0)
            free_flow_speed = flow_data.get('freeFlowSpeed', 0)
            travel_time = flow_data.get('currentTravelTime', 0)
            confidence = flow_data.get('confidence', 0)
            
            if free_flow_speed > 0:
                congestion_ratio = current_speed / free_flow_speed
                if congestion_ratio >= 0.8:
                    congestion_level = 1
                elif congestion_ratio >= 0.6:
                    congestion_level = 2
                elif congestion_ratio >= 0.4:
                    congestion_level = 3
                elif congestion_ratio >= 0.2:
                    congestion_level = 4
                else:
                    congestion_level = 5
            else:
                congestion_level = 3
                congestion_ratio = 0.5
            
            now = datetime.now(NY_TZ) if NY_TZ else datetime.now()
            current_date = now.date()
            is_holiday_today = 1 if is_holiday(current_date) else 0
            holiday_name = get_holiday_name(current_date)
            is_major_event, event_name = check_major_event(current_date)
            is_rush_hour = 1 if (7 <= now.hour <= 9) or (17 <= now.hour <= 19) else 0
            
            estimated_distance = 0.15
            normal_time = (estimated_distance / free_flow_speed * 3600) if free_flow_speed > 0 else travel_time
            if 'ave' in location_name.lower():
                estimated_distance = 0.2
            elif 'hospital' in location_name.lower() or 'park' in location_name.lower():
                estimated_distance = 0.1
            
            weather_data = get_weather_data(lat, lon)
            incident_data = get_traffic_incidents(lat, lon, congestion_level, is_rush_hour)
            
            return {
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                'location_name': location_name,
                'latitude': lat,
                'longitude': lon,
                'current_speed_kmh': current_speed,
                'free_flow_speed_kmh': free_flow_speed,
                'travel_time_seconds': travel_time,
                'normal_time_seconds': int(normal_time),
                'congestion_level': congestion_level,
                'congestion_ratio': round(congestion_ratio, 3),
                'confidence': confidence,
                'road_type': road_type,
                'estimated_distance_km': estimated_distance,
                'hour': now.hour,
                'day_of_week': now.weekday(),
                'day_name': now.strftime('%A'),
                'month': now.month,
                'is_weekend': 1 if now.weekday() >= 5 else 0,
                'is_holiday': is_holiday_today,
                'holiday_name': holiday_name,
                'is_morning_rush': 1 if 7 <= now.hour <= 9 else 0,
                'is_evening_rush': 1 if 17 <= now.hour <= 19 else 0,
                'is_rush_hour': is_rush_hour,
                'time_period': get_time_period(now.hour),
                'season': get_season(now.month),
                'route_segment': get_route_segment(location_name),
                'temperature_celsius': weather_data['temperature_celsius'],
                'weather_condition': weather_data['weather_condition'],
                'is_raining': weather_data['is_raining'],
                'is_snowing': weather_data['is_snowing'],
                'precipitation_mm': weather_data['precipitation_mm'],
                'wind_speed_kmh': weather_data['wind_speed_kmh'],
                'visibility_km': weather_data['visibility_km'],
                'humidity_percent': weather_data['humidity_percent'],
                'air_quality_index': weather_data['air_quality_index'],
                'has_wildfire_smoke': weather_data['has_wildfire_smoke'],
                'is_major_event': is_major_event,
                'event_name': event_name,
                'major_accidents_count': incident_data['major_accidents_count'],
                'accident_severity': incident_data['accident_severity'],
                'accident_roads': incident_data['accident_roads'],
                'is_accident_nearby': incident_data['is_accident_nearby'],
                'accident_type': incident_data['accident_type']
            }
        else:
            print(f"API Error for {location_name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting data for {location_name}: {e}")
        return None

def get_time_period(hour):
    if 5 <= hour < 7:
        return "Early Morning"
    elif 7 <= hour < 10:
        return "Morning Rush"
    elif 10 <= hour < 12:
        return "Late Morning"
    elif 12 <= hour < 14:
        return "Lunch Time"
    elif 14 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 20:
        return "Evening Rush"
    elif 20 <= hour < 23:
        return "Evening"
    else:
        return "Night"

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

def get_route_segment(location_name):
    name_lower = location_name.lower()
    if 'bryant' in name_lower or 'start' in name_lower:
        return "Origin"
    elif 'hospital' in name_lower:
        return "Destination"
    elif '42nd' in name_lower:
        return "Initial Street"
    elif 'ave' in name_lower and ('3rd' in name_lower):
        return "Main Avenue"
    elif '77th' in name_lower:
        return "Final Turn"
    else:
        return "Mid Route"

def collect_comprehensive_dataset():
    print("Starting dataset collection...")
    # Check API key statuses
    api_statuses = check_api_status()
    if api_statuses['Incidents'] != "200 OK":
        print("⚠️ TomTom Incident API issue detected. Using simulated incidents as fallback.")
    if api_statuses['OpenWeather'] != "200 OK" or api_statuses['AirQuality'] != "200 OK":
        print("⚠️ OpenWeatherMap API issues detected. Weather data may use defaults.")
    
    route_points = [
        (40.7536, -73.9832, "Bryant_Park_Start", "Park Area"),
        (40.7535, -73.9815, "W_42nd_St_toward_5th_Ave", "Street"),
        (40.7533, -73.9795, "W_42nd_St_5th_Ave_Junction", "Street"),
        (40.7505, -73.9759, "3rd_Ave_42nd_St_Start", "Avenue"),
        (40.7525, -73.9748, "3rd_Ave_45th_St", "Avenue"),
        (40.7545, -73.9737, "3rd_Ave_48th_St", "Avenue"),
        (40.7565, -73.9726, "3rd_Ave_51st_St", "Avenue"),
        (40.7585, -73.9715, "3rd_Ave_54th_St", "Avenue"),
        (40.7605, -73.9704, "3rd_Ave_57th_St", "Avenue"),
        (40.7625, -73.9693, "3rd_Ave_60th_St", "Avenue"),
        (40.7645, -73.9682, "3rd_Ave_63rd_St", "Avenue"),
        (40.7665, -73.9671, "3rd_Ave_66th_St", "Avenue"),
        (40.7685, -73.9660, "3rd_Ave_69th_St", "Avenue"),
        (40.7705, -73.9649, "3rd_Ave_72nd_St", "Avenue"),
        (40.7725, -73.9638, "3rd_Ave_75th_St", "Avenue"),
        (40.7745, -73.9627, "3rd_Ave_77th_St_Junction", "Avenue"),
        (40.7746, -73.9615, "E_77th_St_from_3rd_Ave", "Street"),
        (40.7747, -73.9610, "E_77th_St_mid_block", "Street"),
        (40.7748, -73.9603, "Lenox_Hill_Hospital_Destination", "Hospital Area")
    ]
    
    headers = [
        'timestamp', 'location_name', 'latitude', 'longitude',
        'current_speed_kmh', 'free_flow_speed_kmh', 'travel_time_seconds',
        'normal_time_seconds', 'congestion_level', 'congestion_ratio', 'confidence',
        'road_type', 'estimated_distance_km', 'route_segment',
        'hour', 'day_of_week', 'day_name', 'month', 'is_weekend',
        'is_holiday', 'holiday_name', 'is_morning_rush', 'is_evening_rush',
        'is_rush_hour', 'time_period', 'season',
        'temperature_celsius', 'weather_condition', 'is_raining', 'is_snowing',
        'precipitation_mm', 'wind_speed_kmh', 'visibility_km', 'humidity_percent',
        'air_quality_index', 'has_wildfire_smoke', 'is_major_event', 'event_name',
        'major_accidents_count', 'accident_severity', 'accident_roads',
        'is_accident_nearby', 'accident_type'
    ]
    
    filename = get_persistent_filename()
    collected_data = load_existing_data(filename)
    initial_count = len(collected_data)
    
    print(f"\n📊 Dataset Collection Options:")
    print("1. Quick test (5 rounds, 5-min intervals) - ~25 minutes")
    print("2. Short term (12 rounds, 10-min intervals) - 2 hours")
    print("3. Half day (24 rounds, 30-min intervals) - 12 hours")
    print("4. Full day (48 rounds, 30-min intervals) - 24 hours")
    print("5. Multi-day (96 rounds, 60-min intervals) - 4 days")
    print("6. Custom configuration")
    print("7. Rush Hour collection (NY 3pm-11pm, 5-min intervals) - 8 hours")
    print("8. 8-hour collection (5-min intervals) - 8 hours")
    print("9. 6-hour collection (5-min intervals) - 6 hours")
    print("10. 3-hour collection (5-min intervals) - 3 hours")
    
    choice = input("Enter your choice (1-10): ").strip()
    
    wait_for_time = False
    if choice == "1":
        num_collections = 5
        interval_minutes = 5
    elif choice == "2":
        num_collections = 12
        interval_minutes = 10
    elif choice == "3":
        num_collections = 24
        interval_minutes = 30
    elif choice == "4":
        num_collections = 48
        interval_minutes = 30
    elif choice == "5":
        num_collections = 96
        interval_minutes = 60
    elif choice == "6":
        num_collections = int(input("How many collection rounds? "))
        interval_minutes = int(input("Interval in minutes? "))
    elif choice == "7":
        num_collections = int((8 * 60) / 5)
        interval_minutes = 5
        wait_for_time = True
        start_hour = 15
        end_hour = 23
    elif choice == "8":
        num_collections = int((8 * 60) / 5)
        interval_minutes = 5
    elif choice == "9":
        num_collections = int((6 * 60) / 5)
        interval_minutes = 5
    elif choice == "10":
        num_collections = int((3 * 60) / 5)
        interval_minutes = 5
    else:
        print("Invalid choice, using quick test settings")
        num_collections = 5
        interval_minutes = 5
    
    total_new_points = num_collections * len(route_points)
    total_time_hours = (num_collections * interval_minutes) / 60
    
    print(f"\n📋 Collection Plan:")
    print(f"   • Collection rounds: {num_collections}")
    print(f"   • Interval: {interval_minutes} minutes")
    print(f"   • Route points per round: {len(route_points)}")
    print(f"   • New data points: {total_new_points}")
    print(f"   • Existing records: {initial_count}")
    print(f"   • Total after completion: {initial_count + total_new_points}")
    print(f"   • Estimated duration: {total_time_hours:.1f} hours")
    print(f"   • Persistent file: {filename}")
    if wait_for_time:
        print(f"   • Scheduled for NY time 3pm-11pm (BDT 1am-9am)")
    
    confirm = input(f"\nReady to collect {total_new_points} new data points? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Collection cancelled.")
        return
    
    if wait_for_time:
        wait_until_ny_time(start_hour, 0)
    
    print(f"\n🚀 Starting data collection...")
    print(f"💾 Using file: {filename}")
    
    failed_collections = 0
    
    try:
        for collection_round in range(num_collections):
            round_start_time = datetime.now()
            print(f"\n🔄 Collection Round {collection_round + 1}/{num_collections}")
            print(f"⏰ Time: {round_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if choice == "7" and NY_TZ:
                current_ny_time = datetime.now(NY_TZ)
                if current_ny_time.hour >= end_hour:
                    print(f"🛑 Collection stopped: Current NY time ({current_ny_time.strftime('%H:%M:%S')}) is past 11pm")
                    break
            
            round_data = []
            round_success = 0
            
            for i, (lat, lon, location_name, road_type) in enumerate(route_points):
                progress = ((collection_round * len(route_points) + i + 1) / total_new_points) * 100
                print(f"  📍 [{i+1}/{len(route_points)}] {location_name} ({progress:.1f}%)")
                
                traffic_data = get_traffic_data(lat, lon, location_name, road_type)
                
                if traffic_data:
                    collected_data.append(traffic_data)
                    round_data.append(traffic_data)
                    round_success += 1
                    
                    speed = traffic_data['current_speed_kmh']
                    congestion = traffic_data['congestion_level']
                    weather = traffic_data['weather_condition']
                    temp = traffic_data['temperature_celsius']
                    incidents = traffic_data['major_accidents_count']
                    
                    status_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "⚫"}
                    emoji = status_emoji.get(congestion, "❓")
                    
                    weather_emoji = "☀️"
                    if traffic_data['is_raining']:
                        weather_emoji = "🌧️"
                    elif traffic_data['is_snowing']:
                        weather_emoji = "❄️"
                    elif traffic_data['has_wildfire_smoke']:
                        weather_emoji = "🔥"
                    elif weather.lower() == "clouds":
                        weather_emoji = "☁️"
                    
                    incident_emoji = "✅" if incidents == 0 else "🚨"
                    
                    print(f"     {emoji} Speed: {speed:.1f} km/h | L{congestion} | {weather_emoji} {weather} | Temp: {temp:.1f}°C | {incident_emoji} {incidents} incidents")
                    
                    conditions = []
                    if traffic_data['major_accidents_count'] > 0:
                        conditions.append(f"🚨 Accident ({traffic_data['accident_severity']} on {traffic_data['accident_roads']})")
                    if traffic_data['is_major_event']:
                        conditions.append("🎉 Event")
                    if conditions:
                        print(f"     ⚠️  {' | '.join(conditions)}")
                else:
                    failed_collections += 1
                    print(f"     ❌ Failed to collect data")
                
                time.sleep(0.7)
            
            if collected_data:
                save_success = save_data_to_csv(collected_data, filename, headers)
                if not save_success:
                    print("⚠️ Save failed, trying timestamped filename...")
                    timestamp_filename = get_persistent_filename(use_timestamp=True)
                    save_success = save_data_to_csv(collected_data, timestamp_filename, headers)
                    if save_success:
                        print(f"   💾 Data saved to fallback: {timestamp_filename}")
                    else:
                        print(f"   ⚠️ Fallback save failed")
                else:
                    print(f"   💾 Data saved successfully to {filename}")
            
            success_rate = (round_success / len(route_points)) * 100
            print(f"   ✅ Round {collection_round + 1} complete: {round_success}/{len(route_points)} successful ({success_rate:.1f}%)")
            print(f"   💾 Total records in dataset: {len(collected_data)}")
            
            if round_data:
                avg_speed = sum(d['current_speed_kmh'] for d in round_data) / len(round_data)
                avg_congestion = sum(d['congestion_level'] for d in round_data) / len(round_data)
                avg_temp = sum(d['temperature_celsius'] for d in round_data) / len(round_data)
                rain_count = sum(1 for d in round_data if d['is_raining'])
                snow_count = sum(1 for d in round_data if d['is_snowing'])
                smoke_count = sum(1 for d in round_data if d['has_wildfire_smoke'])
                total_incidents = sum(d['major_accidents_count'] for d in round_data)
                
                print(f"   📊 Route Summary:")
                print(f"     • Traffic: Avg Speed {avg_speed:.1f} km/h, Avg Congestion L{avg_congestion:.1f}")
                print(f"     • Weather: Avg Temp {avg_temp:.1f}°C, {rain_count} rain, {snow_count} snow, {smoke_count} smoke")
                print(f"     • Incidents: {total_incidents} total accidents")
            
            if collection_round < num_collections - 1:
                print(f"   ⏳ Waiting {interval_minutes} minutes for next collection...")
                time.sleep(interval_minutes * 60)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Data collection interrupted by user")
        print("💾 Saving collected data before exit...")
        if collected_data:
            save_data_to_csv(collected_data, filename, headers)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💾 Attempting to save collected data...")
        if collected_data:
            save_data_to_csv(collected_data, filename, headers)
    
    if collected_data:
        save_success = save_data_to_csv(collected_data, filename, headers)
        if not save_success:
            print("⚠️ Final save failed - attempting backup...")
            backup_filename = f"backup_{filename}"
            save_success = save_data_to_csv(collected_data, backup_filename, headers)
            if save_success:
                print(f"   💾 Backup saved to: {backup_filename}")
    
    print(f"\n" + "="*70)
    print(f"✅ DATA COLLECTION COMPLETE!")
    print(f"="*70)
    print(f"📁 Dataset file: {filename}")
    print(f"📊 Total records in dataset: {len(collected_data)}")
    print(f"🆕 New records added this session: {len(collected_data) - initial_count}")
    print(f"❌ Failed collections: {failed_collections}")
    
    if len(collected_data) > 0:
        success_rate = ((len(collected_data) - initial_count) / (len(collected_data) - initial_count + failed_collections)) * 100 if (len(collected_data) - initial_count + failed_collections) > 0 else 0
        print(f"📈 Session success rate: {success_rate:.1f}%")
    
    if collected_data:
        print(f"\n📈 DATASET ANALYSIS:")
        numeric_data = []
        for d in collected_data:
            try:
                numeric_record = {}
                for key, value in d.items():
                    if key in ['current_speed_kmh', 'free_flow_speed_kmh', 'congestion_level', 
                              'is_raining', 'is_snowing', 'has_wildfire_smoke', 'temperature_celsius',
                              'precipitation_mm', 'wind_speed_kmh', 'visibility_km', 'humidity_percent',
                              'air_quality_index', 'major_accidents_count']:
                        try:
                            numeric_record[key] = float(value) if value != '' else 0.0
                        except (ValueError, TypeError):
                            numeric_record[key] = 0.0
                    else:
                        numeric_record[key] = value
                numeric_data.append(numeric_record)
            except:
                continue
        
        if numeric_data:
            speeds = [d['current_speed_kmh'] for d in numeric_data if d['current_speed_kmh'] > 0]
            congestion_levels = [d['congestion_level'] for d in numeric_data]
            temperatures = [d['temperature_celsius'] for d in numeric_data]
            
            print(f"   🚗 Traffic Statistics:")
            if speeds:
                print(f"     • Speed Range: {min(speeds):.1f} - {max(speeds):.1f} km/h")
                print(f"     • Average Speed: {sum(speeds)/len(speeds):.1f} km/h")
            
            print(f"   🌡️ Temperature Statistics:")
            if temperatures:
                print(f"     • Temperature Range: {min(temperatures):.1f} - {max(temperatures):.1f}°C")
                print(f"     • Average Temperature: {sum(temperatures)/len(temperatures):.1f}°C")
            
            print(f"   🚦 Congestion Distribution:")
            congestion_dist = {}
            for level in congestion_levels:
                congestion_dist[level] = congestion_dist.get(level, 0) + 1
            status_names = {1: "Clear", 2: "Light", 3: "Medium", 4: "Heavy", 5: "Severe"}
            for level in sorted(congestion_dist.keys()):
                print(f"     • Level {int(level)} ({status_names.get(int(level), 'Unknown')}): {congestion_dist[level]} records")
            
            print(f"   🌤️ Weather Conditions:")
            rain_records = sum(1 for d in numeric_data if d['is_raining'] > 0)
            snow_records = sum(1 for d in numeric_data if d['is_snowing'] > 0)
            smoke_records = sum(1 for d in numeric_data if d['has_wildfire_smoke'] > 0)
            print(f"     • Rain conditions: {rain_records} records ({(rain_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Snow conditions: {snow_records} records ({(snow_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Wildfire smoke: {smoke_records} records ({(smoke_records/len(numeric_data)*100):.1f}%)")
            
            print(f"   🚨 Traffic Incidents:")
            incident_records = sum(1 for d in numeric_data if d['major_accidents_count'] > 0)
            total_incidents = sum(d['major_accidents_count'] for d in numeric_data)
            print(f"     • Records with incidents: {incident_records} ({(incident_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Total major accidents: {int(total_incidents)}")
            
            print(f"\n🎯 FINAL DATASET READY")
            print(f"   📊 Features: {len(headers)} columns")
            print(f"   📋 Records: {len(collected_data)} rows")
            
            # if len(collected_data) > 0:
            #     print(f"\n📋 Sample Enhanced Record:")
            #     sample = collected_data[-1]
            #     key_features = [
            #         'timestamp', 'location_name', 'current_speed_kmh', 'congestion_level',
            #         'weather_condition', 'temperature_celsius', 'is_raining', 'is_snowing',
            #         'has_wildfire_smoke', 'major_accidents_count', 'accident_severity', 'accident_roads', 'time_period'
            #     ]
            #     for key in key_features:
            #         if key in sample:
            #             print(f"   {key}: {sample[key]}")
    
    print(f"\n \033[92m💡 Data persists in: {filename}\033[0m")

if __name__ == "__main__":
    collect_comprehensive_dataset()