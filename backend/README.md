# Emotion Detection API

FastAPI service for the Emotion Detection project.

## Responsibilities

- Load the trained TF-IDF vectorizer and Logistic Regression model.
- Predict one of six supported emotions.
- Return confidence and per-class scores.
- Inspect CSV/XLS/XLSX datasets.
- Expose a simple health check for the frontend.

## Start

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Model files

The API expects these files under `backend/model/`:

```text
emotion_model.pkl
tfidf_vectorizer.pkl
label_map.pkl
```

If they are missing, `/predict` and `/model-info` return a model-not-loaded response.

## Train

```bash
python train.py --data data/test.csv --text-column text --label-column label
```

The training script accepts CSV, XLSX, and XLS input.

## API

- `GET /` — service information
- `GET /health` — health check
- `POST /predict` — emotion prediction
- `POST /upload-dataset` — dataset inspection
- `GET /model-info` — loaded model information
