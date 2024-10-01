from flask import Flask, render_template, request, jsonify
import numpy as np
import scripts.startlist_script as ss
import scripts.map_script as ms
from datetime import datetime, timedelta
import time
import os   

#versionner les fichiers statics pour éviter d'utiliser ceux en cache navigateur
current_time = int(time.time())

app = Flask(__name__)

FILE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_dashboard_files')
GPX_FILES_DIRECTORY = os.path.join(FILE_DIRECTORY, 'gpx_files')
GPX_FILES_DIRECTORY_RECENT =  os.path.join(os.path.join(GPX_FILES_DIRECTORY, 'recent'))
GPX_FILES_DIRECTORY_RACES =  os.path.join(os.path.join(GPX_FILES_DIRECTORY, 'races'))


@app.route('/')
def index():
    recent_files = os.listdir(os.path.join(GPX_FILES_DIRECTORY, 'recent'))
    race_files = os.listdir(os.path.join(GPX_FILES_DIRECTORY, 'races'))
    
    return render_template('index.html', time = current_time, race_files=race_files,recent_files=recent_files)


#%% STARTLIST TOOLS

@app.route('/tools/startlist/')
def route_startlist():
    app.logger.info('Startlist route was accessed')
    return render_template('startlist.html')




#Fonction pour traiter la recherche (script Python à exécuter)
@app.route('/rechercher', methods=['POST'])
def rechercher():
    query = request.form['search']  # Récupère la requête de recherche
    print(query)
    if not query or query.strip() == "":
        result = "Veuillez entrer une URL valide", 400
        return render_template('startlist.html', resultats = result)

    try:
        # Effectuer une action avec la valeur recherchée
        startlist, id, name = ss.get_startlist(query)
        

        
        result = '<br>'.join('-'+startlist['name'])
        result = name +' ('+str(len(startlist['name']))+'):<br><br>' + result

        
        # result = query

        print(result)
        return render_template('startlist.html', resultats = result)

        #return result
    except Exception as e:
        result= f"Erreur lors de la requête : {e}", 500
        return render_template('startlist.html', resultats = result)
    
#%% MAP TOOLS




# @app.route('/map/')
# def route_map():
#     default_date = datetime.now().strftime('%Y-%m-%d')  
#     default_time = (datetime.now() + timedelta(hours=1)).strftime('%H:%M') 
#     return render_template('map_settings.html', default_date=default_date, default_time = default_time)
#     #pour affichier la liste des fichiers
#     try:
#         # Récupérer la liste des fichiers dans le dossier
#         file_list = os.listdir(FILE_DIRECTORY)
#         app.logger.info(f"Fichiers trouvés: {file_list}")
#         return render_template('map.html', files=file_list)
#     except Exception as e:
#             app.logger.error(f"Erreur lors de l'accès au dossier: {e}")
#             return "Erreur lors de l'accès aux fichiers.", 500
        




@app.route('/submit' , methods=['POST'])
def submit_form():
    weather_request = 'hidden' #par défaut
    if not request.form['date']:
        time_string='nan'
    elif not request.form['time']:
        time_string = 'nan'
    else:
        time_string = request.form['date']+' '+request.form['time']+':00'
        weather_request = ''

    print(time_string)
    print(request.files)

   


    if ('gpxFile' in request.files) and request.files['gpxFile'].filename != '' :

        file = request.files['gpxFile']
        print(file)

    
        if  not (file and file.filename.endswith('.gpx')):
            return "Fichier GPX importé mais format ou extension non valide"

        else:
            
            files_dir = os.path.join(FILE_DIRECTORY, 'gpx_files')
            filepath = os.path.join(files_dir, file.filename)
            file.save(filepath)

            print(filepath)
            name = file.filename.split('.gpx')[0] 
            return open_map(filepath,time_string,int(request.form['speed'])/3.6,name,weather_request)
    

    
    else:

        if('filename' in request.form) and request.form.get('filename') != '':
            
            
            filename = request.form.get('filename')
            print('filename',filename, request.form)
            name = filename.split('.gpx')[0]
            filepath = os.path.join(GPX_FILES_DIRECTORY_RECENT, filename)
            if not os.path.isfile(filepath):
                filepath = os.path.join(GPX_FILES_DIRECTORY_RACES, filename)
                if not os.path.isfile(filepath):
                    return "Fichier sélectionné introuvable"
                
            return open_map(filepath,time_string,int(request.form['speed'])/3.6,name, weather_request)
        else:
            return "Aucun fichier importé ni sélectionné"
    


def open_map(filepath, time_str,speed,name,weather_request):
    
    
    ts, df_route, df_weather = ms.make_map(filepath,time_str,speed)
    #clé pour actualiser les statics du dashboard
    
    print(ts)
    #calculs sur df
    total_dist = round(max(df_route['distance'])/1000)
    asc = round(sum([x for x in df_route['dz'] if x>0]))
    desc = round(sum([x for x in df_route['dz'] if x<0]))
    dist_list = [round(x/1000) for x in df_route['distance']]
    dist_weather_list = [round(x/1000) for x in df_weather['distance']]
    ele_list = [round(x) for x in df_route['elevation']]
    wind_data = [round(x*3.6) for x in df_weather['wind_speed']]
    

    


    return render_template('map_dashboard.html', time = current_time, map_url='static/maps/map'+ts+'.html', 
                           title= name, dist=total_dist, asc=asc,desc=desc, x_data = dist_list, y_data = ele_list,
                           weather_request=weather_request,#=active si la météo est requise par le user
                           x_weather_data = dist_weather_list, wind_data=wind_data,temp_data = list(df_weather['temp']), rain_data = list(df_weather['rain']))



# a delete en production car lancé via wsgi.py
if __name__ == '__main__':
    app.run(debug=True)


