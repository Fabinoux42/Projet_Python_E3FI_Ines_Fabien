import zipfile
from flask import Flask, send_file
import importlib

name_missing_pack = {"flask", "zipfile"}  # Vérification des packages manquants
for name_pack in name_missing_pack:
    spec = importlib.util.find_spec(name_pack)
    if spec is None:
        print(f"Can't find {name_pack!r} package\n")

app = Flask(__name__)

@app.route('/')
def telecharger_fichiers():
    # Création d'un fichier ZIP temporaire
    with zipfile.ZipFile("fichiers.zip", "w") as zip:
        # Ajout des fichiers à télécharger au fichier ZIP
        zip.write("Fichiers_Statiques/idf.geojson")
        zip.write("Fichiers_Statiques/a-com2022.json")

    # Envoi du fichier ZIP
    return send_file("fichiers.zip", as_attachment=True, mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug = True)