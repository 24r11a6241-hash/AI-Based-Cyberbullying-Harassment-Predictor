"""Application configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cyberbullying_predictor")
    MODEL_PATH = os.getenv("MODEL_PATH", "saved_models/toxicity_classifier.joblib")
    VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "saved_models/tfidf_vectorizer.joblib")
    LABEL_ENCODER_PATH = os.getenv("LABEL_ENCODER_PATH", "saved_models/label_encoder.joblib")
    METRICS_PATH = os.getenv("METRICS_PATH", "saved_models/training_metrics.json")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@12345")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SAMPLE_DATA_PATH = os.getenv("SAMPLE_DATA_PATH", "data/sample_dataset.csv")
    TRAIN_DATA_PATH = os.getenv("TRAIN_DATA_PATH", "data/train.csv")

    CATEGORIES = [
        "Normal",
        "Offensive",
        "Toxic",
        "Cyberbullying",
        "Hate Speech",
        "Threat",
        "Identity Attack",
        "Sexual Harassment",
    ]

    JIGSAW_TO_APP_LABELS = {
        "toxic": "Toxic",
        "severe_toxic": "Toxic",
        "obscene": "Sexual Harassment",
        "threat": "Threat",
        "insult": "Offensive",
        "identity_hate": "Identity Attack",
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/cyberbullying_predictor_test")


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
