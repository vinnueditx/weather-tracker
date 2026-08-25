# weather-tracker
An automated Python data pipeline that fetches real-time weather metrics via the OpenWeatherMap API, normalizes and persists records into a relational SQLite database, and queries structured data using Pandas. Features secure environment variable handling with dotenv, robust error handling, and clean relational foreign key constraints


# Weather Data Pipeline

An automated data pipeline in Python that fetches real-time weather metrics using the OpenWeatherMap API, persists normalized relational records into SQLite, and reads structured reports via Pandas.

## Features
- **API Ingestion**: Pulls metrics (temperature, humidity, pressure, wind speed) from OpenWeatherMap.
- **Relational Storage**: Normalizes data into `cities` and `weather_data` tables with foreign keys.
- **Data Display**: Formatted SQL querying using Pandas DataFrames.
- **Security**: Loads credentials securely via `python-dotenv`.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<vinnueditx>/weather-tracker.git
   cd weather-tracker

