import requests
import geopandas as gpd
from shapely.geometry import shape
import pandas as pd
import time
import paths

data = paths.data
hospitals = paths.hospitals

# Get the API_KEY
with open("key.txt", "r", encoding="utf-8") as f:
    API_KEY = f.read().strip()

# Add key to headers
headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}
# https://account.heigit.org/manage/key
BASE_URL = "https://api.openrouteservice.org/v2/isochrones/driving-car"

locations = pd.read_csv(f"{data}/{hospitals}")

features = []

for _, row in locations.iterrows():
    params = {
        "locations": [[row["LONGITUDE"], row["LATITUDE"]]],
        "range": [300, 600, 900]  # 5, 10, 15 minutes in seconds
    }
    
    response = requests.post(BASE_URL, headers=headers, json=params)  # Send headers
    
    if response.status_code != 200:
        print(f"Error fetching isochrone for {row['NAME']}: {response.text}")
        continue
    
    data = response.json()
    
    for feature in data.get("features", []):
        feature["properties"]["name"] = row["NAME"]
        features.append(feature)

    time.sleep(3.01) # to avoid hitting my rate limit of 20 per minute

# Convert to GeoDataFrame and save as GeoJSON
gdf = gpd.GeoDataFrame.from_features(features)
gdf.to_file(f"{data}/drive_time_isochrones.geojson", driver="GeoJSON")

print("Isochrones generated and saved.")
