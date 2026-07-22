"""CLI entrypoint to train the toxicity classifier."""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import DevelopmentConfig
from app.services.ml_service import ToxicityModelService


def main():
    parser = argparse.ArgumentParser(description="Train cyberbullying / toxicity classifier")
    parser.add_argument(
        "--data",
        default="data/sample_dataset.csv",
        help="Path to Jigsaw-style CSV (comment_text + label columns)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.data):
        print(f"Dataset not found: {args.data}")
        sys.exit(1)

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
    metrics = service.train(args.data)

    print("Training complete.")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision_macro']:.4f}")
    print(f"  Recall:    {metrics['recall_macro']:.4f}")
    print(f"  F1-Score:  {metrics['f1_macro']:.4f}")
    print("  Artifacts: saved_models/ and reports/confusion_matrix.json")


if __name__ == "__main__":
    main()
