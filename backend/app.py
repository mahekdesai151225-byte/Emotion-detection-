from pathlib import Path
import tempfile
import shutil

import joblib
import pandas as pd

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ambiguity import analyze_text


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

MODEL_PATH = MODEL_DIR / "emotion_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
LABEL_MAP_PATH = MODEL_DIR / "label_map.pkl"


# --------------------------------------------------
# App
# --------------------------------------------------

app = FastAPI(
    title="Emotion Detection API",
    description="NLP API for six-class emotion detection.",
    version="1.0.0",
)


# Allow the React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

model = None
vectorizer = None
label_map = None


def load_model():

    global model
    global vectorizer
    global label_map

    if not MODEL_PATH.exists():
        return False

    if not VECTORIZER_PATH.exists():
        return False

    if not LABEL_MAP_PATH.exists():
        return False

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    label_map = joblib.load(LABEL_MAP_PATH)

    return True


load_model()


# --------------------------------------------------
# Request models
# --------------------------------------------------

class PredictionRequest(BaseModel):
    text: str


# --------------------------------------------------
# Basic routes
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Emotion Detection API",
        "status": "running",
        "model_loaded": model is not None,
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


# --------------------------------------------------
# Prediction
# --------------------------------------------------

@app.post("/predict")
def predict(request: PredictionRequest):

    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Train the model first.",
        )

    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    # Convert text into TF-IDF features
    features = vectorizer.transform([text])

    # Predict emotion
    prediction = model.predict(features)[0]

    # Probability scores
    probabilities = model.predict_proba(features)[0]

    classes = model.classes_

    scores = {
        emotion: round(
            float(probability) * 100,
            2,
        )
        for emotion, probability in zip(
            classes,
            probabilities,
        )
    }

    confidence = max(probabilities) * 100
    analysis = analyze_text(text)

    return {
        "text": text,
        "emotion": prediction,
        "confidence": round(
            float(confidence),
            2,
        ),
        "scores": scores,
        "analysis": analysis,
    }


# --------------------------------------------------
# Dataset upload
# --------------------------------------------------

@app.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in {
        ".csv",
        ".xlsx",
        ".xls",
    }:

        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    # Temporary location
    temp_path = (
        Path(tempfile.gettempdir())
        / file.filename
    )

    try:

        with temp_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # Read dataset
        if extension == ".csv":

            df = pd.read_csv(
                temp_path
            )

        else:

            df = pd.read_excel(
                temp_path
            )

        if df.empty:

            raise HTTPException(
                status_code=400,
                detail="Dataset is empty.",
            )

        # Basic dataset information
        columns = list(df.columns)

        preview = (
            df.head(5)
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

        missing_values = (
            df.isnull()
            .sum()
            .to_dict()
        )

        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": columns,
            "preview": preview,
            "missing_values": missing_values,
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read dataset: {error}",
        )

    finally:

        temp_path.unlink(
            missing_ok=True
        )


# --------------------------------------------------
# Dataset information
# --------------------------------------------------

@app.get("/model-info")
def model_info():

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    return {
        "model": "Logistic Regression",
        "vectorizer": "TF-IDF",
        "emotions": list(
            model.classes_
        ),
        "features": (
            len(
                vectorizer.get_feature_names_out()
            )
        ),
    }

# Run directly with: python app.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
