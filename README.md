# 🚑 Traffic Dataset Collector: Smart Routes for Ambulances 🚨

Welcome to the **Traffic Dataset Collector**, a Python tool that gathers real-time traffic data to help ambulances speed from Bryant Park to Lenox Hill Hospital in Manhattan via 3rd Avenue. This dataset fuels an **LSTM (Long Short-Term Memory)** model to predict the fastest, safest routes, saving critical time for patients. Ready to explore? Let's dive in! 🎉

---

## 📑 Table of Contents

- [**What's This Project?**](#-whats-this-project)
- [**Why It's Cool**](#-why-its-cool)
- [**Setup & Installation**](#️-setup--installation)
- [**Dataset Features**](#-dataset-features)
- [**How LSTM Uses This**](#-how-lstm-uses-this)
- [**Benefits of the Code**](#-benefits-of-the-code)
- [**Get Started**](#-get-started)
- [**License**](#-license)
- [**Contributing**](#-contributing)

---

## 🌟 What's This Project?

**This script collects traffic, weather, and incident data along a 2.4-mile ambulance route in NYC. It's like a super-smart GPS that helps ambulances dodge traffic jams, accidents, and bad weather. The data is saved in a CSV file, ready to train an LSTM model to predict the best route. With backup API keys, it keeps collecting data even if the main keys hit their limit, ensuring no interruptions!**

---

## 🔥 Why It's Cool

| 💚 **Life-Saving** | 🧠 **Smart AI** | 📊 **Rich Data** | 🔄 **Reliable** |
|:---:|:---:|:---:|:---:|
| Gets ambulances to patients faster | Uses LSTM to learn traffic patterns over time | 34 features cover everything from speed to snow | Backup keys keep the data flowing |

---

## 🛠️ Setup & Installation

**Get up and running in minutes:**

### 1. 🐍 **Install Python**
Grab Python 3.8+ from [python.org](https://python.org)

### 2. 📦 **Install Libraries**
Open a terminal and run:
```bash
pip install requests python-dotenv
```

### 3. 🔑 **Get API Keys**
- Sign up for a **TomTom API key** (for traffic data)
- **Optional:** Get an **OpenWeatherMap API key** (for weather)
- Create a `.env` file in your project root directory

### 4. 🔐 **Setup Environment Variables**
Create a `.env` file in your project directory and add your API keys:
```env
TOMTOM_API_KEY=your_tomtom_api_key_here
API_KEY2=your_second_tomtom_key_here
BACKUP_API_KEY=your_backup_tomtom_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
```

> **🔒 Security Note:** Never commit your `.env` file to version control! Add `.env` to your `.gitignore` file.

### 5. 📥 **Clone the Repo**
```bash
git clone https://github.com/Ayman-ilias/data_set_collection_for_emergency_route_using_TomTom_and_OpenWeatherApi.git
cd data_set_collection_for_emergency_route_using_TomTom_and_OpenWeatherApi
```

### 6. ▶️ **Run the Script**
python traffic.py



### 7. ⚙️ **Pick a Mode**
Choose from 10 options (e.g., 3pm-11pm NY time) and start collecting! ⚡

> **💡 Tip:** Keep your internet on, and you're ready to roll! 🚀

---

## 📊 Dataset Features

**The script saves data to `bryant_park_len_sum_traffic_data.csv` with 34 features. Each helps the LSTM model predict the best route by analyzing traffic patterns. Here's the scoop, grouped for clarity:**

### 📍 **Where & When**

#### 🕒 **timestamp**
- **When the data was grabbed** (e.g., 2025-06-12 14:25:00)
- **Why?** Tracks traffic changes over time
- **Helps LSTM:** Learn patterns like rush hour vs. late-night flow

#### 📌 **location_name**
- **Route point name** (e.g., 3rd_Ave_42nd)
- **Why?** Identifies specific spots
- **Helps LSTM:** Pinpoint where congestion hits

#### 🗺️ **latitude, longitude**
- **Exact coordinates**
- **Why?** Maps the route
- **Helps LSTM:** Analyze traffic by location

### 🚦 **Traffic Flow**

#### ⚡ **current_speed**
- **Speed of traffic** (km/h)
- **Why?** Shows how fast cars are moving
- **Helps LSTM:** Spot slow routes to avoid

#### 🏁 **free_flow_speed**
- **Normal speed without traffic**
- **Why?** Baseline for clear roads
- **Helps LSTM:** Measure congestion severity

#### ⏱️ **travel_time**
- **Time to cross a segment** (seconds)
- **Why?** Direct delay measure
- **Helps LSTM:** Predict total route time

#### ⏰ **normal_time_seconds**
- **Ideal time without traffic**
- **Why?** Shows best-case travel time
- **Helps LSTM:** Highlight delays

#### 🚥 **congestion_level**
- **Traffic scale** (1 = Clear, 8 = Severe)
- **Why?** Rates congestion
- **Helps LSTM:** Avoid heavy traffic routes

#### 📊 **congestion_ratio**
- **Current speed ÷ free-flow speed**
- **Why?** Precise congestion metric
- **Helps LSTM:** Fine-tune predictions

#### ✅ **confidence**
- **Data reliability** (0 to 100)
- **Why?** Ensures good data
- **Helps LSTM:** Trust accurate inputs

### 🛣️ **Road Info**

#### 🛤️ **road_type**
- **Road type** (e.g., Avenue, Street)
- **Why?** Different roads, different traffic
- **Helps LSTM:** Pick faster road types

#### 📏 **estimated_distance_km**
- **Segment length**
- **Why?** Helps calculate route time
- **Helps LSTM:** Optimize for shorter paths

#### 🎯 **route_segment**
- **Route role** (e.g., Origin, Destination)
- **Why?** Shows segment importance
- **Helps LSTM:** Focus on key areas like the hospital

### ⏰ **Time Features**

#### 🕐 **hour, day_of_week, day_name, month**
- **Time and date details**
- **Why?** Traffic varies by time
- **Helps LSTM:** Spot patterns like Monday rush hours

#### 🎉 **is_weekend**
- **1 for weekends, 0 for weekdays**
- **Why?** Weekends are quieter
- **Helps LSTM:** Adjust for lighter traffic

#### 🎊 **is_holiday, holiday_name**
- **Flags holidays** (e.g., Thanksgiving)
- **Why?** Holidays disrupt traffic
- **Helps LSTM:** Avoid holiday jams

#### 🌅 **is_morning_rush, is_evening_rush, is_rush_hour**
- **Peak hour flags**
- **Why?** Rush hours are busy
- **Helps LSTM:** Steer clear of peak times

#### 🕰️ **time_period**
- **Time of day** (e.g., Morning Rush)
- **Why?** Groups hours for analysis
- **Helps LSTM:** Predict busy vs. quiet times

#### 🍂 **season**
- **Season** (e.g., Winter)
- **Why?** Seasons affect traffic
- **Helps LSTM:** Handle seasonal changes like snow

### 🌧️ **Weather Conditions**

#### 🌤️ **weather_condition**
- **Weather type** (e.g., Clear, Rain)
- **Why?** Weather slows traffic
- **Helps LSTM:** Avoid rainy or snowy routes

#### 🌧️ **has_rain, has_snow, has_wildfire_smoke**
- **1 if true, 0 if not**
- **Why?** Specific weather causes delays
- **Helps LSTM:** Pick safer routes

#### 💧 **rain_intensity, snow_intensity**
- **Precipitation strength** (mm/h)
- **Why?** Heavier rain/snow = worse traffic
- **Helps LSTM:** Gauge weather impact

#### 👁️ **visibility_km**
- **How far you can see** (km)
- **Why?** Low visibility is risky
- **Helps LSTM:** Choose clearer routes

#### 🌬️ **air_quality_index**
- **Air quality** (0-100)
- **Why?** Smoke affects driving
- **Helps LSTM:** Ensure safer air quality

### 🚨 **Incidents**

#### 🚗 **major_accidents_count**
- **Number of nearby accidents**
- **Why?** Accidents block roads
- **Helps LSTM:** Avoid incident zones

#### ⚠️ **accident_severity**
- **Accident impact** (None, Minor, Major)
- **Why?** Severe accidents cause bigger delays
- **Helps LSTM:** Skip high-impact areas

#### 🛣️ **accident_roads**
- **Roads with accidents** (e.g., 3rd Ave)
- **Why?** Pinpoints trouble spots
- **Helps LSTM:** Reroute around them

#### 🚨 **has_major_incident**
- **1 if major incidents, 0 if not**
- **Why?** Flags big disruptions
- **Helps LSTM:** Quickly avoid risky routes

---

## 🧠 How LSTM Uses This

**LSTM is like a traffic fortune-teller! It learns from this data to predict future conditions:**

| ⏰ **Time Trends** | 🚦 **Traffic Flow** | 🌧️ **Weather & Incidents** | 🎯 **Route Optimization** |
|:---:|:---:|:---:|:---:|
| Uses timestamp, hour, etc., to spot patterns like rush hour | Predicts congestion_level and travel_time for each segment | Avoids routes with rain, snow, or accidents | Picks the fastest, safest path by analyzing all features |

---

## 🎯 Benefits of the Code

| 💚 **Saves Lives** | 🔄 **No Downtime** | ⚙️ **Flexible** | 📊 **Data-Rich** | 👥 **User-Friendly** |
|:---:|:---:|:---:|:---:|:---:|
| Helps ambulances reach patients faster | Backup API key ensures continuous data collection | 10 modes, from quick tests to 4-day runs | 34 features give LSTM everything it needs | Easy setup, clear outputs, perfect for beginners |

---

## 🚀 Get Started

1. **📥 Clone the repo and follow the setup steps**
2. **🔐 Create your `.env` file with API keys**
3. **▶️ Run `python traffic_data_collector_with_backup.py`**
4. **⚙️ Choose a collection mode** (e.g., Option 7 for 3pm-11pm NY time, 1am-9am BDT)
5. **💾 Data saves to `bryant_park_len_sum_traffic_data.csv`**
6. **🧠 Train your LSTM model with the CSV to predict optimal routes!**

> **❄️ Fun Fact:** This script works even in snowstorms or rush hour, capturing every detail to keep ambulances moving! 🚦

---

## 📜 License

**This project is licensed under the MIT License. Feel free to use, modify, and share!** 📝

---

## 🤝 Contributing

**Love this project? Want to make it better? Fork the repo, make changes, and submit a pull request! Check out CONTRIBUTING.md for details. Let's save lives together!** 💪

> **⭐ Star this repo if you think it's awesome! Got questions? Open an issue or ping me. Let's make ambulances unstoppable!** 🚑

---

<div align="center">
  <h3>Thank You</h3>
</div>