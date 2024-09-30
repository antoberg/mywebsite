import json
import requests
from datetime import datetime

#%% sous-fonctions
def get_date_timestamp(timestr):
    #timestr exemple : "1999/08/06 12:00:00"
    date_object = datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S")
    timestamp = date_object.timestamp()
    return int(timestamp)

def get_current_timestamp():
    return (int(datetime.now().timestamp()))

def get_exclusion_list(timestamp):
    exclusion_list = ["current", "minutely","hourly","daily","alerts"]
    # trouve la précision la plus adaptée parmis : minutely, hourly, daily en fonction de la date en entrée
    # génère la liste d'exclusion pour la requête
    if timestamp - get_current_timestamp() <= 0:
        accuracy_str = "ERROR : ride date in the past"
    elif timestamp - get_current_timestamp() <= 3600:
        accuracy_str = "minutely"
    elif timestamp - get_current_timestamp() <= 48*3600:
        accuracy_str = "hourly"
    elif timestamp - get_current_timestamp() <= 8*24*3600:
        accuracy_str = "daily"
    else:
        accuracy_str = "ERROR : ride date too far from now"
    print("accuracy : ", accuracy_str)
    print(timestamp)
    exclusion_list.remove(accuracy_str)

    return accuracy_str, exclusion_list

def request_data(lat,lon,exclusion_list):
    
    base_url='https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&exclude={}&appid=5f49b8cafb71989d6b08e823ca0c9b2c'
    exclusion_str = ', '.join(exclusion_list)
    url=base_url.format(lat,lon,exclusion_str)
    response=requests.get(url)
    json_data = json.loads(response.text)
    return json_data

def get_closest_forecast(timestamp, json_data, accuracy_str):
    timedelta_list = [abs(timestamp-i['dt']) for i in json_data[accuracy_str]]
    timedelta_min_index = timedelta_list.index(min(timedelta_list))
    return timedelta_min_index

#%% fonction globale
def get_forecast(lat, lon, timestamp):
    # date → timestamp 
        # → exclusion_list (&coordonnées GPS) → requête openweather API : json_data (&timestamp) 
            # → données les plus proches de la requete temporelle 

    
    #obtenir la précision souhaitée dans la requete (hourly, daily, etc)
    accuracy_str, exclusion_list = get_exclusion_list(timestamp)
    # envoyer la requete et récupérer les donnes
    json_data = request_data(lat,lon, exclusion_list)
    forecast_index = get_closest_forecast(timestamp,json_data, accuracy_str)
    forecast = json_data[accuracy_str][forecast_index]
   
    if 'rain' in forecast:
        rain = forecast['rain']
        if isinstance(rain, dict):
            rain = rain['1h']
    else:
        rain = 0.0

    if isinstance(forecast['temp'],dict): #si daily
        print(forecast['temp'])
        temp = forecast['temp']['day']
    else:
        temp = forecast['temp']


    return round(forecast['wind_speed'],1), int(forecast['wind_deg']), round(temp-273.15),rain, (forecast['pop'])



#%% debug
# print(get_forecast(lat = 47.327456259651235,lon = 5.051558986476181, date_str="25/09/2024 19:50:00"))