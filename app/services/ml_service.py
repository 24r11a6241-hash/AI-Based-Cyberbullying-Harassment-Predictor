"""Machine learning training, evaluation, and inference."""
import json
import os
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from app.utils.nlp_preprocessor import NLPPreprocessor
from app.utils.severity import build_prediction_summary


class ToxicityModelService:
    """Load or train scikit-learn toxicity classifier."""

    def __init__(self, app_config: dict | None = None):
        self.config = app_config or {}
        self.preprocessor = NLPPreprocessor()
        self.vectorizer: TfidfVectorizer | None = None
        self.model: LogisticRegression | None = None
        self.label_encoder: LabelEncoder | None = None
        self.categories = self.config.get(
            "CATEGORIES",
            [
                "Normal",
                "Offensive",
                "Toxic",
                "Cyberbullying",
                "Hate Speech",
                "Threat",
                "Identity Attack",
                "Sexual Harassment",
            ],
        )
        self.metrics: dict[str, Any] = {}

    @property
    def model_path(self) -> str:
        return self.config.get("MODEL_PATH", "saved_models/toxicity_classifier.joblib")

    @property
    def vectorizer_path(self) -> str:
        return self.config.get("VECTORIZER_PATH", "saved_models/tfidf_vectorizer.joblib")

    @property
    def label_encoder_path(self) -> str:
        return self.config.get("LABEL_ENCODER_PATH", "saved_models/label_encoder.joblib")

    @property
    def metrics_path(self) -> str:
        return self.config.get("METRICS_PATH", "saved_models/training_metrics.json")

    def is_loaded(self) -> bool:
        return self.model is not None and self.vectorizer is not None

    def load(self) -> bool:
        """Load persisted model artifacts."""
        if not all(
            os.path.isfile(p)
            for p in (self.model_path, self.vectorizer_path, self.label_encoder_path)
        ):
            return False
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.label_encoder = joblib.load(self.label_encoder_path)
        if os.path.isfile(self.metrics_path):
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        return True

    def save(self):
        """Persist model artifacts."""
        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.label_encoder, self.label_encoder_path)
        with open(self.metrics_path, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2)

    @staticmethod
    def jigsaw_row_to_label(row: pd.Series) -> str:
        """Map Jigsaw multi-label row to primary app category."""
        if row.get("toxic", 0) == 0 and row.get("severe_toxic", 0) == 0:
            return "Normal"
        if row.get("threat", 0) == 1:
            return "Threat"
        if row.get("identity_hate", 0) == 1:
            return "Identity Attack"
        if row.get("severe_toxic", 0) == 1:
            return "Hate Speech"
        if row.get("obscene", 0) == 1:
            return "Sexual Harassment"
        if row.get("insult", 0) == 1 and row.get("toxic", 0) == 1:
            return "Cyberbullying"
        if row.get("insult", 0) == 1:
            return "Offensive"
        if row.get("toxic", 0) == 1:
            return "Toxic"
        return "Normal"

    def load_jigsaw_dataset(self, csv_path: str) -> pd.DataFrame:
        """Load Jigsaw-style CSV and derive single primary label."""
        df = pd.read_csv(csv_path)
        text_col = "comment_text" if "comment_text" in df.columns else df.columns[0]
        label_cols = [
            c
            for c in ("toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate")
            if c in df.columns
        ]
        if not label_cols:
            if "label" in df.columns:
                df = df.rename(columns={text_col: "text"})
                df["primary_label"] = df["label"]
                return df[["text", "primary_label"]].dropna()
            raise ValueError("Dataset must include Jigsaw label columns or a label column.")

        df = df[[text_col] + label_cols].dropna(subset=[text_col])
        df = df.rename(columns={text_col: "text"})
        for c in label_cols:
            df.loc[:, c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        df["primary_label"] = df.apply(self.jigsaw_row_to_label, axis=1)
        return df[["text", "primary_label"]]

    def train(self, csv_path: str, test_size: float = 0.2, random_state: int = 42) -> dict:
        """Train TF-IDF + LogisticRegression on Jigsaw-style data."""
        df = self.load_jigsaw_dataset(csv_path)
        df.loc[:, "clean_text"] = df["text"].apply(lambda t: self.preprocessor.preprocess(str(t)))

        present_labels = [c for c in self.categories if c in set(df["primary_label"])]
        if not present_labels:
            raise ValueError("No valid labels found in dataset.")

        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(present_labels)
        y = self.label_encoder.transform(df["primary_label"])

        self.vectorizer = TfidfVectorizer(
            max_features=25000,
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=True,
        )
        X = self.vectorizer.fit_transform(df["clean_text"])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        self.model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        labels = list(self.label_encoder.classes_)
        label_ids = list(range(len(labels)))
        cm = confusion_matrix(y_test, y_pred, labels=label_ids)
        report = classification_report(
            y_test,
            y_pred,
            labels=label_ids,
            target_names=labels,
            output_dict=True,
            zero_division=0,
        )

        self.metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
            "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "labels": labels,
            "train_samples": int(X_train.shape[0]),
            "test_samples": int(X_test.shape[0]),
            "dataset_path": csv_path,
        }

        self.save()
        self._write_confusion_matrix_artifacts(cm, labels)
        return self.metrics

    def _write_confusion_matrix_artifacts(self, cm: np.ndarray, labels: list[str]):
        """Save confusion matrix as JSON; PNG if matplotlib is available."""
        os.makedirs("reports", exist_ok=True)
        payload = {"labels": labels, "matrix": cm.tolist()}
        with open("reports/confusion_matrix.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 8))
            plt.imshow(cm, interpolation="nearest", cmap="Blues")
            plt.title("Confusion Matrix — Toxicity Classifier")
            plt.colorbar()
            tick_marks = np.arange(len(labels))
            plt.xticks(tick_marks, labels, rotation=45, ha="right")
            plt.yticks(tick_marks, labels)
            plt.ylabel("True label")
            plt.xlabel("Predicted label")
            plt.tight_layout()
            plt.savefig("reports/confusion_matrix.png", dpi=120)
            plt.close()
        except Exception:
            pass

    def predict(self, text: str) -> dict[str, Any]:
        """Run inference on raw user text."""
        if not self.is_loaded():
            raise RuntimeError("Model is not loaded. Train or deploy model artifacts first.")

        clean = self.preprocessor.preprocess(text)
        X = self.vectorizer.transform([clean])
        proba = self.model.predict_proba(X)[0]
        classes = list(self.label_encoder.classes_)
        scores = {cls: float(proba[i]) for i, cls in enumerate(classes)}
        primary_idx = int(np.argmax(proba))
        primary_label = classes[primary_idx]
        confidence = float(proba[primary_idx])
        keywords = self.preprocessor.extract_toxic_keywords(text)
        summary = build_prediction_summary(primary_label, confidence, scores, keywords)
        summary["highlighted_text"] = self.preprocessor.highlight_toxic_keywords(text, keywords)
        summary["preprocessed_text"] = clean
        return summary
