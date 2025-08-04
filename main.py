from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import pymeshlab

app = FastAPI()

# Configuration CORS : autorise uniquement ton site WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.3dhack.ch"],  # Remplace par l'URL de ton site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Vérifie l’extension du fichier
    if not file.filename.lower().endswith((".stl", ".step", ".stp")):
        return {"error": "Fichier non supporté"}

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, file.filename)
        # Sauvegarde le fichier temporairement
        with open(filepath, "wb") as f:
            f.write(await file.read())

        ms = pymeshlab.MeshSet()
        try:
            ms.load_new_mesh(filepath)
        except Exception:
            return {"error": "Échec du chargement du fichier dans MeshLab"}

        volume = ms.get_geometric_measures().mesh_volume
        surface = ms.get_geometric_measures().surface_area

        # Calcul simple du coût
        prix_base = 10.0  # CHF de base
        prix_volume = volume * 0.12  # CHF/cm3
        prix_surface = surface * 0.05  # CHF/cm2
        total = round(prix_base + prix_volume + prix_surface, 2)

        return {
            "volume": round(volume, 2),
            "surface": round(surface, 2),
            "prix": total
        }
