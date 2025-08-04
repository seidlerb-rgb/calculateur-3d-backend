import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import pymeshlab

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS : adapte ton domaine ici
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.3dhack.ch"],  # Ou ["*"] pour tests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logging.info(f"Upload reçu : {file.filename}")

        # Vérification extension
        if not file.filename.lower().endswith((".stl", ".step", ".stp")):
            logging.warning("Fichier non supporté")
            return JSONResponse(status_code=400, content={"error": "Fichier non supporté"})

        with tempfile.TemporaryDirectory() as tmpdir:
            logging.info(f"Dossier temporaire créé : {tmpdir}")
            filepath = os.path.join(tmpdir, file.filename)
            logging.info(f"Chemin fichier temporaire : {filepath}")

            # Sauvegarde du fichier
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)
                logging.info(f"Fichier écrit en local, taille : {len(content)} octets")

            ms = pymeshlab.MeshSet()

            try:
                ms.load_new_mesh(filepath)
                logging.info("Fichier chargé dans MeshLab")
            except Exception as e:
                logging.error(f"Erreur MeshLab: {e}")
                return JSONResponse(status_code=422, content={"error": "Échec du chargement du fichier dans MeshLab", "details": str(e)})

            volume = ms.get_geometric_measures().mesh_volume
            surface = ms.get_geometric_measures().surface_area
            logging.info(f"Volume calculé : {volume}, Surface calculée : {surface}")

            prix_base = 10.0
            prix_volume = volume * 0.12
            prix_surface = surface * 0.05
            total = round(prix_base + prix_volume + prix_surface, 2)
            logging.info(f"Prix calculé : {total}")

            return {
                "volume": round(volume, 2),
                "surface": round(surface, 2),
                "prix": total
            }

    except Exception as e:
        logging.error(f"Erreur serveur inattendue : {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Erreur serveur inattendue", "details": str(e)})
