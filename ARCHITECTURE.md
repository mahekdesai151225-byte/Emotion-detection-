# Architecture

## Overview

```text
┌─────────────────────────────┐
│        React Frontend       │
│      Vite + TypeScript      │
│                             │
│  Detect · Dataset · Audit   │
└──────────────┬──────────────┘
               │ HTTP / JSON
               ▼
┌─────────────────────────────┐
│        FastAPI Backend      │
│                             │
│  /predict                   │
│  /upload-dataset            │
│  /health                    │
│  /model-info                │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       ML Pipeline           │
│                             │
│ Text → TF-IDF → Logistic    │
│ Regression → Emotion        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Model Artifacts         │
│                             │
│ emotion_model.pkl           │
│ tfidf_vectorizer.pkl        │
│ label_map.pkl               │
└─────────────────────────────┘
```

## Frontend

`frontend/src/App.tsx` contains the application flow:

- **Detect Emotion** — sends text to `/predict`
- **Dataset** — sends CSV/XLS/XLSX files to `/upload-dataset`
- **Analytics** — presents the project's current model evaluation

`App.css` contains application-specific styling and `index.css` contains global tokens/reset styles.

The API base URL is configurable with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Backend

`backend/app.py` owns the HTTP API and loads the three model artifacts at startup.

Prediction flow:

```text
User text
   ↓
POST /predict
   ↓
TF-IDF vectorizer
   ↓
Logistic Regression
   ↓
emotion + confidence + class scores
   ↓
React result view
```

Dataset flow:

```text
CSV/XLS/XLSX
   ↓
POST /upload-dataset
   ↓
pandas
   ↓
rows + columns + missing values + 5-row preview
   ↓
React dataset view
```

## Training

`backend/train.py` is separate from the API.

```text
Dataset
  ↓
Validate columns
  ↓
Clean text and labels
  ↓
Keep labels 0–5
  ↓
Train/test split
  ↓
TF-IDF
  ↓
Balanced Logistic Regression
  ↓
Evaluation
  ↓
Save model artifacts
```

## Why there are no extra frontend libraries

The current application only needs:

- React for UI/state
- Vite for development/build
- TypeScript for type safety
- CSS for the visual system

Adding a UI framework, charting library, router, state-management package, or HTTP client would add maintenance without solving a current requirement.

## Build boundaries

### Development

```text
Browser → Vite dev server → FastAPI → model files
```

### Production

```text
Browser → deployed frontend → deployed FastAPI → model files
```

The frontend and backend remain separate so the backend can later be deployed or replaced without redesigning the UI.
