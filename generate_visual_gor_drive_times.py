import folium
import geopandas as gpd
import pandas as pd
import paths

data = paths.data
hospitalcsv = paths.hospitals
geojson = paths.geojson
web = paths.web
docs = paths.docs

# Base map
m = folium.Map(location=[28.5383, -81.3792], zoom_start=9)

# Load data
gdf = gpd.read_file(f"{data}/{geojson}")
hospitals = pd.read_csv(f"{data}/{hospitalcsv}")

# Sort hospitals by county, then name
hospitals = hospitals.sort_values(['COUNTY', 'NAME'])

# Create a dict to store county groups
county_groups = {}

# Create FeatureGroups for each hospital and store by county
for _, row in hospitals.iterrows():
    county = row['COUNTY']
    hospital_name = row['NAME']

    # FeatureGroup for the hospital
    hospital_fg = folium.FeatureGroup(name=f"--{hospital_name}", show=True)

    # Add polygons for this hospital
    hospital_iso = gdf[gdf['name'] == hospital_name].sort_values('value', ascending=False)
    for feature in hospital_iso.to_dict('records'):
        value = feature['value']
        color = 'green' if value <= 300 else 'orange' if value <= 600 else 'red'
        folium.GeoJson(
            feature['geometry'],
            name=feature['name'],
            tooltip=f"{feature['name']} ({feature['value']/60:.0f} min)",
            style_function=lambda f, v=feature['value']: {
                'fillOpacity': 0,
                'weight': 2,
                'color': 'green' if v <= 300 else 'orange' if v <= 600 else 'red',
            }
        ).add_to(hospital_fg)

    # Add hospital location marker
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,
        color='black',
        fill=True,
        fill_color='black',
        fill_opacity=0.8,
        tooltip=hospital_name
    ).add_to(hospital_fg)

    # Add hospital FeatureGroup to the correct county group
    if county not in county_groups:
        county_groups[county] = []
    county_groups[county].append(hospital_fg)

# Now add county headers and hospitals to the map
for county, hospital_list in county_groups.items():
    # Add a "header" FeatureGroup for the county
    county_fg = folium.FeatureGroup(name=f"County: {county.capitalize()}", show=True)
    county_fg.add_to(m)

    # Add all hospital FeatureGroups under this county
    for hospital_fg in hospital_list:
        hospital_fg.add_to(m)

# Collapsible LayerControl to toggle hospitals
folium.LayerControl(collapsed=True).add_to(m)

# Save map
m.save(f"{web}/fl_isochrones_GOR.html")
m.save(f"{docs}/index.html")