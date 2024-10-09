import pandas as pd
import numpy as np
import os
import hashlib


#=========================== GENERER LES ID ==========================

def generate_gpx_id(file_path : os.path):
    # Lire le contenu du fichier GPX
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # Générer un hachage SHA-1 (ou MD5 si tu préfères)
    hash_object = hashlib.sha1(file_content)
    
    # Convertir le hachage en un entier (hexadécimal -> entier)
    hash_int = int(hash_object.hexdigest(), 16)
    
    # Limiter à 19 chiffres en utilisant le modulo
    unique_id = hash_int % (10**19)
    
    return unique_id

#============= WRITE IN USERS DB ==============

def write_user(athlete_id: int, new_token: dict, users_db_path : os.path):

    """
    Writes the token information to a .CSV : 
    - remplace les valeurs si le user existe
    - ajoute les valeurs si le user est inconnu
    """
    df_users = pd.read_csv(users_db_path)
    #===> UPDATE DU USER EXISTANT POUR REFRESH LE TOKEN
    if athlete_id in df_users['athlete_id'].values:#si athlète connu
        index = df_users.index[df_users['athlete_id'] == athlete_id].tolist()
        for key in new_token: #remplace ses tokens par les nouveaux
            df_users[key][index] = new_token[key]
        df_users.to_csv(users_db_path,index=False)

    #===> AJOUT D'UN NOUVEAU USER
    else:
        print('new_token',new_token)
        new_user = pd.DataFrame(new_token)
        new_df = pd.concat([df_users, new_user], ignore_index=True)
        new_df.to_csv(users_db_path,index=False)


#==============CREATION DES CSV VIDES =====================

def user_data(file_path : os.path):
    df = pd.DataFrame({ 
        "user_id":[], 
        "id":[], #strava
        "access_token":[],
        "refresh_token":[],
        "expires_at":[],
        "firstname":[],
        "lastname":[],
        "profile_medium":[]

    })
    print(df)
    df.to_csv(file_path,index=False)

# user_data()

def routes_data(file_path : os.path):
    df = pd.DataFrame({ 
        "file_id":[],
        "route_name":[],
        "user_id":[],
        "route_strava_id":[],
        "filepath":[],
        "distance":[],
        "elevation":[],
        "source":[] #strava, import, account
    })
    print(df)
    df.to_csv(file_path,index=False)

# routes_data()