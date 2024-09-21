import gpxpy
import folium
from folium.plugins import AntPath
import numpy as np
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
def get_wind(lats,lons):
    wind_dir = 120
    wind_speed = 12
    kms = 100
    dir_lat=0
    dir_lon=0  
    points=[]
    bearings=[]
    indexes = np.linspace(0,len(lats)-1,10,dtype=int)
    
    for i in indexes:
        norm_arrow=0.0001*kms*wind_speed/3.6
        if wind_dir<270:
            angle=np.radians(270-wind_dir)
        else:
            angle=np.radians(630-wind_dir)            
        dir_lat=norm_arrow*np.sin(angle)
        dir_lon=norm_arrow*np.cos(angle) 
        point = [(lats[i],lons[i]),(lats[i]+dir_lat,lons[i]+dir_lon)]
        points.append(point)   
        bearings.append(get_bearing(point[0],point[1])-90)

    # print(points,bearings)
    return points,bearings

def make_map(coords):
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    center_lat = lats[round(len(coords)/2)]
    center_lon = lons[round(len(coords)/2)]
    
    m = folium.Map(location=[center_lat,center_lon])

    #Indiquer le sens du parcours
    ant_path = AntPath(coords, color="blue", weight=5, opacity=0.7, dash_array=[10, 20],delay = 1000)
    # ant_path.add_to(m)

    #ajout du vent
    # wind_vectors,wind_bearing = get_wind(lats,lons)
    # for index,vector in enumerate(wind_vectors):
        
    #     folium.PolyLine(vector,color='black').add_to(m)
    #     folium.RegularPolygonMarker(vector[1],fill_opacity=100,opacity=100,fill_color='black',color='black',number_of_sides=3,radius=10,rotation=wind_bearing[index],popup='-60').add_to(m)

    folium.PolyLine(coords,color='red',).add_to(m)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construire le chemin vers le fichier dans 'tools/templates'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(current_dir, '../templates/gpx_viewer.html')
    m.save(template_file_path)



    
    
