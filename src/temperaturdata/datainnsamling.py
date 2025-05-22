import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os

"""
Script for å hente timesoppløst historisk temperaturdata fra Open-Meteo Archive API.

Funksjonalitet:
- Bruker Open-Meteo sitt "archive" API til å laste ned timesdata for ønsket periode og posisjon (her: Trondheim, 1950 til 2025).
- Robust mot nettverksfeil med caching og automatisk retry ved feil eller timeouts.
- Transformerer de hentede dataene til et pandas DataFrame, med kolonnene 'date' (tidspunkt) og 'temperature_2m' (lufttemperatur 2 meter over bakken).
- Skriver ut litt metadata (koordinater, tidssone, høyde) for å verifisere hentet område.
- Lagrer ferdig behandlet data som CSV-fil i mappen ../data/temperaturdata/ (to nivå over denne filens plassering).

Forutsetninger:
- Krever installert: openmeteo_requests, requests_cache, retry_requests, pandas.
- Scriptet bør kjøres fra src/temperaturdata/-mappa eller tilsv. struktur for at filstier skal stemme.

Bruksområde:
- Egner seg til automatisert uthenting og lagring av store mengder meteorologisk timesdata for videre analyse og rensing.

Eksempel på utdata:
- CSV-fil: 'data/temperaturdata/temperaturdata.csv' med alle timer fra 1950-01-01 til 2025-03-22.

"""


# Setup: cache og retry for stabil API-tilgang
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# API-parametere
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 63.43,
    "longitude": 10.39,
    "start_date": "1950-01-01",
    "end_date": "2025-03-22",
    "hourly": "temperature_2m"
}

# Hent data
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Debug-info
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Behandle timebasert temperaturdata
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly_temperature_2m
}

hourly_dataframe = pd.DataFrame(data=hourly_data)
print(hourly_dataframe)

# --- Lagre som CSV i ../data/temperaturdata/ ---
# Finn base directory (2 nivå opp fra src/temperaturdata/)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
output_dir = os.path.join(base_dir, "data", "temperaturdata")
os.makedirs(output_dir, exist_ok=True)

# Skriv til CSV-fil
output_path = os.path.join(output_dir, "temperaturdata.csv")
hourly_dataframe.to_csv(output_path, index=False)

print(f"✅ Data lagret til: {output_path}")
