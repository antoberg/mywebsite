# ====================== Importations ======================

from flask import Flask, render_template, request, jsonify, redirect, session
import numpy as np
import scripts.startlist_script as ss
import scripts.map_script as ms
from scripts.strava import api_connection as scon
from scripts.strava import functions as sfun
import os
from datetime import datetime, timedelta
import time
import os   

# ================== Constantes et Variables =================

## Directories and files
FILE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

GPX_FILES_DIRECTORY = os.path.join(FILE_DIRECTORY, 'gpx_files')
GPX_FILES_DIRECTORY_RECENT =  os.path.join(GPX_FILES_DIRECTORY, 'recent')
GPX_FILES_DIRECTORY_RACES =  os.path.join(GPX_FILES_DIRECTORY, 'races')
GPX_FILES_DIRECTORY_STRAVA =  os.path.join(GPX_FILES_DIRECTORY, 'strava')
GPX_FILES_DIRECTORY_IMPORTS = os.path.join(GPX_FILES_DIRECTORY, 'imports')

MAPS_FILES_DIRECTORY = os.path.join(FILE_DIRECTORY, 'folium_maps')

TOKENS_FILES_DIRECTORY = os.path.join(FILE_DIRECTORY, 'tokens')
tokenPath = os.path.join(TOKENS_FILES_DIRECTORY, 'strava_token.json')

recent_files = os.listdir(os.path.join(GPX_FILES_DIRECTORY, 'recent'))
race_files = os.listdir(os.path.join(GPX_FILES_DIRECTORY, 'races'))

## variables
current_time = int(time.time())
strava_connect_status0 = "No connected athlete"
strava_connect_status1 = 'Connected as {}'
connect_btn0 = 'Connect'
connect_btn1 = 'Disconnect'

# ====================== Fonctions ===========================

def open_map(filepath, time_str,speed,name,weather_request):
    ts, df_route, df_weather = ms.make_map(filepath,time_str,speed,DIRECTORY=MAPS_FILES_DIRECTORY)
   
    #calculs sur df
    total_dist = round(max(df_route['distance'])/1000)
    asc = round(sum([x for x in df_route['dz'] if x>0]))
    desc = round(sum([x for x in df_route['dz'] if x<0]))
    dist_list = [round(x/1000) for x in df_route['distance']]
    dist_weather_list = [round(x/1000) for x in df_weather['distance']]
    ele_list = [round(x) for x in df_route['elevation']]
    wind_data = [round(x*3.6) for x in df_weather['wind_speed']]
    
    map_filepath = os.path.join(MAPS_FILES_DIRECTORY, f'map_{ts}.html')
    map_filepath = f'map_dashboard_files/folium_maps/map_{ts}.html'
    return render_template('map_dashboard.html', time = current_time, map_url=map_filepath, 
                           title= name, dist=total_dist, asc=asc,desc=desc, x_data = dist_list, y_data = ele_list,
                           weather_request=weather_request,#=active si la météo est requise par le user
                           x_weather_data = dist_weather_list, wind_data=wind_data,temp_data = list(df_weather['temp']), rain_data = list(df_weather['rain']))

# ====================== Routes Flask ===========================
app = Flask(__name__)


@app.route('/')
def index():
    # session.clear()
    
    if not 'athlete_id' in session:
        strava_connect_status = strava_connect_status0
        connect_btn = connect_btn0
        


    else:
        
        scon.check_token_validity(session['athlete_id'], tokenPath)##refresh le token si besoin
        strava_connect_status = strava_connect_status1.format(session['username'])
        connect_btn = connect_btn1
        
  
    return render_template('index.html', time = current_time, 
                           race_files=race_files,recent_files=recent_files,
                           strava_connect_status=strava_connect_status,
                           connect_btn = connect_btn)

# ======================== début connexion strava =====================================
#   
@app.route('/strava-connect-btn')
def strava_connect():
    if not 'athlete_id' in session:
        if app.debug:
            request_url = scon.request_authorization(redirect_uri = 'http://127.0.0.1:5000/strava_redirect')
        else:
            request_url = scon.request_authorization(redirect_uri = 'http://antoineberger.com/strava_redirect')
        return redirect(request_url)
 
    else:

        athId = session['athlete_id']
        session.pop('athlete_id', athId)

        strava_connect_status = strava_connect_status0
        connect_btn = connect_btn0
        

        return render_template('index.html', time = current_time, 
                            race_files=race_files,recent_files=recent_files,
                            strava_connect_status=strava_connect_status,
                            connect_btn = connect_btn)

@app.route('/strava_redirect')
def strava_redirect():
    # Extraire le code de l'URL
    code = request.args.get('code')
    token_response = scon.request_token(code).json()
    
    session['athlete_id'] = token_response['athlete']['id']
    session['username'] = token_response['athlete']['username']
    scon.write_token(session['athlete_id'], token_response, tokenPath)

    strava_connect_status = strava_connect_status1.format(session['username'])
    connect_btn = connect_btn1
    

    scon.check_token_validity(session['athlete_id'], tokenPath)##refresh le token si besoin
    
    return render_template('index.html', time = current_time, 
                        race_files=race_files,recent_files=recent_files,
                        strava_connect_status=strava_connect_status,
                        connect_btn = connect_btn)

    
#================ fin connexion strava ====================

@app.route('/import-strava-routes', methods=['POST'])
def ma_route():
    if 'athlete_id' in session:
        access_token = scon.get_athlete_token(session['athlete_id'], tokenPath)['access_token']
        df = sfun.get_athlete_routes(access_token,session['athlete_id'])
        return jsonify(df)
    

@app.route('/submit' , methods=['POST'])
def submit_form():
    fileSource = request.form.get('fileSource')
    weather_request = 'hidden' #par défaut
    
    if not request.form['date']:
        time_string='nan'
    elif not request.form['time']:
        time_string = 'nan'
    else:
        time_string = request.form['date']+' '+request.form['time']+':00'
        weather_request = ''

    if fileSource == 'import':
        if ('gpxFile' in request.files) and request.files['gpxFile'].filename != '' :
            file = request.files['gpxFile']
            if  not (file and file.filename.endswith('.gpx')):
                return "Fichier GPX importé mais format ou extension non valide"
            else:
                filepath = os.path.join(GPX_FILES_DIRECTORY_IMPORTS, file.filename)
                file.save(filepath)
                name = file.filename.split('.gpx')[0] 
                return open_map(filepath,time_string,int(request.form['speed'])/3.6,name,weather_request)
            
    elif('filename' in request.form) and request.form.get('filename') != '':
        
        if fileSource == 'strava':
        
            filename = request.form.get('filename')
            route_id = request.form.get('fileId')
            print('===================================')
            print("Loading :",filename,'id :',route_id)
            print('===================================')
            
            access_token = scon.get_athlete_token(session['athlete_id'], tokenPath)['access_token']
            sfun.get_route_GPX(access_token, route_id=route_id, GPX_DIRECTORY=GPX_FILES_DIRECTORY_STRAVA) #save route en GPX

            name = f'route_{route_id}.gpx'
            filepath = os.path.join(GPX_FILES_DIRECTORY_STRAVA, name)
            if not os.path.isfile(filepath):
                return "Fichier sélectionné introuvable" 

            return open_map(filepath,time_string,int(request.form['speed'])/3.6,filename, weather_request)
    
        elif fileSource == 'server':
            
            filename = request.form.get('filename')
            filepath = os.path.join(GPX_FILES_DIRECTORY_RECENT, filename)
            if not os.path.isfile(filepath):
                filepath = os.path.join(GPX_FILES_DIRECTORY_RACES, filename)
                if not os.path.isfile(filepath):
                    return "Fichier sélectionné introuvable" 
                
            name = filename.split('.gpx')[0]
            return open_map(filepath,time_string,int(request.form['speed'])/3.6,name, weather_request)
        
        else:
            return 'Pas de source'
    else:
        return "Aucun fichier importé ni sélectionné"

app.secret_key = 'ton_secret_unique_ici'
#cookies sécurisés dans navigateur
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

if __name__ == '__main__': # inutile en production car lancé via wsgi.py
    app.run(debug=True)


