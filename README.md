# CyberGuard AI — Cyberbullying & Harassment Predictor

Production-ready Flask web application that detects **Normal**, **Offensive**, **Toxic**, **Cyberbullying**, **Hate Speech**, **Threat**, **Identity Attack**, and **Sexual Harassment** in user text using NLP preprocessing and a scikit-learn classifier trained on **Jigsaw Toxic Comment**-style data.

## Features

- **NLP pipeline**: lowercase, URL removal, punctuation removal, tokenization, stopword removal, lemmatization
- **ML**: TF-IDF + balanced Logistic Regression (multinomial)
- **Evaluation**: Accuracy, Precision, Recall, F1-Score, confusion matrix plot
- **Predictions**: confidence %, severity (Low/Medium/High/Critical), sentiment, toxic keyword highlighting
- **Auth**: registration, login, JWT, bcrypt password hashing
- **MongoDB**: users, prediction history, admin analytics
- **Admin**: dashboard, retraining API, model status
- **REST API** with validation, logging, and error handlers
- **UI**: Bootstrap responsive pages (Home, Login, Register, Dashboard, Predict, History, Admin, Reports)
- **Deploy**: Dockerfile, docker-compose, Kubernetes manifests

> **Note on BERT/RoBERTa**: This repo ships a lightweight, CPU-friendly scikit-learn stack suitable for demos and production without GPU. You can swap `ToxicityModelService` with a Hugging Face transformer wrapper using the same API surface.

## Project Structure

```
cyberbullying-predictor/
├── app/                 # Flask app (routes, services, utils, templates, static)
├── ml/                  # Training CLI
├── database/            # MongoDB index initialization
├── data/                # Sample Jigsaw-style CSV + place full train.csv here
├── saved_models/        # joblib artifacts
├── reports/             # confusion matrix & metrics outputs
├── tests/
├── kubernetes/
├── Dockerfile
├── docker-compose.yml
└── run.py
```

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- MongoDB 6+ running locally

### Installation

```bash
cd ~/Projects/cyberbullying-predictor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python database/init_db.py
python -m ml.train --data data/sample_dataset.csv
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

**Default admin** (from `.env`): `admin@example.com` / `Admin@12345`

### Full Jigsaw Dataset

1. Download [Jigsaw Toxic Comment Classification Challenge](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) `train.csv`
2. Save as `data/train.csv`
3. Train: `python -m ml.train --data data/train.csv`
4. Or retrain from **Admin Panel** → **Retrain Model**

## Docker

```bash
docker compose up --build
```

App: [http://localhost:5000](http://localhost:5000)

## Kubernetes

```bash
docker build -t cyberguard-ai:latest .
kubectl apply -f kubernetes/deployment.yaml
```

Create secrets before deploy:

```bash
kubectl create secret generic cyberguard-secrets \
  --from-literal=SECRET_KEY='your-secret' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret'
```

## API Documentation

See [docs/API.md](docs/API.md)

## Tests

```bash
pytest tests/ -q
```

## Security Notes

- Change `SECRET_KEY`, `JWT_SECRET_KEY`, and admin credentials in production
- Use HTTPS and secure MongoDB credentials
- Do not commit `.env` or model secrets

## License

MIT (sample/educational use — tune models and policies before production moderation decisions)
