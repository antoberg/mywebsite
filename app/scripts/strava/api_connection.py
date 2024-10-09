# ====================== Importations ======================

import json
import os
import requests
import time
import pandas as pd
import data.initiate_db as db

# ================== Constantes et Variables =================

client_id = '55219'
client_secret = 'efca1851af97b16a2250e408f5543dfb206aca34'


# =================== RECUPERATION TOKEN VALIDE =========================

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
 
def refresh_token(refresh_token: str, athlete_id, users_db_path : os.path) -> requests.Response:
    
    

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
    new_token_dict = {'access_token' : new_token['access_token'],'expires_at':new_token['expires_at'],
                      'refresh_token':new_token['refresh_token']}
    
    return new_token
    



