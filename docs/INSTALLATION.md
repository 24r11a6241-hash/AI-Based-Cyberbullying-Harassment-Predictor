# Installation Guide

## 1. System requirements

| Component | Version |
|-----------|---------|
| Python | 3.11+ recommended (3.14 supported) |
| MongoDB | 6.x or 7.x |
| OS | Linux, macOS, Windows (WSL) |

## 2. Clone and virtual environment

```bash
cd ~/Projects/cyberbullying-predictor
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 3. Environment variables

```bash
cp .env.example .env
```

Edit `.env` for secrets and MongoDB URI.

## 4. NLTK data (first run)

```bash
python -m nltk.downloader punkt punkt_tab stopwords wordnet averaged_perceptron_tagger averaged_perceptron_tagger_eng
```

The app also attempts automatic downloads on first NLP use.

## 5. MongoDB

Start MongoDB locally or use Docker:

```bash
docker run -d --name mongo -p 27017:27017 mongo:7
python database/init_db.py
```

## 6. Train the model

**Sample data (included):**

```bash
python -m ml.train --data data/sample_dataset.csv
```

**Full Jigsaw dataset:**

1. Download `train.csv` from Kaggle Jigsaw Toxic Comment Classification Challenge.
2. Place at `data/train.csv`.
3. Run: `python -m ml.train --data data/train.csv`

Artifacts are written to `saved_models/` and `reports/`.

## 7. Run the application

```bash
python run.py
```

Visit `http://127.0.0.1:5000`.

Default admin: credentials from `.env` (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).

## 8. Production (Gunicorn)

```bash
gunicorn -b 0.0.0.0:5000 -w 4 run:app
```

## 9. Docker Compose

```bash
docker compose up --build
```

## 10. Verify

```bash
pytest tests/ -q
curl http://localhost:5000/api/v1/health
```
