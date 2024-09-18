from flask import Flask, jsonify
import gpxpy

app = Flask(__name__)

def lire_gpx(fichier_gpx):
    with open(fichier_gpx, 'r') as f:
        gpx = gpxpy.parse(f)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))
    print(coords)
    return coords

@app.route('/read-gpx', methods=['POST'])
def obtenir_coordonnees():
    fichier_gpx = 'G:\Mon Drive\Code\Websites\antoineberger\tools\routes\cdf.gpx'  # Remplace avec le chemin de ton fichier GPX
    coordonnees = lire_gpx(fichier_gpx)
    return jsonify(coordonnees)

if __name__ == '__main__':
    app.run(debug=True)
