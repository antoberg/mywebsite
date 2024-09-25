import gpxpy
import folium
from folium.plugins import AntPath
import numpy as np
import pandas as pd
import os

def read_gpx(fichier_gpx):
    with open(fichier_gpx, 'r') as f:
        gpx = gpxpy.parse(f)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    # print(coords)
    return coords


#%% calculs distance et temps
#calcul de la distance et du temps écoulé
def calc_travel_time(coords, speed):
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

#%% création de la map
def create_map(coords):
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    center_lat = lats[round(len(coords)/2)]
    center_lon = lons[round(len(coords)/2)]
    
    m = folium.Map(location=[center_lat,center_lon])

    #Indiquer le sens du parcours
    # ant_path = AntPath(coords, color="blue", weight=5, opacity=0.7, dash_array=[10, 20],delay = 1000)
    # ant_path.add_to(m)

    
    folium.PolyLine(coords,color='red',).add_to(m)

    return m

#%% ajout de la météo à la map
#Fonction d'orientation des vecteurs-vents
def get_bearing(p1,p2):
    long_diff=np.radians(p2[1]-p1[1])
    lati1=np.radians(p1[0])
    lati2=np.radians(p2[0])
    x=np.sin(long_diff)*np.cos(lati2)
    y = (np.cos(lati1)*np.sin(lati2)-(np.sin(lati1)*np.cos(lati2)* np.cos(long_diff)))
    bearing = np.degrees(np.arctan2(x, y))
    if bearing < 0:
        return bearing + 360
    return bearing

#construction des vecteurs vent à un pt précis
def make_wind_vector(lat,lon,wind_speed, wind_dir, total_distance):
 
    
    norm_arrow=0.0001*total_distance/1000*wind_speed/3.6

    print(wind_dir)
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

def get_weather(coords, date_string ,bike_speed):
    #exemple date_str="25/09/2024 19:50:00" #speed m/s
    #points auquels on récupère la météo
    df = calc_travel_time(coords,bike_speed)
    print(df)
    weather_indexes = np.linspace(0,len(coords)-1,10).astype(int)
    print(weather_indexes)
    

    df = df.iloc[weather_indexes]
    

    speedl = []
    degl = []

    timestamp = get_date_timestamp(date_string)
    
    for i in weather_indexes:
        
        timestamp += df['time'][i]
        speed, deg = get_forecast(df['coords'][i][0],df['coords'][i][1], timestamp)
        speedl.append(speed)
        degl.append(deg)
    
    
    
    df['wind_speed'] = speedl
    df['wind_deg'] = degl

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
def save_map(m):
    

    # Construire le chemin vers le fichier dans 'tools/templates'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(current_dir, '../templates/gpx_viewer.html')
    m.save(template_file_path)

#%% FONCTION GLOBALE

def make_map(filepath, date_str, speed):
    coords = read_gpx(filepath)

    #création de la map
    m = create_map(coords)
    print(m)
    if date_str != '':
        #récupération de la météo
        df_weather = get_weather(coords, date_str, speed)
        print(df_weather)
        #ajout des vecteurs vent
        m = add_wind_vectors_to_map(df_weather, m)
        #sauvegarde de la map dans un fichier
        save_map(m)
        
        

#%% DEBUG
# current_dir = os.path.dirname(os.path.abspath(__file__))
# exemple_gpx_file = os.path.join(current_dir, '../gpx_files/Rome.gpx')
# make_map(filepath=exemple_gpx_file, date_str='25/09/2024 19:50:00', speed=30/3.6)


