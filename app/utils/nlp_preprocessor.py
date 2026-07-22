"""NLP preprocessing pipeline for toxicity detection."""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_nltk_ready = False


def ensure_nltk_data():
    """Download required NLTK resources once."""
    global _nltk_ready
    if _nltk_ready:
        return
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
        ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except (LookupError, OSError):
            nltk.download(name, quiet=True)
    _nltk_ready = True


class NLPPreprocessor:
    """Text cleaning and normalization for ML models."""

    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    MENTION_PATTERN = re.compile(r"@\w+")
    HASHTAG_PATTERN = re.compile(r"#(\w+)")

    TOXIC_KEYWORDS = {
        "hate", "kill", "die", "stupid", "idiot", "moron", "ugly", "loser",
        "worthless", "trash", "garbage", "freak", "disgusting", "pathetic",
        "threat", "attack", "harass", "abuse", "slut", "whore", "rape",
        "nazi", "terrorist", "retard", "faggot", "bitch", "bastard",
    }

    def __init__(self):
        ensure_nltk_data()
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def to_lowercase(self, text: str) -> str:
        return text.lower()

    def remove_urls(self, text: str) -> str:
        return self.URL_PATTERN.sub(" ", text)

    def remove_mentions(self, text: str) -> str:
        return self.MENTION_PATTERN.sub(" ", text)

    def normalize_hashtags(self, text: str) -> str:
        return self.HASHTAG_PATTERN.sub(r"\1", text)

    def remove_punctuation(self, text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))

    def tokenize(self, text: str) -> list[str]:
        return word_tokenize(text)

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        return [t for t in tokens if t not in self.stop_words and len(t) > 1]

    def lemmatize(self, tokens: list[str]) -> list[str]:
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def preprocess(self, text: str, for_display: bool = False) -> str:
        """Full pipeline; returns space-joined cleaned text."""
        if not text or not str(text).strip():
            return ""
        cleaned = str(text).strip()
        cleaned = self.to_lowercase(cleaned)
        cleaned = self.remove_urls(cleaned)
        cleaned = self.remove_mentions(cleaned)
        cleaned = self.normalize_hashtags(cleaned)
        if for_display:
            return cleaned
        cleaned = self.remove_punctuation(cleaned)
        tokens = self.tokenize(cleaned)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize(tokens)
        return " ".join(tokens)

    def extract_toxic_keywords(self, text: str) -> list[str]:
        """Find toxic terms in original text for UI highlighting."""
        if not text:
            return []
        words = re.findall(r"[a-zA-Z']+", text.lower())
        found = []
        for w in words:
            if w in self.TOXIC_KEYWORDS and w not in found:
                found.append(w)
        return found

    def highlight_toxic_keywords(self, text: str, keywords: list[str]) -> str:
        """Wrap toxic keywords in mark tags for HTML display."""
        if not keywords:
            return text
        result = text
        for kw in sorted(keywords, key=len, reverse=True):
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            result = pattern.sub(
                lambda m: f'<mark class="toxic-highlight">{m.group(0)}</mark>',
                result,
            )
        return result
