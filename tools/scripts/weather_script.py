#PARAMETRES : t = "21 Nov 2019 13:00:00" et precision = nb de pts meteo souhaites
def meteo(lat,lon,points,nb_points,v_moy,time_sec,precision):
    
    
    #calcul du pas entre 2 infos météos (en nb de points)
    pas=int(nb_points/precision)
    #calcul des coordonnées des pts météo
    latitude=np.zeros(precision)
    longitude=np.zeros(precision)
    for i in range(0,precision):
        latitude[i]=lat[pas*i]
        longitude[i]=lon[pas*i]
        
    #Extraction des données et API et affectation aux variables
    wind_speed=np.zeros(precision)
    wind_dir=np.zeros(precision)
    heures=np.zeros(precision)
    temp=np.zeros(precision)
    temp_apparent=np.zeros(precision)
    precip=np.zeros(precision)
    precip_proba=np.zeros(precision)
    for i in range(0,precision):
        dt=calc_distance(latitude[i-1],latitude[i],longitude[i-1],longitude[i])/v_moy
        time_sec+=dt*3600
        
        base_url='https://api.darksky.net/forecast/f3bc3bd870812cc013666f2bfb75b45d/{},{},{}'
        url=base_url.format(latitude[i],longitude[i],int(time_sec))
        response=requests.get(url)
        json_data = json.loads(response.text)  
        
        wind_speed[i]=np.around(json_data["currently"]["windSpeed"]*3.6,2)
        wind_dir[i]=json_data["currently"]["windBearing"]
        temp[i]=(np.around(json_data["currently"]["temperature"],1)-32)*(5/9)
        temp_apparent[i]=(np.around(json_data["currently"]["apparentTemperature"],1)-32)*(5/9)
        precip[i]=json_data["currently"]["precipIntensity"]
        precip_proba[i]=json_data["currently"]["precipProbability"]
        heures[i]=time_sec
        
        print('Point',i+1,':','vitesse =',wind_speed[i],'km/h, direction =',wind_dir[i],'deg')
    return latitude,longitude,wind_speed,wind_dir,heures,precip,precip_proba,temp,temp_apparent
