import pandas as pd
import requests
import numpy as np

def load_activities_to_csv(access_token: str):

    activities_url = f"https://www.strava.com/api/v3/athlete/activities"

    page = 10
    per_page = 30
    df_activities = pd.DataFrame()

    print("Loading activities ...")

    while True:
        params = {
            "access_token": access_token,
            "page": page,
            "per_page": per_page
        }

        response = requests.get(activities_url, params=params)

        if response.status_code == 200:
            activities = response.json()

            if not activities:  # No more activities to fetch
                break

            # Convert activities to DataFrame
            df_new_activities = pd.json_normalize(activities)

            # Concatenate with existing DataFrame
            df_activities = pd.concat([df_activities, df_new_activities], ignore_index=True)

            page += 1
        else:
            print(f"Error fetching activities. Status code: {response.status_code}")
            break

    df_activities.to_csv('activities.csv', index=False)
    print("Activities load into csv file.")

def load_athlete_info(access_token: str):

    athlete_url = f"https://www.strava.com/api/v3/athlete?" \
              f"access_token={access_token}"
    response = requests.get(athlete_url)
    athlete = response.json()

    print('AUTHENTIFICATED ATHLETE : ' + athlete['firstname'] + ' ' + athlete['lastname'])

def get_athlete_routes(access_token: str, athlete_id: int):

    routes_url = f"https://www.strava.com/api/v3/athletes/{athlete_id}/routes?" \
                f"access_token={access_token}"
    response = requests.get(routes_url)
    routes = response.json()
    df_routes = pd.json_normalize(routes)
    df_routes.to_csv("routes.csv", index=False)

# def activities_map(csv_file: str):
#     activities = pd.read_csv(csv_file)
#     elevations_rates = [( activities['total_elevation_gain'][index] / (activities['distance'][index])) for index, elevation in enumerate(activities['total_elevation_gain'].notna())]

#     print(elevations_rates)

#     activities = activities[activities['map.summary_polyline'].notna()]
#     activities['map.polyline'] = activities['map.summary_polyline'].apply(polyline.decode)
#     activities['url'] = 'https://www.strava.com/activities/' + activities['id'].astype(str)

   


#     tiles = ['openstreetmap','cartodbdark_matter']
#     # Créer une carte centrée sur la première activité
#     m = folium.Map(location=[activities['map.polyline'].iloc[0][0][0], activities['map.polyline'].iloc[0][0][1]], zoom_start=10)
#     folium.TileLayer(tiles[0]).add_to(m)

#     # Iterate over each ride
#     for index, row in activities.iterrows():
#         # Calculer le centroïde de la polyline pour l'activité actuelle
#         coordinates = row['map.polyline']
#         centroid = [
#             np.mean([coord[0] for coord in coordinates]),
#             np.mean([coord[1] for coord in coordinates])
#         ]
#         if elevations_rates[index] >=0.01:
#             poly_col = 'red'
#         else:
#             poly_col = 'blue'
#         # Add polyline to the map with a popup containing a link
#         folium.PolyLine(
#             coordinates,
#             color=poly_col,
#             popup=f"<a href='{row['url']}' target='_blank'>{row['name']}</a>",
#             weight=1
#         ).add_to(m)

#     # Save the map to an HTML file
#     m.save('activities.html')

# def routes_map(csv_file: str):
#     activities = pd.read_csv(csv_file)
#     activities = activities[activities['map.summary_polyline'].notna()]
#     activities['map.polyline'] = activities['map.summary_polyline'].apply(polyline.decode)

#     # Créer une carte centrée sur la première activité
#     m = folium.Map(location=[activities['map.polyline'].iloc[0][0][0], activities['map.polyline'].iloc[0][0][1]], zoom_start=10)
#     folium.TileLayer('cartodbdark_matter').add_to(m)

#     # Iterate over each ride
#     for index, row in activities.iterrows():
#         # Calculer le centroïde de la polyline pour l'activité actuelle
#         coordinates = row['map.polyline']
#         centroid = [
#             np.mean([coord[0] for coord in coordinates]),
#             np.mean([coord[1] for coord in coordinates])
#         ]

#         # Add polyline to the map with a popup containing a link
#         folium.PolyLine(
#             coordinates,
#             color='red',
#             weight=1
#         ).add_to(m)

#     # Save the map to an HTML file
#     m.save('routes.html')

# def startpoints_map(csv_file: str):
#     startpoints = pd.read_csv(csv_file)
#     startpoints = startpoints[startpoints['start_latlng'].notna()]
    
#     tiles = ['openstreetmap','cartodbdark_matter']
#     # Créer une carte centrée sur la première activité
#     m = folium.Map(location=[startpoints[0][0], startpoints[0][1]], zoom_start=10)
#     folium.TileLayer(tiles[0]).add_to(m)

#     # Iterate over each ride
#     for index, row in activities.iterrows():
#         # Calculer le centroïde de la polyline pour l'activité actuelle
#         coordinates = row['map.polyline']
#         centroid = [
#             np.mean([coord[0] for coord in coordinates]),
#             np.mean([coord[1] for coord in coordinates])
#         ]

#         # Add polyline to the map with a popup containing a link
#         folium.PolyLine(
#             coordinates,
#             color='red',
#             popup=f"<a href='{row['url']}' target='_blank'>{row['name']}</a>",
#             weight=1
#         ).add_to(m)

#     # Save the map to an HTML file
#     m.save('activities.html')
