# ====================== Importations ======================

import json
import os
import requests
import time

# ================== Constantes et Variables =================

client_id = '55219'
client_secret = 'efca1851af97b16a2250e408f5543dfb206aca34'

# =================== FONCTIONS GENERIQUES =========================
def get_athlete_token(athlete_id, tokenPath : os.path): #--> renvoit le token d'un athlete donné
    """
    Fonction perso pour faciliter l'accès au token dans l'app
    si il existe
    - renvoit le json de l'athlete en question tq : { "id" : {}} 
    - sinon renvoit None
    """
    with open(tokenPath, 'r') as token:
                data = json.load(token)

    filled=0
    for i,v in enumerate(data):
        dict_id = next(iter(v))
        
        if dict_id == str(athlete_id) and filled == 0:
            data_athlete = data[i][dict_id]
            filled = 1
    
    if filled == 0:
        data_athlete = None

    return data_athlete

def write_token(athlete_id: int, token: dict, tokenPath : os.path):
    """
    Writes the token information to a JSON file.

    Args:
        filename (str): Name of the JSON file.
        athlete_id (int): ID of the athlete.
        token (dict): Dictionary containing token information.
    """
    
    if os.path.exists(tokenPath):
        with open(tokenPath, 'r') as file:
            data = json.load(file)

        filled=0
        for i,v in enumerate(data):
            dict_id = next(iter(v))
            print(dict_id)
            if dict_id == str(athlete_id) and filled == 0:
                data[i][dict_id] = token
                filled = 1
        
        if filled == 0:
            athlete_data = {}
            athlete_data[f"{athlete_id}"] = token
            data.append(athlete_data)
            
    else:
        data = []
        athlete_data = {}
        athlete_data[f"{athlete_id}"] = token
        data.append(athlete_data)

    with open(tokenPath, 'w') as file:
        json.dump(data, file)

# =================== RECUPERATION TOKEN VALIDE =========================


def check_token_validity(athlete_id: int, tokenPath : os.path):
    """
    - Vérifier si l'utilisateur est bien connecté et à accès au données
    - Rafraichis le token
    """
    
    access = False
    if os.path.exists(tokenPath): #------>existence du fichier ? (quasi garanti)
        with open(tokenPath, 'r') as token:
            data = json.load(token)

        access_string = "athlete id absent du json"
        for ath in data: #------> ID présent ?
            if f"{athlete_id}" in ath: 
                athlete = ath[f"{athlete_id}"]
                if 'errors' in athlete: #------> erreurs ?
                    access_string = "access token erroné dans le json"
                else:
                    username = athlete['athlete']['username']
                    if athlete['expires_at'] < time.time(): #------> token expiré ?
                        refresh_token(client_id, client_secret, athlete['refresh_token'], athlete_id)
                        access_string = f'{username} connecté - access token refreshed car il était expiré'
                    else:
                        access_string = f'{username} connecté avec succès'
                        access = True
            break
                


    else:
        access_string = "strava_token.json inexistant"

    print('=======================================')
    print('ACCES AU DONNES STRAVA :',access_string)
    print('id :',athlete_id)
    print('=======================================')
    return access

def request_token(code: str) -> requests.Response:

    """
    Requests an access token from the Strava API using the provided code.

    Args:
        client_id (str): Strava API client ID.
        client_secret (str): Strava API client secret.
        code (str): Authorization code obtained after user authentication.

    Returns:
        requests.Response: Response object containing token information.
    """
    response = requests.post(url='https://www.strava.com/oauth/token',
                             data={'client_id': client_id,
                                   'client_secret': client_secret,
                                   'code': code,
                                   'grant_type': 'authorization_code'})
    return response

def request_authorization(redirect_uri : str):
    """
    Initiates the authorization process with Strava.

    Args:
        filename (str): Name of the JSON file.
        athlete_id (int): ID of the athlete.
    """
    #----> important : approval_prompt : auto permet de se connecter sans demander les authorisations à chaque fois, sinon mettre force
    request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                    f'&response_type=code&redirect_uri={redirect_uri}' \
                    f'&approval_prompt=auto' \
                    f'&scope=profile:read_all,activity:read_all,read'

    # webbrowser.open(request_url)
    return request_url
 
def refresh_token(client_id: str, client_secret: str, refresh_token: str, athlete_id, tokenPath : os.path) -> requests.Response:
    """
    Requests a new access token using a refresh token.

    Args:
        client_id (str): Strava API client ID.
        client_secret (str): Strava API client secret.
        refresh_token (str): Refresh token obtained during initial authentication.

    Returns:
        requests.Response: Response object containing the new token information.
    """
    response = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                             data={'client_id': client_id,
                                   'client_secret': client_secret,
                                   'grant_type': 'refresh_token',
                                   'refresh_token': refresh_token})
    
    new_token = response.json()
    with open(tokenPath, 'r') as token:
                data = json.load(token)

    data = get_athlete_token(athlete_id)

    data['access_token'] = new_token['access_token']
    data['expires_at'] = new_token['expires_at']
    data['expires_in'] = new_token['expires_in']
    data['refresh_token'] = new_token['refresh_token']
    
    write_token(data, tokenPath)



