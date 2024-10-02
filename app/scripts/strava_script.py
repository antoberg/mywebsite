import strava
from strava.api_connection import get_token
import pandas as pd
import strava.functions
import matplotlib.pyplot as plt
import numpy as np

athlete_id = 7270139
token_filename = 'strava_token'

data = get_token(token_filename, athlete_id)
access_token = data['access_token']
