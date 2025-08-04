import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import pymeshlab

logging.basicConfig(level=logging.INFO)

print("pymeshlab est installé")  # simple test

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.3dhack.ch"],  # ou ["*"] pour tests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".stl", ".step", ".stp")):
        return {"error": "Fichier non supporté"}

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        ms = pymeshlab.MeshSet()
        try:
            ms.load_new_mesh(filepath)
        except Exception as e:
            return {"error": f"Échec du chargement du fichier dans MeshLab: {str(e)}"}

        volume = ms.get_geometric_measures().mesh_volume
        surface = ms.get_geometric_measures().surface_area

        prix_base = 10.0
        prix_volume = volume * 0.12
        prix_surface = surface * 0.05
        total = round(prix_base + prix_volume + prix_surface, 2)

        return {
            "volume": round(volume, 2),
            "surface": round(surface, 2),
            "prix": total
        }