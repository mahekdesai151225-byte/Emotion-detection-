import { useEffect, useState, type ChangeEvent } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type Page = "detect" | "dataset" | "analytics";

type Prediction = {
  text: string;
  emotion: string;
  confidence: number;
  scores: Record<string, number>;
  analysis?: {
    ambiguity_types: string[];
    ambiguity_level: string;
    sarcasm: boolean;
    negation: boolean;
    slang: boolean;
    intensity: boolean;
    context_dependent: boolean;
    cues: string[];
    details: {
      slang_terms: string[];
      negation_terms: string[];
      intensity_terms: string[];
      exclamation_marks: number;
      question_marks: number;
      emphasized_words: string[];
    };
  };
};

type Dataset = {
  filename: string;
  rows: number;
  columns: string[];
  preview: Record<string, unknown>[];
  missing_values: Record<string, number>;
};

const emotions = [
  "sadness",
  "joy",
  "love",
  "anger",
  "fear",
  "surprise",
];

const icons: Record<string, string> = {
  sadness: "😢",
  joy: "😊",
  love: "❤️",
  anger: "😠",
  fear: "😨",
  surprise: "😮",
};

function App() {
  const [page, setPage] = useState<Page>("detect");

  const [text, setText] = useState("");
  const [prediction, setPrediction] =
    useState<Prediction | null>(null);

  const [dataset, setDataset] =
    useState<Dataset | null>(null);

  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    void checkApi();
  }, []);

  async function checkApi() {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (!response.ok) throw new Error();
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
  }

  async function predict() {
    if (!text.trim()) {
      setError("Please enter some text first.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Prediction failed."
        );
      }

      setPrediction(data);
      setApiOnline(true);
    } catch (err) {
      setApiOnline(false);
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to the API."
      );
    } finally {
      setLoading(false);
    }
  }

  async function uploadDataset(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;
    event.target.value = "";

    setError("");
    setDataset(null);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/upload-dataset`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Dataset upload failed."
        );
      }

      setDataset(data);
      setApiOnline(true);
    } catch (err) {
      setApiOnline(false);
      setError(
        err instanceof Error
          ? err.message
          : "Dataset upload failed."
      );
    } finally {
      setUploading(false);
    }
  }

  const title = {
    detect: "Emotion Detection",
    dataset: "Dataset Manager",
    analytics: "Model Analytics",
  }[page];

  const description = {
    detect:
      "Analyze text using the trained NLP model.",
    dataset:
      "Upload and inspect your emotion dataset.",
    analytics:
      "Audit model performance across emotion classes.",
  }[page];

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            🧠
          </div>

          <div>
            <h1>EmotionAI</h1>
            <span>NLP ANALYZER</span>
          </div>
        </div>

        <nav>

          <button
            className={
              page === "detect"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("detect")}
          >
            <span>🔍</span>
            Detect Emotion
          </button>

          <button
            className={
              page === "dataset"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("dataset")}
          >
            <span>📁</span>
            Dataset
          </button>

          <button
            className={
              page === "analytics"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("analytics")}
          >
            <span>📊</span>
            Analytics
          </button>

        </nav>

        <div className="sidebar-bottom">
          <div className="model-status">

            <span className="status-dot" />

            <div>
              <strong>Model Online</strong>

              <small>
                TF-IDF + Logistic Regression
              </small>
            </div>

          </div>
        </div>

      </aside>


      {/* MAIN */}

      <main className="main">

        <header className="topbar">

          <div>
            <span className="eyebrow">
              NATURAL LANGUAGE PROCESSING
            </span>

            <h2>{title}</h2>

            <p className="topbar-description">
              {description}
            </p>
          </div>

          <div className={`api-status ${apiOnline ? "online" : "offline"}`}>
            <span className="status-dot" />
            {apiOnline ? "API Connected" : "API Offline"}
          </div>

        </header>


        {error && (
          <div className="error-box">
            ⚠️ {error}
          </div>
        )}


        {/* =========================
            DETECT
        ========================= */}

        {page === "detect" && (
          <section className="page">

            <div className="hero">

              <div>

                <span className="eyebrow">
                  SIX-CLASS EMOTION CLASSIFICATION
                </span>

                <h3>
                  Understand the emotion
                  <br />
                  behind the text.
                </h3>

                <p>
                  Enter a sentence and let the
                  trained NLP model analyze its
                  emotional meaning.
                </p>

              </div>

              <div className="hero-orb">
                🧠
              </div>

            </div>


            <div className="detect-card">

              <div className="card-header">

                <div>
                  <h3>Analyze Text</h3>

                  <p>
                    Enter any sentence or message
                    below.
                  </p>
                </div>

                <span className="model-badge">
                  TF-IDF + LR
                </span>

              </div>


              <textarea
                value={text}
                onChange={(event) =>
                  setText(event.target.value)
                }
                placeholder="Example: I am so happy and excited about my new achievement!"
              />


              <div className="input-footer">

                <span>
                  {text.length} characters
                </span>

                <button
                  className="primary-button"
                  onClick={predict}
                  disabled={loading}
                >
                  {loading
                    ? "Analyzing..."
                    : "Detect Emotion →"}
                </button>

              </div>

            </div>


            {prediction && (
              <section className="results-pop" aria-live="polite">
                <div className="result-pop-main">
                  <div className="result-pop-glow" />
                  <div className="result-pop-icon">
                    {icons[prediction.emotion] || "🧠"}
                  </div>
                  <span className="result-label">DETECTED EMOTION</span>
                  <h3>{prediction.emotion}</h3>
                  <p className="result-pop-subtitle">The model reads the strongest emotional signal as</p>
                  <div className="confidence-pop">
                    <span>Confidence</span>
                    <strong>{prediction.confidence}%</strong>
                  </div>
                  <div className="confidence-pop-track">
                    <div style={{ width: `${prediction.confidence}%` }} />
                  </div>
                </div>

                <div className="statement-pop">
                  <div className="statement-heading">
                    <div>
                      <span className="result-label">WHAT DOES THE STATEMENT SAY?</span>
                      <h4>Interpretation</h4>
                    </div>
                    <span className={`ambiguity-pill ${prediction.analysis?.ambiguity_level?.toLowerCase() || "low"}`}>
                      {prediction.analysis?.ambiguity_level || "Low"} ambiguity
                    </span>
                  </div>

                  <div className="statement-text">“{prediction.text}”</div>

                  <div className="analysis-table">
                    <div><span>Emotion</span><strong>{icons[prediction.emotion]} {prediction.emotion}</strong></div>
                    <div><span>Confidence</span><strong>{prediction.confidence}%</strong></div>
                    <div><span>Sarcasm</span><strong>{prediction.analysis?.sarcasm ? "Detected" : "Not detected"}</strong></div>
                    <div><span>Negation</span><strong>{prediction.analysis?.negation ? "Detected" : "Not detected"}</strong></div>
                    <div><span>Slang</span><strong>{prediction.analysis?.slang ? "Detected" : "Not detected"}</strong></div>
                    <div><span>Intensity</span><strong>{prediction.analysis?.intensity ? "Detected" : "Normal"}</strong></div>
                    <div><span>Context dependence</span><strong>{prediction.analysis?.context_dependent ? "Likely" : "Low"}</strong></div>
                    <div><span>Ambiguity types</span><strong>{prediction.analysis?.ambiguity_types?.length ? prediction.analysis.ambiguity_types.join(" · ") : "None detected"}</strong></div>
                  </div>

                  {prediction.analysis?.cues?.length ? (
                    <div className="cue-row">
                      {prediction.analysis.cues.map((cue) => <span key={cue}>{cue}</span>)}
                    </div>
                  ) : (
                    <div className="clear-reading">✓ No strong ambiguity, sarcasm, slang, or negation cues detected.</div>
                  )}
                </div>

                <div className="distribution-pop">
                  <div className="statement-heading">
                    <div>
                      <span className="result-label">EMOTION DISTRIBUTION</span>
                      <h4>Model scores</h4>
                    </div>
                  </div>
                  <div className="scores">
                    {emotions.map((emotion) => {
                      const score = prediction.scores[emotion] ?? 0;
                      return (
                        <div className={`score-row ${emotion === prediction.emotion ? "top-score" : ""}`} key={emotion}>
                          <div className="score-name">{icons[emotion]} {emotion}</div>
                          <div className="score-track"><div className="score-fill" style={{ width: `${score}%` }} /></div>
                          <strong>{score}%</strong>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </section>
            )}

          </section>
        )}


        {/* =========================
            DATASET
        ========================= */}

        {page === "dataset" && (

          <section className="page">

            <div className="section-heading">

              <span className="eyebrow">
                DATA MANAGEMENT
              </span>

              <h3>
                Upload your dataset
              </h3>

              <p>
                Import CSV or Excel files and
                inspect the data before training.
              </p>

            </div>


            <div className="upload-card">

              <div className="upload-icon">
                📁
              </div>

              <h3>
                Upload Dataset
              </h3>

              <p>
                CSV, XLSX and XLS supported
              </p>

              <label className="upload-button">

                {uploading
                  ? "Uploading..."
                  : "Choose Dataset"}

                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  hidden
                  onChange={uploadDataset}
                />

              </label>

            </div>


            {dataset && (

              <div className="dataset-result">

                <div className="dataset-header">

                  <div>

                    <span className="result-label">
                      DATASET LOADED
                    </span>

                    <h3>
                      {dataset.filename}
                    </h3>

                  </div>

                  <span className="success-badge">
                    ✓ Valid
                  </span>

                </div>


                <div className="dataset-stats">

                  <div>
                    <strong>
                      {dataset.rows.toLocaleString()}
                    </strong>
                    <span>Rows</span>
                  </div>

                  <div>
                    <strong>
                      {dataset.columns.length}
                    </strong>
                    <span>Columns</span>
                  </div>

                  <div>

                    <strong>
                      {Object.values(
                        dataset.missing_values
                      ).reduce(
                        (sum, value) =>
                          sum + value,
                        0
                      )}
                    </strong>

                    <span>Missing Values</span>

                  </div>

                </div>


                <h4>
                  Columns
                </h4>

                <div className="column-list">

                  {dataset.columns.map(
                    (column) => (
                      <span key={column}>
                        {column}
                      </span>
                    )
                  )}

                </div>


                <h4>
                  Dataset Preview
                </h4>

                <div className="table-wrapper">

                  <table>

                    <thead>
                      <tr>

                        {dataset.columns.map(
                          (column) => (
                            <th key={column}>
                              {column}
                            </th>
                          )
                        )}

                      </tr>
                    </thead>

                    <tbody>

                      {dataset.preview.map(
                        (row, index) => (

                          <tr key={index}>

                            {dataset.columns.map(
                              (column) => (
                                <td key={column}>
                                  {String(
                                    row[column] ?? ""
                                  )}
                                </td>
                              )
                            )}

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              </div>

            )}

          </section>
        )}


        {/* =========================
            ANALYTICS
        ========================= */}

        {page === "analytics" && (

          <section className="page">

            <div className="section-heading">

              <span className="eyebrow">
                MODEL EVALUATION
              </span>

              <h3>
                Performance & Class Audit
              </h3>

              <p>
                Review accuracy and performance
                across all six emotion classes.
              </p>

            </div>


            <div className="metric-grid">

              <div className="metric-card">
                <span>ACCURACY</span>
                <strong>60.50%</strong>
                <small>400 test samples</small>
              </div>

              <div className="metric-card">
                <span>MACRO PRECISION</span>
                <strong>57%</strong>
                <small>Six emotion classes</small>
              </div>

              <div className="metric-card">
                <span>MACRO RECALL</span>
                <strong>54%</strong>
                <small>Six emotion classes</small>
              </div>

              <div className="metric-card">
                <span>MACRO F1</span>
                <strong>54%</strong>
                <small>Six emotion classes</small>
              </div>

            </div>


            <div className="audit-card">

              <div className="card-header">

                <div>

                  <h3>
                    Class Performance Audit
                  </h3>

                  <p>
                    Precision, recall and F1-score
                    for each emotion.
                  </p>

                </div>

              </div>


              <div className="audit-table">

                <div className="audit-row audit-head">
                  <span>Emotion</span>
                  <span>Precision</span>
                  <span>Recall</span>
                  <span>F1</span>
                </div>

                <div className="audit-row">
                  <span>😢 Sadness</span>
                  <span>69%</span>
                  <span>61%</span>
                  <span>65%</span>
                </div>

                <div className="audit-row">
                  <span>😊 Joy</span>
                  <span>66%</span>
                  <span>70%</span>
                  <span>68%</span>
                </div>

                <div className="audit-row">
                  <span>❤️ Love</span>
                  <span>33%</span>
                  <span>41%</span>
                  <span>37%</span>
                </div>

                <div className="audit-row">
                  <span>😠 Anger</span>
                  <span>54%</span>
                  <span>60%</span>
                  <span>57%</span>
                </div>

                <div className="audit-row">
                  <span>😨 Fear</span>
                  <span>55%</span>
                  <span>51%</span>
                  <span>53%</span>
                </div>

                <div className="audit-row">
                  <span>😮 Surprise</span>
                  <span>62%</span>
                  <span>38%</span>
                  <span>48%</span>
                </div>

              </div>

            </div>


            <div className="audit-card">

              <div className="card-header">

                <div>

                  <h3>
                    Model Audit
                  </h3>

                  <p>
                    The current model uses TF-IDF
                    features with Logistic Regression.
                  </p>

                </div>

              </div>

              <div className="dataset-stats">

                <div>
                  <strong>4,550</strong>
                  <span>TF-IDF Features</span>
                </div>

                <div>
                  <strong>2,000</strong>
                  <span>Dataset Samples</span>
                </div>

                <div>
                  <strong>6</strong>
                  <span>Emotion Classes</span>
                </div>

              </div>

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;