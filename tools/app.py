from flask import Flask, render_template, request
import scripts.startlist_script as ss
import scripts.map_script as ms
import os

app = Flask(__name__)

FILE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx_files')

@app.route('/tools/map/')
def route_map():
    try:
        # Récupérer la liste des fichiers dans le dossier
        file_list = os.listdir(FILE_DIRECTORY)
        app.logger.info(f"Fichiers trouvés: {file_list}")
        return render_template('map.html', files=file_list)
    except Exception as e:
            app.logger.error(f"Erreur lors de l'accès au dossier: {e}")
            return "Erreur lors de l'accès aux fichiers.", 500
        


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



@app.route('/upload_gpx', methods=['POST'])
def upload_gpx():
    render_template('map.html')
    if 'gpxFile' not in request.files:
        return "Pas de fichier sélectionné"
    
    file = request.files['gpxFile']

    if file.filename == '':
        return "Fichier non valide"

    if file and file.filename.endswith('.gpx'):
        files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx_files')
        filepath = os.path.join(files_dir, file.filename)
        file.save(filepath)
        
        print(filepath)
        return open_map(filepath)
       
    
    return "Format de fichier non supporté"

@app.route('/load_gpx/<filename>')
def load_gpx(filename):
    #chemin absolu du dossier
    files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpx_files')
    filepath = os.path.join(files_dir, filename)
    print(filepath)
    return open_map(filepath)

def open_map(filepath):
    
    coords = ms.read_gpx(filepath)
    ms.make_map(coords)
    return render_template('gpx_viewer.html')



# a delete en production car lancé via wsgi.py
if __name__ == '__main__':
    app.run(debug=True)


