import re
from unidecode import unidecode
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

def _ensure_nltk():
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")
    try:
        word_tokenize("test")
    except LookupError:
        nltk.download("punkt")

_ensure_nltk()

STOPWORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()

def normalize_basic(text: str) -> str:
    if not text:
        return ""
    txt = unidecode(text.lower())
    txt = re.sub(r"http[s]?://\S+", " ", txt)
    txt = re.sub(r"[-_/]", " ", txt)
    txt = re.sub(r"\d+", " ", txt)
    txt = re.sub(r"[^\w\s]", " ", txt)
    txt = re.sub(r"[^a-z\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def preprocess_text_field(text: str):
    cleaned = normalize_basic(text)
    toks = word_tokenize(cleaned) if cleaned else []
    toks = [t for t in toks if t not in STOPWORDS]
    toks = [STEMMER.stem(t) for t in toks]
    return {"tokens": toks, "text": " ".join(toks)}
