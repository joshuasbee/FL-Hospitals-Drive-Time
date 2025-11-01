import folium
import geopandas as gpd
import pandas as pd
import random
import paths

data = paths.data
geojson = paths.geojson
hospitalcsv = paths.hospitals
web = paths.web
docs = paths.docs

# Base map
m = folium.Map(location=[28.5383, -81.3792], zoom_start=9)

# Load data
gdf = gpd.read_file(f"{data}/{geojson}")
hospitals = pd.read_csv(f"{data}/{hospitalcsv}")

# Assign unique colors per hospital
hospital_colors = {name: f"#{random.randint(0,0xFFFFFF):06x}" for name in hospitals['NAME']}

# Sort by county
hospitals = hospitals.sort_values(['COUNTY', 'NAME'])

current_county = None

# Add counties and hospitals in order
for _, row in hospitals.iterrows():
    county = row['COUNTY']
    hospital_name = row['NAME']
    color = hospital_colors[hospital_name]
    
    # If new county, add a county FeatureGroup first
    if county != current_county:
        county_fg = folium.FeatureGroup(name=f"County: {county.capitalize()}", show=True)
        county_fg.add_to(m)
        current_county = county
    
    # FeatureGroup for the hospital
    hospital_fg = folium.FeatureGroup(name=f"--{hospital_name}", show=True)
    
    # Add polygons for this hospital (using randomized colors)
    hospital_iso = gdf[gdf['name'] == hospital_name].sort_values('value', ascending=False)
    for feature in hospital_iso.to_dict('records'):
        folium.GeoJson(
            feature['geometry'],
            tooltip=f"{hospital_name} ({feature['value']/60:.0f} min)",
            style_function=lambda f, c=color: {
                'fillOpacity': 0.3,
                'weight': 2,
                'color': c
            }
        ).add_to(hospital_fg)
    
    # Add hospital location marker
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,
        color='black',
        fill=True,
        fill_color=color, # use the same color as travel time polygons
        fill_opacity=0.9,
        tooltip=hospital_name
    ).add_to(hospital_fg)
    
    hospital_fg.add_to(m)

# Collapsible LayerControl to toggle hospitals
folium.LayerControl(collapsed=True).add_to(m)

# Save map
m.save(f"{web}/fl_isochrones_unique_colors.html")
m.save(f"{docs}/fl_isochrones_unique_colors.html")