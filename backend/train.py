from pathlib import Path
import argparse

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


# Dataset label -> emotion name
LABEL_MAP = {
    0: "sadness",
    1: "joy",
    2: "love",
    3: "anger",
    4: "fear",
    5: "surprise",
}

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

MODEL_DIR.mkdir(exist_ok=True)


def load_dataset(path):
    file = Path(path)

    if not file.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file}"
        )

    if file.suffix.lower() == ".csv":
        df = pd.read_csv(file)

    elif file.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(file)

    else:
        raise ValueError(
            "Only CSV and XLSX files are supported."
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    print(f"\nDataset loaded: {len(df):,} rows")
    print("Columns:", list(df.columns))

    return df


def prepare_data(df, text_column, label_column):

    if text_column not in df.columns:
        raise ValueError(
            f"Text column '{text_column}' not found."
        )

    if label_column not in df.columns:
        raise ValueError(
            f"Label column '{label_column}' not found."
        )

    data = df[[text_column, label_column]].copy()

    # Clean text
    data[text_column] = (
        data[text_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Convert labels to numbers
    data[label_column] = pd.to_numeric(
        data[label_column],
        errors="coerce"
    )

    # Remove invalid rows
    data = data.dropna(
        subset=[text_column, label_column]
    )

    # Convert labels to integers
    data[label_column] = data[label_column].astype(int)

    # Keep only the six supported emotions
    data = data[
        data[label_column].isin(LABEL_MAP.keys())
    ]

    # Remove empty text
    data = data[data[text_column] != ""]

    # Convert numeric labels to emotion names
    data["emotion"] = data[label_column].map(
        LABEL_MAP
    )

    print(
        f"\nRows after cleaning: {len(data):,}"
    )

    print("\nEmotion distribution:")

    distribution = (
        data["emotion"]
        .value_counts()
        .reindex(LABEL_MAP.values())
        .fillna(0)
        .astype(int)
    )

    print(distribution)

    return data[text_column], data["emotion"]


def train_model(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(
        f"\nTraining samples: {len(X_train):,}"
    )

    print(
        f"Testing samples: {len(X_test):,}"
    )

    # Convert text into TF-IDF numerical features
    vectorizer = TfidfVectorizer(
        lowercase=True,
        max_features=50_000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )

    X_test_tfidf = vectorizer.transform(
        X_test
    )

    print(
        f"\nTF-IDF features: "
        f"{X_train_tfidf.shape[1]:,}"
    )

    # Logistic Regression with class balancing
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    )

    print("\nTraining balanced model...")

    model.fit(
        X_train_tfidf,
        y_train,
    )

    # Predictions
    predictions = model.predict(
        X_test_tfidf
    )

    # Accuracy
    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    # Classification report
    report = classification_report(
        y_test,
        predictions,
        labels=list(LABEL_MAP.values()),
        zero_division=0,
    )

    # Confusion matrix
    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=list(LABEL_MAP.values()),
    )

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification Report:")

    print(report)

    print("\nConfusion Matrix:")

    print(matrix)

    print("\n" + "=" * 60)
    print("CLASS-WISE PERFORMANCE AUDIT")
    print("=" * 60)

    report_dict = classification_report(
        y_test,
        predictions,
        labels=list(LABEL_MAP.values()),
        output_dict=True,
        zero_division=0,
    )

    for emotion in LABEL_MAP.values():

        metrics = report_dict[emotion]

        print(
            f"\n{emotion.upper()}"
        )

        print(
            f"  Precision: {metrics['precision']:.2f}"
        )

        print(
            f"  Recall:    {metrics['recall']:.2f}"
        )

        print(
            f"  F1-score:  {metrics['f1-score']:.2f}"
        )

        print(
            f"  Samples:   {int(metrics['support'])}"
        )

    print("\n" + "=" * 60)

    return model, vectorizer


def save_model(model, vectorizer):

    model_path = (
        MODEL_DIR / "emotion_model.pkl"
    )

    vectorizer_path = (
        MODEL_DIR / "tfidf_vectorizer.pkl"
    )

    label_map_path = (
        MODEL_DIR / "label_map.pkl"
    )

    joblib.dump(
        model,
        model_path,
    )

    joblib.dump(
        vectorizer,
        vectorizer_path,
    )

    joblib.dump(
        LABEL_MAP,
        label_map_path,
    )

    print("\n" + "=" * 60)
    print("MODEL SAVED")
    print("=" * 60)

    print(
        f"\nModel:      {model_path}"
    )

    print(
        f"Vectorizer: {vectorizer_path}"
    )

    print(
        f"Label map:  {label_map_path}"
    )


def main():

    parser = argparse.ArgumentParser(
        description="Train Emotion Detection NLP model."
    )

    parser.add_argument(
        "--data",
        required=True,
        help="Path to CSV or XLSX dataset.",
    )

    parser.add_argument(
        "--text-column",
        required=True,
        help="Column containing text.",
    )

    parser.add_argument(
        "--label-column",
        required=True,
        help="Column containing emotion labels.",
    )

    args = parser.parse_args()

    # Load dataset
    df = load_dataset(
        args.data
    )

    # Prepare dataset
    X, y = prepare_data(
        df,
        args.text_column,
        args.label_column,
    )

    # Train model
    model, vectorizer = train_model(
        X,
        y,
    )

    # Save model
    save_model(
        model,
        vectorizer,
    )

    print(
        "\nPhase 1 completed successfully!"
    )


if __name__ == "__main__":
    main()