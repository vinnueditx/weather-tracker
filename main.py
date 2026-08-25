```python
import os
import sqlite3
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_NAME = "weather_data.db"


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE,
            country TEXT,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER,
            timestamp TIMESTAMP,
            temperature_c REAL,
            humidity INTEGER,
            pressure_hpa REAL,
            wind_speed_mps REAL,
            weather_condition TEXT,
            FOREIGN KEY (city_id) REFERENCES cities(city_id)
        )
    """)

    conn.commit()
    conn.close()


def fetch_weather_data(city: str):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["description"],
        }
    except requests.exceptions.RequestException as e:
        print(f"API Request Error for {city}: {e}")
        return None
    except KeyError as e:
        print(f"Unexpected response structure for {city}: {e}")
        return None


def save_weather_data(weather: dict):
    if not weather:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Upsert city
    cursor.execute("""
        INSERT OR IGNORE INTO cities (city_name, country, latitude, longitude)
        VALUES (?, ?, ?, ?)
    """, (
        weather["city"],
        weather["country"],
        weather["latitude"],
        weather["longitude"],
    ))

    # Retrieve city_id
    cursor.execute("SELECT city_id FROM cities WHERE city_name = ?", (weather["city"],))
    city_id = cursor.fetchone()[0]

    # Insert weather measurement
    cursor.execute("""
        INSERT INTO weather_data (
            city_id,
            timestamp,
            temperature_c,
            humidity,
            pressure_hpa,
            wind_speed_mps,
            weather_condition
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        city_id,
        weather["timestamp"],
        weather["temperature"],
        weather["humidity"],
        weather["pressure"],
        weather["wind_speed"],
        weather["condition"],
    ))

    conn.commit()
    conn.close()
    print(f"✓ Data saved for {weather['city']}")


def display_weather_data():
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT
            c.city_name,
            c.country,
            w.timestamp,
            w.temperature_c,
            w.humidity,
            w.pressure_hpa,
            w.wind_speed_mps,
            w.weather_condition
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        ORDER BY w.timestamp DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print("\n========== RECENT WEATHER DATA ==========")
    print(df.to_string(index=False))
    return df


if __name__ == "__main__":
    if not API_KEY or API_KEY == "your_openweathermap_api_key_here":
        raise ValueError("Missing OPENWEATHER_API_KEY. Please set it in your .env file.")

    setup_database()

    target_cities = ["Vijayawada", "Hyderabad", "Chennai", "Bangalore"]

    for city in target_cities:
        print(f"Fetching {city}...")
        data = fetch_weather_data(city)
        if data:
            save_weather_data(data)

    display_weather_data()