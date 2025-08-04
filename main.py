import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

logging.basicConfig(level=logging.INFO)

print(f"pymeshlab version : {pymeshlab.__version__}")

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
    try:
        logging.info(f"Upload reçu : {file.filename}")

        if not file.filename.lower().endswith((".stl", ".step", ".stp")):
            return JSONResponse(status_code=400, content={"error": "Fichier non supporté"})

        with tempfile.TemporaryDirectory() as tmpdir:
            logging.info(f"Dossier temporaire créé : {tmpdir}")
            filepath = os.path.join(tmpdir, file.filename)
            logging.info(f"Chemin fichier temporaire : {filepath}")

            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)
                logging.info(f"Fichier écrit en local, taille : {len(content)} octets")

        return {"message": "Fichier reçu et enregistré temporairement"}
    except Exception as e:
        logging.error(f"Erreur serveur inattendue : {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Erreur serveur inattendue", "details": str(e)})
