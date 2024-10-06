# ====================== Importations ======================

import gpxpy
import folium
from folium.plugins import AntPath,Fullscreen
import numpy as np
import pandas as pd
import os
from datetime import datetime

def get_current_timestamp():
    return (int(datetime.now().timestamp()))

# ================== MANIPULATION GPX =================

def read_gpx(fichier_gpx):
    with open(fichier_gpx, 'r',encoding='utf-8', errors='replace') as f: #Utf-8 important pour la lecture des emojis dans les titres strava
        gpx = gpxpy.parse(f)

    coords = []
    ele = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))
                ele.append(point.elevation)

    # print(coords)
    return coords,ele

def make_route_df(coords,ele):
    distance=[]#m
    dz=[]
    dz.append(0.0)
    distance.append(0.0)
    
    for i,p in enumerate(coords):
        if i>0:
            dx = (calc_distance(coords[i-1][0],p[0],coords[i-1][1],p[1] ))
            dz.append( ele[i]-ele[i-1])
            
            distance.append(distance[i-1]+dx)

    df = pd.DataFrame(
        {
        'coords' : coords,
        'distance' : distance,
        'elevation' : ele,
        'dz' : dz
        }
    )

    return df

def calc_travel_time(coords, speed):
    #calcul de la distance et du temps écoulé
    #speed en m/s
    distance=[]#m
    time=[] #secs
    distance.append(0.0)
    time.append(0)
    for i,p in enumerate(coords):
        if i>0:
            dx = (calc_distance(coords[i-1][0],p[0],coords[i-1][1],p[1] ))
            distance.append(distance[i-1]+dx)
            dt = (dx/speed)
            time.append(int(round(time[i-1]+dt)))
    df = pd.DataFrame(
        {
        "coords" : coords,
        "distance" : distance,
        "time" : time 
        }
    )
    return df

def calc_distance(laA,laB,loA,loB): 
    laA=laA*np.pi/180
    laB=laB*np.pi/180
    loA=loA*np.pi/180
    loB=loB*np.pi/180
    
    dist=6371*2*np.arcsin(np.sqrt(np.sin((laB-laA)/2)**2+np.cos(laA)*np.cos(laB)*np.sin((loB-loA)/2)**2))
    
    return dist*1000 #m

# ========================== CREATION MAP FOLIUM =======================================           

def create_map(coords):
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    center_lat = (max(lats)+min(lats))/2
    center_lon = (max(lons)+min(lons))/2
    m = folium.Map(location=[center_lat,center_lon],zoom_start=11)
    Fullscreen(position='topright', title='Plein écran', titleCancel='Quitter plein écran').add_to(m)
    folium.Marker(coords[0],popup='start',icon=folium.Icon(icon='play',color='green')).add_to(m)
    folium.Marker(coords[len(coords)-1],popup='finish',icon=folium.Icon(icon='stop',color='red')).add_to(m)
    #animation montrant le sens du parcours
    ant_path = AntPath(coords, color="blue", weight=5, opacity=0.7, dash_array=[10, 20],delay = 1000)
    ant_path.add_to(m)
    folium.PolyLine(coords,color='red',).add_to(m)
    return m

def save_map(m, DIRECTORY : os.path):
    ts = str(get_current_timestamp())
    template_file_path = os.path.join(DIRECTORY, f'map_{ts}.html')
    m.save(template_file_path)
    return ts

def get_bearing(p1,p2):
    # calcul de l'orientation des vecteurs vent
    long_diff=np.radians(p2[1]-p1[1])
    lati1=np.radians(p1[0])
    lati2=np.radians(p2[0])
    x=np.sin(long_diff)*np.cos(lati2)
    y = (np.cos(lati1)*np.sin(lati2)-(np.sin(lati1)*np.cos(lati2)* np.cos(long_diff)))
    bearing = np.degrees(np.arctan2(x, y))
    if bearing < 0:
        return bearing + 360
    return bearing

def make_wind_vector(lat,lon,wind_speed, wind_dir, total_distance):
    #construction des vecteurs vent à un point (lat, lon)
    norm_arrow=0.0001*total_distance/1000*wind_speed/3.6
    if wind_dir<270:
        angle=np.radians(270-wind_dir)
    else:
        angle=np.radians(630-wind_dir)            
    dir_lat=norm_arrow*np.sin(angle)
    dir_lon=norm_arrow*np.cos(angle)
    A = (lat,lon)
    B = (lat+dir_lat,lon+dir_lon)
    orientation = get_bearing((lat,lon), (lat+dir_lat,lon+dir_lon))-90
       
    return A,B, orientation

from scripts.weather_script import get_forecast, get_date_timestamp
# ========================== WEATHER → MAP =======================================

def get_weather(coords, date_string ,bike_speed):
    #exemple date_str="25/09/2024 19:50:00" #speed m/s
    #points auquels on récupère la météo
    df = calc_travel_time(coords,bike_speed)
    print(df)
    #durée entre chaque relevé en secondes
    time_step = 20*60
    nb_indexes = round(max(df['time'])/time_step-1)
    print('nombre indexes météo : ',nb_indexes)
    weather_indexes = np.linspace(0,len(coords)-1,nb_indexes).astype(int)
    print(weather_indexes)
    
    

    df = df.iloc[weather_indexes]
    

    speedl = []
    degl = []
    templ=[]
    rainl=[]

    timestamp = get_date_timestamp(date_string)
    print('target_timestamp',timestamp)
    
    for i in weather_indexes:
        
        ts = timestamp + df['time'][i]
        speed, deg, temp, rain, pop = get_forecast(df['coords'][i][0],df['coords'][i][1], ts)
        speedl.append(speed)
        degl.append(deg)
        templ.append(temp)
        rainl.append(rain)
    
    
    
    df['wind_speed'] = speedl
    df['wind_deg'] = degl
    df['temp'] = templ
    df['rain'] = rainl

    df = df.reset_index(drop=True)

    return df
    
def add_wind_vectors_to_map(df_weather, m):
    total_distance = max(df_weather['distance'])
    print(str(total_distance/1000)+'kms')
    for i,v in enumerate(df_weather['coords']):
        A,B, orientation = make_wind_vector(v[0],v[1],wind_speed=df_weather['wind_speed'][i],wind_dir=df_weather['wind_deg'][i],total_distance=total_distance)
        print (A,B)
        folium.PolyLine([A,B],color='black').add_to(m)
        folium.RegularPolygonMarker(B,fill_opacity=100,opacity=100,fill_color='black',color='black',number_of_sides=3,radius=10,rotation=orientation,popup='speed : '+str(round(df_weather['wind_speed'][i]*3.6))+' km/h').add_to(m)

    return m

#==========================  COORDINATION DES FONCTIONS ===================================

def make_map(filepath, date_str, speed, DIRECTORY : os.path):
    coords, ele = read_gpx(filepath)
    df_route= make_route_df(coords, ele)
    coords = df_route['coords']
    m = create_map(coords)
    if date_str != 'nan':
        df_weather = get_weather(coords, date_str, speed)
        m = add_wind_vectors_to_map(df_weather, m)

    else:
        df_weather = pd.DataFrame({
            'distance':[],
            'wind_speed':[],
            'temp':[],
            'rain':[]
        })
    
    return save_map(m, DIRECTORY), df_route, df_weather
    
# ========================== DEBUG ===============================================

# current_dir = os.path.dirname(os.path.abspath(__file__))
# exemple_gpx_file = os.path.join(current_dir, '../gpx_files/Rome.gpx')
# make_map(filepath=exemple_gpx_file, date_str='25/09/2024 19:50:00', speed=30/3.6)


