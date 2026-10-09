# Emotion Detection

A small full-stack NLP application that detects one of six emotions from text:

**sadness · joy · love · anger · fear · surprise**

The project keeps the original concept intact:

- React + TypeScript + Vite frontend
- FastAPI backend
- TF-IDF text features
- Logistic Regression classifier
- CSV/XLS/XLSX dataset inspection
- Model analytics page
- Pre-trained model artifacts stored in `backend/model/`

## Project structure

```text
emotion-detection/
├── frontend/                 # React web application
├── backend/                  # FastAPI API + training script
├── ARCHITECTURE.md           # System and data-flow overview
├── README.md                 # This file
└── .gitignore
```

## Requirements

- Node.js 20+
- npm
- Python 3.10+
- A trained model in `backend/model/`

## Run the backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API runs at `http://127.0.0.1:8000`.

## Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

The frontend uses `http://127.0.0.1:8000` by default. To change it, create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Train the model

The training script expects a dataset with a text column and numeric emotion labels `0`–`5`.

Example:

```bash
cd backend
python train.py --data data/test.csv --text-column text --label-column label
```

Training produces:

```text
backend/model/
├── emotion_model.pkl
├── tfidf_vectorizer.pkl
└── label_map.pkl
```

## Frontend checks

```bash
cd frontend
npm run build
npm run lint
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/predict` | Predict emotion from text |
| POST | `/upload-dataset` | Inspect CSV/Excel dataset |
| GET | `/model-info` | Return loaded model information |

## Notes

The UI is intentionally dependency-light. No component library or charting package was added because the current requirements can be handled with React and CSS alone.

For deployment, add production environment configuration and serve the frontend from a production host. Do not commit virtual environments, `node_modules`, caches, or secrets.


## Final update

This ZIP includes the ambiguity-analysis update and visual result changes. See `START_HERE_MAC_WINDOWS.txt` for first-time and daily startup steps for macOS and Windows.
