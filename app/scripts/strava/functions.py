import pandas as pd
import requests
import numpy as np
import os



#=================== GETTING ATHLETE INFOS ======================================

def load_athlete_info(access_token: str):

    athlete_url = f"https://www.strava.com/api/v3/athlete?" \
              f"access_token={access_token}"
    response = requests.get(athlete_url)
    athlete = response.json()

    print('AUTHENTIFICATED ATHLETE : ' + athlete['firstname'] + ' ' + athlete['lastname'])

#=================== GETTING ROUTES ======================================

def get_athlete_routes(access_token: str, athlete_id: int):

    routes_url = f"https://www.strava.com/api/v3/athletes/{athlete_id}/routes?" \
                f"access_token={access_token}&" \
                "per_page=10"
    
    response = requests.get(routes_url)
    routes = response.json()

    namid=[]
    for r in routes:
        namid.append((r['name'],r['id_str']))
    
    return namid
    
def get_route_GPX(access_token: str, route_id: str, GPX_DIRECTORY : os.path):
    filepath = os.path.join(GPX_DIRECTORY, f"{route_id}.gpx")
    if not os.path.isfile(filepath): #on envoit la requête que si on a pas le fichier
        route_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
        response = requests.get(route_url, headers={'Authorization': f'Bearer {access_token}'})
        with open(filepath, "wb") as file:
                file.write(response.content)