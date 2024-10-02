import json
import os
import requests
import time
import webbrowser

client_id = '55219'
client_secret = 'efca1851af97b16a2250e408f5543dfb206aca34'
redirect_uri = 'http://localhost/'

def request_token(client_id: str, client_secret: str, code: str) -> requests.Response:
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

def refresh_token(client_id: str, client_secret: str, refresh_token: str) -> requests.Response:
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
    return response

def write_token(filename: str, athlete_id: int, token: dict):
    """
    Writes the token information to a JSON file.

    Args:
        filename (str): Name of the JSON file.
        athlete_id (int): ID of the athlete.
        token (dict): Dictionary containing token information.
    """
    if os.path.exists(f'./{filename}.json'):
        with open(f'{filename}.json', 'r') as file:
            data = json.load(file)
    else:
        data = {}

    data[f"{athlete_id}"] = token

    with open(f'{filename}.json', 'w') as file:
        json.dump(data, file)

def request_authorization(filename: str, athlete_id: int):
    """
    Initiates the authorization process with Strava.

    Args:
        filename (str): Name of the JSON file.
        athlete_id (int): ID of the athlete.
    """
    request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                    f'&response_type=code&redirect_uri={redirect_uri}' \
                    f'&approval_prompt=force' \
                    f'&scope=profile:read_all,activity:read_all'

    webbrowser.open(request_url)
    code = input('Insert the code from the url: ')

    token = request_token(client_id, client_secret, code)
    #Save json response as a variable
    strava_token = token.json()
    # Save tokens to file
    write_token(filename, athlete_id, strava_token)

def get_token(filename: str, athlete_id: int) -> dict:
    """
    Retrieves the token information from a JSON file. If the token has expired,
    it refreshes the token.

    Args:
        filename (str): Name of the JSON file containing token information.
        athlete_id (int): ID of the athlete.

    Returns:
        dict: Dictionary containing token information.
    """
    if not os.path.exists(f'./{filename}.json'):
        request_authorization(filename, athlete_id)
        with open(f'{filename}.json', 'r') as token:
            data = json.load(token)
    else:
        with open(f'{filename}.json', 'r') as token:
            data = json.load(token)

        if f"{athlete_id}" not in data or data[f"{athlete_id}"]['errors'][0]['code'] == "invalid":
            request_authorization(filename, athlete_id)
            #reopen the file after update
            with open(f'{filename}.json', 'r') as token:
                data = json.load(token)

    if data[f"{athlete_id}"]['expires_at'] < time.time():
        print('Refreshing token!')
        new_token = refresh_token(client_id, client_secret, data[f"{athlete_id}"]['refresh_token'])
        strava_token = new_token.json()
        # Update the file
        write_token(filename, athlete_id, strava_token)

    with open(f'{filename}.json', 'r') as token:
        data = json.load(token)

    return data[f"{athlete_id}"]
