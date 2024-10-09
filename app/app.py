# ====================== Importations ======================

from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import numpy as np
import scripts.startlist_script as ss
import scripts.map_script as ms
from scripts.strava import api_connection as scon
from scripts.strava import functions as sfun
import os
from datetime import datetime, timedelta
import time
import os   
import pandas as pd
import data.initiate_db as db
import glob
# ================== Constantes et Variables =================

# ---- ROOT DIRECTORY DATA
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# ---- FICHIERS GPX
GPX_FILES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'gpx_files')
GPX_FILES_DIRECTORY_TEMP = os.path.join(GPX_FILES_DIRECTORY, 'cache_routes') # routes importées par user sans compte
GPX_FILES_DIRECTORY_USER =  os.path.join(GPX_FILES_DIRECTORY, 'user_routes') # routes importées par user connecté


# ----  CARTES FOLIUM
MAPS_FILES_DIRECTORY_TEMP = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), 'cache_maps')

# ---- DONNEES UTILISATEURS
users_db_path = os.path.join(DATA_DIRECTORY, 'users.csv')
routes_db_path = os.path.join(DATA_DIRECTORY, 'routes.csv')

## constantes
current_time = int(time.time())
strava_connect_status0 = "No connected athlete"
strava_connect_status1 = 'Connected as {}'
connect_btn0 = 'Connect'
connect_btn1 = 'Disconnect'
sections = ['home', 'gpxplorer', 'events', 'settings']

# ====================== FONCTIONS GENERALES ===========================
def toggle_sections(section : str):
    '''
    renvoit une liste de strings utilisés pour render les template 
    et gérer l'affichage des sections en CSS
    '''
    result = []
    for s in sections:
        if s == section:
            result.append("active")
        else:
            result.append('hidden')
    return result

def render_dashboard(gpx_path  : os.path, time_str : str, speed : int , title : str):

    ts, df_route, df_weather = ms.make_map(gpx_path,time_str,speed,MAPS_FILES_DIRECTORY=MAPS_FILES_DIRECTORY_TEMP)

    if time_str: #vérifie si la météo est demandée
        weather_request = '' # sert à cacher ou afficher la section météo dans le dashboard
    else:
        weather_request = 'hidden'
    #calculs sur df
    total_dist = round(max(df_route['distance'])/1000)
    asc = round(sum([x for x in df_route['dz'] if x>0]))
    desc = round(sum([x for x in df_route['dz'] if x<0]))
    dist_list = [round(x/1000) for x in df_route['distance']]
    dist_weather_list = [round(x/1000) for x in df_weather['distance']]
    ele_list = [round(x) for x in df_route['elevation']]
    wind_data = [round(x*3.6) for x in df_weather['wind_speed']]
    
    # map_filepath = os.path.join(MAPS_FILES_DIRECTORY, f'map_{ts}.html')
    # map_filepath = f'map_dashboard_files/folium_maps/map_{ts}.html'
    map_url = url_for('static', filename=f'cache_maps/map_{ts}.html')

    

    return render_template('map_dashboard.html', time = current_time, map_url=map_url, 
                           title= title, dist=total_dist, asc=asc,desc=desc, x_data = dist_list, y_data = ele_list,
                           weather_request=weather_request,#=active si la météo est requise par le user
                           x_weather_data = dist_weather_list, wind_data=wind_data,temp_data = list(df_weather['temp']), rain_data = list(df_weather['rain'])
                           )

#regroupement du render template pour éviter les répétitions dans les fonctions
def render_index(connect_status : str, section : str):

    if connect_status == 'in':
        
        user = read_user(session['user_id'])
        
        
        username = user['firstname']+' '+user['lastname']
        strava_connect_status = strava_connect_status1.format(username)
        connect_btn = connect_btn1

        #recherche des routes à afficher
        if section == 'gpxplorer':
            df_routes = pd.read_csv(routes_db_path)
            user_routes_indexes = df_routes.index[df_routes['user_id'] == user['user_id']].tolist()
            user_file_ids = df_routes['file_id'][user_routes_indexes]
            user_file_names=df_routes['route_name'][user_routes_indexes]
            file_dict = {file_id: file_name for file_id, file_name in zip(user_file_ids, user_file_names)}
        else:
            file_dict = {'Aucun fichier':''}


    else:
        username = ''
        strava_connect_status = strava_connect_status0
        connect_btn = connect_btn0
        file_dict = {'Connexion requise':''}

    if section =='':
        section ='home'
    
    section1,section2,section3,section4 =toggle_sections(section)

    


    
    return render_template('index.html', title=section,
                            status = connect_status, username = username, #---------> session en cours
                            connect_btn = connect_btn, strava_connect_status=strava_connect_status, #------>status de la connexion
                            section1=section1,section2=section2,section3=section3,section4=section4, #------> section à activer
                            time = current_time, file_dict=file_dict #-----> section MAP
                            )

def read_user(user_id):    
    """
    Renvoit les informations d'un athlète donné
    Renvoit False si user inconnu
    ----
    Arg : id user (!= athlete id)
    Resp : infos user en {dict} | None
    """
    df_users = pd.read_csv(users_db_path)
    if user_id in df_users['user_id'].values:
        index = df_users.index[df_users['user_id'] == user_id].tolist()[0] #on récupère l'index du user dans la db
        return df_users.iloc[index].to_dict() #on renvoit le dict correspondant à la ligne avec les key utilisables
    else:
        return False

def clear_temp_files(TARGET_DIRECTORY): 
    #Au démarrage de l'app : Supprime tous les fichiers dans le dossier temporaire
    for file in glob.glob(os.path.join(TARGET_DIRECTORY, '*')):
        try:
            os.remove(file)
            print(f"Supprimé: {file}")
        except Exception as e:
            print(f"Erreur lors de la suppression de {file}: {e}")


# ====================== ROUTES FLASK ===========================
app = Flask(__name__)
clear_temp_files(MAPS_FILES_DIRECTORY_TEMP)
clear_temp_files(GPX_FILES_DIRECTORY_TEMP)
#session Keys : 'user_id'



@app.route('/')#redirect du nom de domaine
def redirect_to_home():
        return redirect(url_for('index', var = 'home'), 301)

@app.route('/<var>') 
def index(var):
    '''
intercepte les différentes requetes et renvoit aux sections 
de l'index ou erreur 404 si section page inexistante
'''
    # session.clear()
    if var in sections:
        print('========')
        print('SESSION EN COURS :\n-------------------------------\n▪️ Session Flask : ',session)
        print('========')
        if not 'user_id' in session:
            status = 'out'
        
        else:
            status = 'in'
            
        return render_index(connect_status = status, section = var )

    else:
        return render_template('my404.html  ')

# ======================== CONNEXION API STRAVA =====================================


@app.route('/strava-connect-btn')
def strava_connect():
    if not 'user_id' in session:
        if app.debug:
            request_url = scon.request_authorization(redirect_uri = 'http://127.0.0.1:5000/strava_redirect')
        else:
            request_url = scon.request_authorization(redirect_uri = 'http://antoineberger.com/strava_redirect')
   
        return redirect(request_url)
 
    else:
        session.pop('user_id')
        status = 'out'
        return render_index(connect_status=status, section='gpxplorer')


@app.route('/strava_redirect')
def strava_redirect():
    status='in'

    # Extraire le code de l'URL
    code = request.args.get('code')
    new_token = scon.request_token(code).json()
    
    user_id = new_token['athlete']['id'] #pour l'instant mes users id sont = athletes_id
    session['user_id'] = user_id

    user = read_user(user_id)

    #==== DEUX OPTIONS : user déja dans DB ou user inconnu
    if user:   
    # OPTION 1 : user déja connu => REFRESH TOKEN SI BESOIN
        
        if user['expires_at'] < time.time():
            refreshed_token = scon.refresh_token(refresh_token=user['refresh_token'],athlete_id=user['athlete_id'], users_db_path=users_db_path)
            db.write_user(user['athlete_id'], refreshed_token, users_db_path)
    else:
    #OPTION 2 : user inconnu => AJOUT NEW USER DB
        new_dict = {'user_id':[user_id],
                            'athlete_id':[user_id],'access_token':[new_token['access_token']],'refresh_token':[new_token['refresh_token']],
                            'expires_at':[new_token['expires_at']],'firstname':[new_token['athlete']['firstname']],
                            'lastname':[new_token['athlete']['lastname']],'profile_medium':[new_token['athlete']['profile_medium']]}
        
        db.write_user(athlete_id=session['user_id'], new_token=new_dict, users_db_path=users_db_path)
    
    return render_index(connect_status=status, section='gpxplorer')
    
    
#================ SECTION GPXPLORER ====================


@app.route('/import-strava-routes', methods=['POST']) #importation des routes strava
def ma_route():
    if 'user_id' in session:
        access_token = read_user(session['user_id'])['access_token']
        athlete_id = read_user(session['user_id'])['athlete_id']
        df = sfun.get_athlete_routes(access_token, athlete_id)
        return jsonify(df)
    

@app.route('/load-dashboard', methods=['POST']) #lancement du dashboard
def submit_form():
    
    fileSource = request.form.get('fileSource')
    
    status = 'user_id' in session #renvoit vrai si l'utilisateur est connecté
    if status:
        df_routes = pd.read_csv(os.path.join(DATA_DIRECTORY, 'routes.csv'))
      
        
    #METEO
    if not request.form['date'] or not request.form['time'] : #si la météo n'est pas demandée
        time_string = None
    else:
        time_string = request.form['date']+' '+request.form['time']+':00'
        
    #FICHIERS : on vérifie la provenance parmis : import, strava et server
    if fileSource == 'import':
        #CAS 1 : ficher importé
        
        if ('gpxFile' in request.files) and request.files['gpxFile'].filename != '' : #CHECK FILE PRESENCE
            file = request.files['gpxFile']
            filename = file.filename
            if  not (file and filename.endswith('.gpx')): #CHECK FILE FORMAT
                return "Fichier GPX importé mais format ou extension non valide"
            else:
                if status: #CHECK SI USER CONNECTE POUR ENREGISTRER & OUVRIR LE FICHIER DANS LE BON DOSSIER
                    
                    temp_filepath = os.path.join(GPX_FILES_DIRECTORY_USER,filename)
                    file.save(temp_filepath)
                    file_id = db.generate_gpx_id(temp_filepath)
                    new_route = pd.DataFrame({'file_id': [file_id], 'route_name': [filename], 'user_id': [session['user_id']],'route_strava_id':[None], 'distance':[None],'elevation':[None],'source':[fileSource]})
                    new_df = pd.concat([df_routes, new_route], ignore_index=True)
                    new_df.to_csv(os.path.join(DATA_DIRECTORY, 'routes.csv'), index=False)
                    filepath = os.path.join(GPX_FILES_DIRECTORY_USER, f'{file_id}.gpx')
                else:
                    temp_filepath = os.path.join(GPX_FILES_DIRECTORY_TEMP,filename)
                    file.save(temp_filepath)
                    file_id = db.generate_gpx_id(temp_filepath)
                    filepath = os.path.join(GPX_FILES_DIRECTORY_TEMP, f'{file_id}.gpx')
                  
                
                if os.path.isfile(filepath):
                    os.remove(filepath)#suppression du fichier s'il existe déja
                os.rename(temp_filepath,filepath)  

                return render_dashboard(gpx_path=filepath,time_str=time_string,speed=int(request.form['speed'])/3.6,title=filename.split('.gpx')[0])
            
    elif('filename' in request.form) and request.form.get('filename') != '':
        filename = request.form.get('filename')
        file_id = request.form.get('fileId')
        #CAS 2 : route importé depuis STRAVA    
        if fileSource == 'strava':
            filepath = os.path.join(GPX_FILES_DIRECTORY_TEMP, f'{file_id}.gpx')
            access_token = read_user(user_id=session['user_id'])['access_token']
            sfun.get_route_GPX(access_token, route_id=file_id, GPX_DIRECTORY=GPX_FILES_DIRECTORY_TEMP) #save route en GPX
            if not os.path.isfile(filepath):
                return "Fichier sélectionné introuvable"            
            return render_dashboard(filepath,time_string,int(request.form['speed'])/3.6,filename)

        #CAS 3 : ficher selectionné sur le serveur
        elif fileSource == 'server':
            filepath = os.path.join(GPX_FILES_DIRECTORY_USER, f'{file_id}.gpx')

            if not os.path.isfile(filepath):
                filepath = os.path.join(GPX_FILES_DIRECTORY_USER, f'{file_id}.gpx')
                if not os.path.isfile(filepath):
                    return "Fichier sélectionné introuvable" 
            return render_dashboard(filepath,time_string,int(request.form['speed'])/3.6,filename)
    else:
        return "Aucun fichier importé ni sélectionné"

app.secret_key = 'ton_secret_unique_ici'
#cookies sécurisés dans navigateur
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

if __name__ == '__main__': # inutile en production car lancé via wsgi.py
    app.run(debug=True)





