"""Offline evaluation of saved model artifacts."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import DevelopmentConfig
from app.services.ml_service import ToxicityModelService


def main():
    parser = argparse.ArgumentParser(description="Evaluate saved toxicity model on a CSV")
    parser.add_argument("--data", required=True, help="Jigsaw-style CSV path")
    args = parser.parse_args()

    cfg = DevelopmentConfig()
    service = ToxicityModelService(
        {
            "MODEL_PATH": cfg.MODEL_PATH,
            "VECTORIZER_PATH": cfg.VECTORIZER_PATH,
            "LABEL_ENCODER_PATH": cfg.LABEL_ENCODER_PATH,
            "METRICS_PATH": cfg.METRICS_PATH,
            "CATEGORIES": cfg.CATEGORIES,
        }
    )
    if not service.load():
        print("Model artifacts not found. Train first.")
        sys.exit(1)

    metrics = service.train(args.data)
    print(json.dumps({k: metrics[k] for k in ("accuracy", "precision_macro", "recall_macro", "f1_macro")}, indent=2))


if __name__ == "__main__":
    main()
