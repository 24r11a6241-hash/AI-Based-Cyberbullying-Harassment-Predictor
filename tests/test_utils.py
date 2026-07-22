import pytest
from app.utils.nlp_preprocessor import NLPPreprocessor
from app.utils.validators import validate_registration, validate_prediction_text
from app.utils.severity import compute_severity, compute_sentiment


def test_preprocess_lowercase_and_clean():
    prep = NLPPreprocessor()
    out = prep.preprocess("Check HTTPS://EVIL.com NOW!!!")
    assert "http" not in out
    assert out.islower() or out == ""


def test_extract_toxic_keywords():
    prep = NLPPreprocessor()
    kws = prep.extract_toxic_keywords("You are such an idiot")
    assert "idiot" in kws


def test_validate_registration():
    ok, _ = validate_registration("user@example.com", "Password1", "testuser")
    assert ok is True
    ok, err = validate_registration("bad", "short", "ab")
    assert ok is False and err


def test_validate_prediction_text():
    ok, _ = validate_prediction_text("hello world")
    assert ok is True
    ok, err = validate_prediction_text("   ")
    assert ok is False and "empty" in err.lower()


def test_severity_normal_low():
    assert compute_severity("Normal", 0.9) == "Low"


def test_sentiment_threat():
    assert compute_sentiment("Threat", 0.8) == "Very Negative"
