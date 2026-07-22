import os
import pytest

os.environ["FLASK_ENV"] = "testing"
os.environ["TEST_MONGO_URI"] = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/cyberbullying_predictor_test")

from app import create_app


@pytest.fixture
def app():
    application = create_app("testing")
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"


def test_predict_requires_auth(client):
    res = client.post("/api/v1/predict", json={"text": "hello"})
    assert res.status_code == 401
