from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
from feature_engineering import add_features
from data_loader import load_inventory_data

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ouvrir à tous pour la démo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    try:
        content = await file.read()
        # Use your loader to ensure date parsing and column consistency
        df = load_inventory_data(io.BytesIO(content))
        df = add_features(df)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement du fichier : {str(e)}")
