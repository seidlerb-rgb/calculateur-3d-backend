from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import pymeshlab

app = FastAPI()

# Configuration CORS - adapte allow_origins à ton domaine en production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.3dhack.ch"],  # Ou ["*"] en test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith((".stl", ".step", ".stp")):
            return JSONResponse(status_code=400, content={"error": "Fichier non supporté"})

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, file.filename)
            with open(filepath, "wb") as f:
                f.write(await file.read())

            ms = pymeshlab.MeshSet()
            try:
                ms.load_new_mesh(filepath)
            except Exception as e:
                return JSONResponse(status_code=422, content={"error": "Échec du chargement du fichier dans MeshLab", "details": str(e)})

            volume = ms.get_geometric_measures().mesh_volume
            surface = ms.get_geometric_measures().surface_area

            prix_base = 10.0  # CHF de base
            prix_volume = volume * 0.12  # CHF/cm3
            prix_surface = surface * 0.05  # CHF/cm2
            total = round(prix_base + prix_volume + prix_surface, 2)

            return {
                "volume": round(volume, 2),
                "surface": round(surface, 2),
                "prix": total
            }

    except Exception as e:
        # Log dans la console (Render logs)
        print(f"Erreur serveur dans /upload : {e}")
        return JSONResponse(status_code=500, content={"error": "Erreur serveur inattendue", "details": str(e)})
