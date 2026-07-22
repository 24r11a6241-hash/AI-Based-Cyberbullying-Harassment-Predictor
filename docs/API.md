# API Reference

Base URL: `http://localhost:5000`

Authenticated routes require header:

```
Authorization: Bearer <JWT>
```

## Health

`GET /api/v1/health`

Response:

```json
{ "status": "ok", "model_loaded": true }
```

## Auth

### Register

`POST /auth/register`

```json
{ "username": "jane", "email": "jane@example.com", "password": "Secret123" }
```

### Login

`POST /auth/login`

```json
{ "email": "jane@example.com", "password": "Secret123" }
```

Returns `token` and `user`.

### Current User

`GET /auth/me` (JWT required)

## Predictions

### Predict

`POST /api/v1/predict`

```json
{ "text": "Your comment here", "save_history": true }
```

Response fields include:

- `primary_label`, `confidence`, `confidence_percent`
- `severity`, `sentiment`
- `all_scores`, `toxic_keywords`, `highlighted_text`
- `prediction_id` (when saved)

### History

`GET /api/v1/history?limit=50&skip=0`

### History Item

`GET /api/v1/history/<prediction_id>`

### Metrics

`GET /api/v1/metrics`

## Admin (JWT + admin role)

### Stats

`GET /api/v1/admin/stats`

### Users

`GET /api/v1/admin/users`

### Recent Predictions

`GET /api/v1/admin/predictions/recent?limit=20`

### Top Keywords

`GET /api/v1/admin/keywords/top`

### Model Status

`GET /api/v1/admin/model/status`

### Retrain

`POST /api/v1/admin/model/retrain`

```json
{ "dataset_path": "data/train.csv" }
```

Omit `dataset_path` to use `TRAIN_DATA_PATH` or sample dataset from config.

## Error Format

```json
{ "error": "Human-readable message" }
```

Common status codes: `400`, `401`, `403`, `404`, `413`, `500`, `503`
