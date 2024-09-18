from flask import Flask, render_template, request



#%%
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

def get_startlist(url):
    response = requests.get(url)
    soup = bs(response.content, "lxml") #données html brutes
    
    body = soup.find("section",{"class" : "startlist"})
    riders = body.find_all("li",{"class": "startlist-rider"})
    race_ID = soup.find('body', id='article-show')['data-article']
    race_name = soup.find('div', {"class" : 'main'}).h1.text
    
    
    r_urls=[]
    r_name=[]
    r_number=[]
    for r in riders:
        r_urls.append(r.a['href'])
        row_name = r.a.text
        row_name = row_name.replace('\n', '')
        row_name = re.sub(r"([A-Z])", r" \1", row_name).strip()
        r_name.append(row_name)
         #dossard
        r_number.append(r.find("em", {"class" : "startlist-number"}).text)
        
    df_startlist=pd.DataFrame({
        'name': r_name,
        'url' : r_urls,
        'number' : r_number
        })
    
    print('Partants scrapés avec succès pour : '+race_name)
    return  df_startlist, race_ID, race_name

#%%

app = Flask(__name__)

@app.route('/')
def index():
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
        # startlist, id, name = get_startlist(query)
        

        
        # result = '<br>'.join('-'+startlist['name'])
        # result = name +' ('+str(len(startlist['name']))+'):<br><br>' + result

        
        result = query

        print(result)
        return render_template('startlist.html', resultats = result)

        #return result
    except Exception as e:
        result= f"Erreur lors de la requête : {e}", 500
        return render_template('startlist.html', resultats = result)

    
if __name__ == '__main__':
    app.run(debug=True)


