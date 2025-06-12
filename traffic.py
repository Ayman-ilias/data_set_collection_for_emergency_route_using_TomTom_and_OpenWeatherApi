import requests
import csv
import time
import json
import math
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("TOMTOM_API_KEY")
API_KEY2 = os.getenv("API_KEY2")
BACKUP_API_KEY = os.getenv("BACKUP_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

NY_TZ = ZoneInfo("America/New_York")

# Manual holiday definitions for New York (2024-2025)
NY_HOLIDAYS = {
    # 2024
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
    
    # 2025
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

# Define our route roads for incident filtering
RELEVANT_ROADS = [
    "3rd Avenue", "3rd Ave", "Third Avenue",
    "W 42nd St", "West 42nd Street", "42nd Street",
    "E 77th St", "East 77th Street", "77th Street",
    "5th Avenue", "5th Ave", "Fifth Avenue",
    "Park Avenue", "Park Ave",
    "Lexington Avenue", "Lexington Ave", "Lex Ave"
]

def is_holiday(date_obj):
    """Check if given date is a holiday"""
    date_str = date_obj.strftime('%Y-%m-%d')
    return date_str in NY_HOLIDAYS

def get_holiday_name(date_obj):
    """Get holiday name if it's a holiday"""
    date_str = date_obj.strftime('%Y-%m-%d')
    return NY_HOLIDAYS.get(date_str, "None")

def get_road_type(street_name):
    """Determine road type based on street name"""
    street_lower = street_name.lower()
    
    if 'ave' in street_lower or 'avenue' in street_lower:
        return 'Avenue'
    elif 'st' in street_lower or 'street' in street_lower:
        return 'Street'
    elif 'blvd' in street_lower or 'boulevard' in street_lower:
        return 'Boulevard'
    elif 'pkwy' in street_lower or 'parkway' in street_lower:
        return 'Parkway'
    elif 'hwy' in street_lower or 'highway' in street_lower:
        return 'Highway'
    elif 'hospital' in street_lower or 'park' in street_lower:
        return 'Special Area'
    else:
        return 'Street'  # Default

def calculate_distance(lat1, lon1, lat2, lon2):
    #Haversine formula use kore distance calculate korbo
    R = 6371  # km e
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
    if not WEATHER_API_KEY or WEATHER_API_KEY == os.getenv("OPENWEATHER_API_KEY"):
        return {
            'weather_condition': 'Clear',
            'has_rain': 0,
            'has_snow': 0,
            'has_wildfire_smoke': 0,
            'rain_intensity': 0.0,
            'snow_intensity': 0.0,
            'visibility_km': 10.0,
            'air_quality_index': 50
        }
    
    try:
        # Current weather
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        
        # Air quality for wildfire smoke detection
        air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        air_params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY
        }
        
        air_response = requests.get(air_url, params=air_params, timeout=10)
        
        # Initialize default values
        weather_condition = 'Clear'
        has_rain = 0
        has_snow = 0
        has_wildfire_smoke = 0
        rain_intensity = 0.0
        snow_intensity = 0.0
        visibility_km = 10.0
        air_quality_index = 50
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            
            # Main weather condition
            if 'weather' in weather_data and len(weather_data['weather']) > 0:
                main_weather = weather_data['weather'][0]['main']
                description = weather_data['weather'][0]['description']
                weather_condition = description.title()
                
                # Check for rain
                if main_weather.lower() in ['rain', 'drizzle'] or 'rain' in description.lower():
                    has_rain = 1
                    if 'rain' in weather_data and '1h' in weather_data['rain']:
                        rain_intensity = weather_data['rain']['1h']
                    elif 'rain' in weather_data and '3h' in weather_data['rain']:
                        rain_intensity = weather_data['rain']['3h'] / 3  # Convert to hourly
                
                # Check for snow
                if main_weather.lower() == 'snow' or 'snow' in description.lower():
                    has_snow = 1
                    if 'snow' in weather_data and '1h' in weather_data['snow']:
                        snow_intensity = weather_data['snow']['1h']
                    elif 'snow' in weather_data and '3h' in weather_data['snow']:
                        snow_intensity = weather_data['snow']['3h'] / 3  # Convert to hourly
            
            # Visibility
            if 'visibility' in weather_data:
                visibility_km = weather_data['visibility'] / 1000  # Convert meters to km
        
        # Air quality for wildfire smoke detection
        if air_response.status_code == 200:
            air_data = air_response.json()
            if 'list' in air_data and len(air_data['list']) > 0:
                aqi_data = air_data['list'][0]
                if 'main' in aqi_data:
                    air_quality_index = aqi_data['main']['aqi'] * 20  # Convert 1-5 scale to 0-100
                
                # Detect wildfire smoke (high PM2.5 and PM10 with low visibility)
                if 'components' in aqi_data:
                    pm25 = aqi_data['components'].get('pm2_5', 0)
                    pm10 = aqi_data['components'].get('pm10', 0)
                    
                    # Wildfire smoke indicators: high particulate matter + reduced visibility
                    if (pm25 > 35 or pm10 > 50) and visibility_km < 8:
                        has_wildfire_smoke = 1
                        weather_condition = f"{weather_condition} with Smoke"
        
        return {
            'weather_condition': weather_condition,
            'has_rain': has_rain,
            'has_snow': has_snow,
            'has_wildfire_smoke': has_wildfire_smoke,
            'rain_intensity': round(rain_intensity, 2),
            'snow_intensity': round(snow_intensity, 2),
            'visibility_km': round(visibility_km, 1),
            'air_quality_index': air_quality_index
        }
        
    except Exception as e:
        print(f"Weather API error: {e}")
        # Return safe defaults
        return {
            'weather_condition': 'Unknown',
            'has_rain': 0,
            'has_snow': 0,
            'has_wildfire_smoke': 0,
            'rain_intensity': 0.0,
            'snow_intensity': 0.0,
            'visibility_km': 10.0,
            'air_quality_index': 50
        }

def get_traffic_incidents(lat, lon):
    try:
        incidents_url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
        
        # Define a bounding box around our route (Manhattan area)
        # Bryant Park to Lenox Hill Hospital area
        min_lat, max_lat = 40.750, 40.780  # Latitude range
        min_lon, max_lon = -73.990, -73.955  # Longitude range
        
        bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
        
        params = {
            'key': API_KEY2,
            'bbox': bbox,
            'categoryFilter': '0,1,2,3',  # 0=Unknown, 1=Accident, 2=Fog, 3=Dangerous Conditions
            'timeValidityFilter': 'present',
            'language': 'en'
        }
        
        response = requests.get(incidents_url, params=params, timeout=15)
        
        # Check for 403 error and try backup key
        if response.status_code == 403:
            print(f"Primary API key (API_KEY2) failed with 403, trying backup key...")
            params['key'] = BACKUP_API_KEY
            response = requests.get(incidents_url, params=params, timeout=15)
        
        major_accidents_count = 0
        accident_roads = []
        accident_severity = "None"
        
        if response.status_code == 200:
            incidents_data = response.json()
            
            if 'incidents' in incidents_data:
                for incident in incidents_data['incidents']:
                    # Only process accidents (category 1) and dangerous conditions (category 3)
                    if incident.get('categoryName', '').lower() in ['accident', 'dangerous conditions']:
                        
                        # Check if incident is on our relevant roads
                        incident_desc = incident.get('description', '').lower()
                        incident_road = incident.get('roadName', '').lower()
                        
                        is_relevant = False
                        for road in RELEVANT_ROADS:
                            if road.lower() in incident_desc or road.lower() in incident_road:
                                is_relevant = True
                                break
                        
                        if is_relevant:
                            major_accidents_count += 1
                            
                            # Extract road name
                            road_name = incident.get('roadName', 'Unknown Road')
                            if road_name not in accident_roads:
                                accident_roads.append(road_name)
                            
                            # Determine severity based on description
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
            'accident_roads': ', '.join(accident_roads[:3]) if accident_roads else "None",  # Max 3 roads
            'has_major_incident': 1 if major_accidents_count > 0 else 0
        }
        
    except Exception as e:
        print(f"Traffic incidents API error: {e}")
        return {
            'major_accidents_count': 0,
            'accident_severity': "Unknown",
            'accident_roads': "Unknown",
            'has_major_incident': 0
        }

def get_persistent_filename():
    return "bryant_park_lenox_hill_traffic_dataset_persistent.csv"

def load_existing_data(filename):
    """Load existing data from CSV if file exists"""
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
    else:
        print(f"📝 Creating new dataset file: {filename}")
        return []

def save_data_to_csv(data, filename, headers):
    #Save data to CSV file
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_traffic_data(lat, lon, location_name, road_type="Street"):
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    
    params = {
        'key': API_KEY,
        'point': f'{lat},{lon}',
        'unit': 'KMPH'
    }
    
    try:
        response = requests.get(url, params=params)
        
        # Check for 403 error and try backup key
        if response.status_code == 403:
            print(f"Primary API key (API_KEY) failed with 403, trying backup key...")
            params['key'] = BACKUP_API_KEY
            response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            flow_data = data.get('flowSegmentData', {})
            
            # Core traffic data
            current_speed = flow_data.get('currentSpeed', 0)
            free_flow_speed = flow_data.get('freeFlowSpeed', 0)
            travel_time = flow_data.get('currentTravelTime', 0)
            confidence = flow_data.get('confidence', 0)
            
            # Congestion calculate korbo
            if free_flow_speed > 0:
                congestion_ratio = current_speed / free_flow_speed
                if congestion_ratio >= 0.8:
                    congestion_level = 1  # Clear
                elif congestion_ratio >= 0.6:
                    congestion_level = 2  # Light 
                elif congestion_ratio >= 0.4:
                    congestion_level = 3  # Medium
                elif congestion_ratio >= 0.2:
                    congestion_level = 4  # Heavy
                else:
                    congestion_level = 5  # Severe
            else:
                congestion_level = 3
                congestion_ratio = 0.5  # Default assumption
            
            # Time-based features
            now = datetime.now(ZoneInfo("America/New_York"))
            bd = datetime.now()
            current_date = now.date()
            
            # Holiday check using manually 
            is_holiday_today = 1 if is_holiday(current_date) else 0
            holiday_name = get_holiday_name(current_date)
            
            # Calculate normal travel time (based on free flow speed)
            estimated_distance = 0.15  # km (average block distance in NYC)
            normal_time = (estimated_distance / free_flow_speed * 3600) if free_flow_speed > 0 else travel_time
            
            # Distance calculation (estimate for route segment)
            if 'ave' in location_name.lower():
                estimated_distance = 0.2  # Avenues are longer
            elif 'hospital' in location_name.lower() or 'park' in location_name.lower():
                estimated_distance = 0.1  # Special areas
            else:
                estimated_distance = 0.15  # Regular streets
            
            # Get weather data 
            weather_data = get_weather_data(lat, lon)
            
            # Get traffic incidents
            incident_data = get_traffic_incidents(lat, lon)
            
            # Combine all data
            traffic_record = {
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
                'day_of_week': now.weekday(),  # 0=Monday, 6=Sunday
                'day_name': now.strftime('%A'),
                'month': now.month,
                'is_weekend': 1 if now.weekday() >= 5 else 0,
                'is_holiday': is_holiday_today,
                'holiday_name': holiday_name,
                
                # Rush hour indicators
                'is_morning_rush': 1 if 7 <= now.hour <= 9 else 0,
                'is_evening_rush': 1 if 17 <= now.hour <= 19 else 0,
                'is_rush_hour': 1 if (7 <= now.hour <= 9) or (17 <= now.hour <= 19) else 0,
                
                # Additional time periods
                'time_period': get_time_period(now.hour),
                'season': get_season(now.month),
                
                # Route position indicator
                'route_segment': get_route_segment(location_name)
            }
            
            # weather features 
            traffic_record.update(weather_data)
            
            #incident features
            traffic_record.update(incident_data)
            
            return traffic_record
            
        else:
            print(f"API Error for {location_name}: {response.status_code}")
            if response.status_code == 403:
                print("Both primary and backup API keys failed or quota exceeded")
            return None
            
    except Exception as e:
        print(f"Error getting data for {location_name}: {e}")
        return None

def get_time_period(hour):
    #Categorize time into periods
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
    #Get season based on month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

def get_route_segment(location_name):
    #Identify which part of route this point represents
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

def wait_until_ny_time(hour, minute, timezone="America/New_York"):
    """Wait until the specified time in New York timezone"""
    ny_tz = ZoneInfo(timezone)
    now = datetime.now(ny_tz)
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If target time is in the past, wait until the next day
    if target_time <= now:
        target_time += timedelta(days=1)
    
    wait_seconds = (target_time - now).total_seconds()
    print(f"⏳ Waiting until {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ({wait_seconds/3600:.1f} hours)...")
    time.sleep(wait_seconds)

def collect_comprehensive_dataset():
    
    print("🚑 ENHANCED TRAFFIC DATASET COLLECTOR v2.0")
    print("=" * 70)
    print("Route: Bryant Park → Lenox Hill Hospital via 3rd Avenue")
    print("Distance: 2.4 miles (3.86 km) | Expected: ~25 minutes")
    print("=" * 70)
    
    # Define route points 
    route_points = [
        # Starting point - Bryant Park
        (40.7536, -73.9832, "Bryant_Park_Start", "Special Area"),
        
        # Head southeast on W 42nd St toward 5th Ave
        (40.7535, -73.9815, "W_42nd_St_toward_5th_Ave", "Street"),
        (40.7533, -73.9795, "W_42nd_St_5th_Ave_Junction", "Street"),
        
        # Turn left onto 3rd Ave - key points along 3rd Avenue
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
        
        # Turn left onto E 77th St
        (40.7745, -73.9627, "3rd_Ave_77th_St_Junction", "Avenue"),
        (40.7746, -73.9615, "E_77th_St_from_3rd_Ave", "Street"),
        (40.7747, -73.9610, "E_77th_St_mid_block", "Street"),
        
        # Arrive at Lenox Hill Hospital, 100 E 77th St
        (40.7748, -73.9603, "Lenox_Hill_Hospital_Destination", "Special Area")
    ]
    
    print(f"📍 Route analysis points: {len(route_points)} strategic locations")
    print("   Including: Start, Street turns, Avenue segments, Destination")
    
    # CSV headers 
    headers = [
        # Core identifiers
        'timestamp', 'location_name', 'latitude', 'longitude',
        
        # Main traffic features
        'current_speed_kmh', 'free_flow_speed_kmh', 'travel_time_seconds',
        'normal_time_seconds', 'congestion_level', 'congestion_ratio', 'confidence',
        
        # Road and distance features
        'road_type', 'estimated_distance_km', 'route_segment',
        
        # Time-based features
        'hour', 'day_of_week', 'day_name', 'month', 'is_weekend',
        'is_holiday', 'holiday_name', 'is_morning_rush', 'is_evening_rush',
        'is_rush_hour', 'time_period', 'season',
        
        # WEATHER FEATURES
        'weather_condition', 'has_rain', 'has_snow', 'has_wildfire_smoke',
        'rain_intensity', 'snow_intensity', 'visibility_km', 'air_quality_index',
        
        # INCIDENT FEATURES  
        'major_accidents_count', 'accident_severity', 'accident_roads', 'has_major_incident'
    ]
    
    # Use persistent filename
    filename = get_persistent_filename()
    
    # Load existing data
    collected_data = load_existing_data(filename)
    initial_count = len(collected_data)
    
    # Data collection options
    print(f"\n📊 Dataset Collection Options:")
    print("1. Quick test (5 rounds, 5-min intervals) - ~25 minutes")
    print("2. Short term (12 rounds, 10-min intervals) - 2 hours") 
    print("3. Half day (24 rounds, 30-min intervals) - 12 hours")
    print("4. Full day (48 rounds, 30-min intervals) - 24 hours")
    print("5. Multi-day (96 rounds, 60-min intervals) - 4 days")
    print("6. Custom configuration")
    print("7. Night collection (NY 3pm-11pm, 5-min intervals) - 8 hours")
    print("8. 8-hour collection (5-min intervals) - 8 hours")
    print("9. 6-hour collection (5-min intervals) - 6 hours")
    print("10. 3-hour collection (5-min intervals) - 3 hours")
    
    choice = input("Enter your choice (1-10): ").strip()
    
    if choice == "1":
        num_collections = 5
        interval_minutes = 5
        wait_for_time = False
    elif choice == "2":
        num_collections = 12
        interval_minutes = 10
        wait_for_time = False
    elif choice == "3":
        num_collections = 24
        interval_minutes = 30
        wait_for_time = False
    elif choice == "4":
        num_collections = 48
        interval_minutes = 30
        wait_for_time = False
    elif choice == "5":
        num_collections = 96
        interval_minutes = 60
        wait_for_time = False
    elif choice == "6":
        num_collections = int(input("How many collection rounds? "))
        interval_minutes = int(input("Interval in minutes? "))
        wait_for_time = False
    elif choice == "7":
        # 8 hours (3pm-11pm NY time) at 5-minute intervals
        num_collections = int((8 * 60) / 5)  # 8 hours * 60 min / 5 min per round = 96 rounds
        interval_minutes = 5
        wait_for_time = True
        start_hour = 15  # 3pm
        end_hour = 23  # 11pm
    elif choice == "8":
        # 8 hours at 5-minute intervals
        num_collections = int((8 * 60) / 5)  # 8 hours * 60 min / 5 min per round = 96 rounds
        interval_minutes = 5
        wait_for_time = False
    elif choice == "9":
        # 6 hours at 5-minute intervals
        num_collections = int((6 * 60) / 5)  # 6 hours * 60 min / 5 min per round = 72 rounds
        interval_minutes = 5
        wait_for_time = False
    elif choice == "10":
        # 3 hours at 5-minute intervals
        num_collections = int((3 * 60) / 5)  # 3 hours * 60 min / 5 min per round = 36 rounds
        interval_minutes = 5
        wait_for_time = False
    else:
        print("Invalid choice, using quick test settings")
        num_collections = 5
        interval_minutes = 5
        wait_for_time = False
    
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
    
    # Confirm before starting
    confirm = input(f"\nReady to collect {total_new_points} new data points? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Collection cancelled.")
        return
    
    # Wait for 3pm NY time if option 7 is selected
    if wait_for_time:
        wait_until_ny_time(start_hour, 0)  # Wait until 3pm NY time
    
    failed_collections = 0
    
    try:
        print(f"\n🚀 Starting enhanced data collection...")
        print(f"💾 Using persistent file: {filename}")
        
        for collection_round in range(num_collections):
            round_start_time = datetime.now()
            print(f"\n🔄 Collection Round {collection_round + 1}/{num_collections}")
            print(f"⏰ Time: {round_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check if current NY time is past 11pm for option 7
            if choice == "7":
                ny_tz = ZoneInfo("America/New_York")
                current_ny_time = datetime.now(ny_tz)
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
                    
                    # Display key metrics with new features
                    speed = traffic_data['current_speed_kmh']
                    congestion = traffic_data['congestion_level']
                    weather = traffic_data['weather_condition']
                    incidents = traffic_data['major_accidents_count']
                    
                    status_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "⚫"}
                    emoji = status_emoji.get(congestion, "❓")
                    
                    # Weather emoji
                    weather_emoji = "☀️"
                    if traffic_data['has_rain']:
                        weather_emoji = "🌧️"
                    elif traffic_data['has_snow']:
                        weather_emoji = "❄️"
                    elif traffic_data['has_wildfire_smoke']:
                        weather_emoji = "🔥"
                    
                    # Incident emoji
                    incident_emoji = "✅" if incidents == 0 else "🚨"
                    
                    print(f"     {emoji} Speed: {speed:.1f} km/h | L{congestion} | {weather_emoji} {weather} | {incident_emoji} {incidents} incidents")
                else:
                    failed_collections += 1
                    print(f"     ❌ Failed to collect data")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Save data after each round (persistent backup)
            if collected_data:
                save_success = save_data_to_csv(collected_data, filename, headers)
                if save_success:
                    print(f"   💾 Data saved successfully to {filename}")
                else:
                    print(f"   ⚠️ Warning: Failed to save data")
            
            # Round summary 
            success_rate = (round_success / len(route_points)) * 100
            print(f"   ✅ Round {collection_round + 1} complete: {round_success}/{len(route_points)} successful ({success_rate:.1f}%)")
            print(f"   💾 Total records in dataset: {len(collected_data)}")
            
            if round_data:
                # Traffic metrics
                avg_speed = sum(d['current_speed_kmh'] for d in round_data) / len(round_data)
                avg_congestion = sum(d['congestion_level'] for d in round_data) / len(round_data)
                
                # Weather summary
                rain_count = sum(1 for d in round_data if d['has_rain'])
                snow_count = sum(1 for d in round_data if d['has_snow'])
                smoke_count = sum(1 for d in round_data if d['has_wildfire_smoke'])
                
                # Incident summary
                total_incidents = sum(d['major_accidents_count'] for d in round_data)
                
                print(f"   📊 Route Summary:")
                print(f"     • Traffic: Avg Speed {avg_speed:.1f} km/h, Avg Congestion L{avg_congestion:.1f}")
                print(f"     • Weather: {rain_count} rain, {snow_count} snow, {smoke_count} smoke points")
                print(f"     • Incidents: {total_incidents} total accidents on relevant roads")
            
            # Wait for next collection
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
    
    # Final save
    if collected_data:
        save_success = save_data_to_csv(collected_data, filename, headers)
        if not save_success:
            print("⚠️ Final save failed - attempting backup...")
            backup_filename = f"backup_{filename}"
            save_data_to_csv(collected_data, backup_filename, headers)
    
    # Final comprehensive report
    print(f"\n" + "="*70)
    print(f"✅DATA COLLECTION COMPLETE!")
    print(f"="*70)
    print(f"📁 Dataset file: {filename}")
    print(f"📊 Total records in dataset: {len(collected_data)}")
    print(f"🆕 New records added this session: {len(collected_data) - initial_count}")
    print(f"❌ Failed collections: {failed_collections}")
    
    if len(collected_data) > 0:
        success_rate = ((len(collected_data) - initial_count) / (len(collected_data) - initial_count + failed_collections)) * 100 if (len(collected_data) - initial_count + failed_collections) > 0 else 0
        print(f"📈 Session success rate: {success_rate:.1f}%")
    
    # dataset analysis
    if collected_data:
        print(f"\n📈 COMPREHENSIVE DATASET ANALYSIS:")
        
        # Convert string values to numeric for analysis
        numeric_data = []
        for d in collected_data:
            try:
                numeric_record = {}
                for key, value in d.items():
                    if key in ['current_speed_kmh', 'free_flow_speed_kmh', 'congestion_level', 
                              'has_rain', 'has_snow', 'has_wildfire_smoke', 'major_accidents_count']:
                        numeric_record[key] = float(value) if value != '' else 0
                    else:
                        numeric_record[key] = value
                numeric_data.append(numeric_record)
            except:
                continue
        
        if numeric_data:
            speeds = [d['current_speed_kmh'] for d in numeric_data if d['current_speed_kmh'] > 0]
            congestion_levels = [d['congestion_level'] for d in numeric_data]
            
            print(f"   🚗 Traffic Statistics:")
            if speeds:
                print(f"     • Speed Range: {min(speeds):.1f} - {max(speeds):.1f} km/h")
                print(f"     • Average Speed: {sum(speeds)/len(speeds):.1f} km/h")
                
                free_flow_speeds = [d['free_flow_speed_kmh'] for d in numeric_data if d['free_flow_speed_kmh'] > 0]
                if free_flow_speeds:
                    print(f"     • Free Flow Average: {sum(free_flow_speeds)/len(free_flow_speeds):.1f} km/h")
            
            print(f"   🚦 Congestion Distribution:")
            congestion_dist = {}
            for level in congestion_levels:
                congestion_dist[level] = congestion_dist.get(level, 0) + 1
            
            status_names = {1: "Clear", 2: "Light", 3: "Medium", 4: "Heavy", 5: "Severe"}
            for level in sorted(congestion_dist.keys()):
                print(f"     • Level {int(level)} ({status_names.get(int(level), 'Unknown')}): {congestion_dist[level]} records")
            
            # Weather analysis
            print(f"   🌤️ Weather Conditions:")
            rain_records = sum(1 for d in numeric_data if d['has_rain'] > 0)
            snow_records = sum(1 for d in numeric_data if d['has_snow'] > 0)
            smoke_records = sum(1 for d in numeric_data if d['has_wildfire_smoke'] > 0)
            
            print(f"     • Rain conditions: {rain_records} records ({(rain_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Snow conditions: {snow_records} records ({(snow_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Wildfire smoke: {smoke_records} records ({(smoke_records/len(numeric_data)*100):.1f}%)")
            
            # Incident analysis
            print(f"   🚨 Traffic Incidents:")
            incident_records = sum(1 for d in numeric_data if d['major_accidents_count'] > 0)
            total_incidents = sum(d['major_accidents_count'] for d in numeric_data)
            
            print(f"     • Records with incidents: {incident_records} ({(incident_records/len(numeric_data)*100):.1f}%)")
            print(f"     • Total major accidents: {int(total_incidents)}")
            
            # Time distribution
            time_periods = {}
            for d in collected_data:
                period = d.get('time_period', 'Unknown')
                time_periods[period] = time_periods.get(period, 0) + 1
            
            print(f"   ⏰ Time Period Distribution:")
            for period, count in sorted(time_periods.items()):
                print(f"     • {period}: {count} records")
            
            # Special conditions
            holiday_count = sum(1 for d in collected_data if d.get('is_holiday') == '1')
            weekend_count = sum(1 for d in collected_data if d.get('is_weekend') == '1')
            rush_hour_count = sum(1 for d in collected_data if d.get('is_rush_hour') == '1')
            
            print(f"   🎯 Special Conditions:")
            print(f"     • Holiday records: {holiday_count}")
            print(f"     • Weekend records: {weekend_count}")
            print(f"     • Rush hour records: {rush_hour_count}")
            
            print(f"\n🎯 FINAL DATASET READY")
            print(f"   📊 Features: {len(headers)} columns")
            print(f"   📋 Records: {len(collected_data)} rows")
            
            # Sample enhanced record
            if len(collected_data) > 0:
                print(f"\n📋 Sample Enhanced Record:")
                sample = collected_data[-1]  # Latest record
                key_features = [
                    'timestamp', 'location_name', 'current_speed_kmh', 'congestion_level',
                    'weather_condition', 'has_rain', 'has_snow', 'has_wildfire_smoke',
                    'major_accidents_count', 'accident_severity', 'time_period'
                ]
                for key in key_features:
                    if key in sample:
                        print(f"   {key}: {sample[key]}")
    
    # print(f"  \n💡 Data persists in: {filename}")
    print(f"\n \033[92m💡 Data persists in: {filename}\033[0m")


if __name__ == "__main__":
    collect_comprehensive_dataset()