import json
import math
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Iterable, Optional

# For repo imports
import sys
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "project_progress"))
from utils.preprocessing import preprocess_text_field

from myapp.search.objects import Document, ResultItem


# Load enriched corpus + boolean index
DATA_DIR = REPO_ROOT / "data"
INDEX_DIR = DATA_DIR / "index"

ENRICHED_PATH = DATA_DIR / "fashion_products_dataset_enriched.json"
INVERTED_PATH = INDEX_DIR / "boolean_inverted_index.json"
DOCMAP_PATH = INDEX_DIR / "docid_pid_map.json"

docs_raw: List[Dict[str, Any]] = json.loads(ENRICHED_PATH.read_text(encoding="utf-8"))
inverted_index: Dict[str, List[int]] = json.loads(INVERTED_PATH.read_text(encoding="utf-8"))
docid_to_pid: Dict[str, str] = json.loads(DOCMAP_PATH.read_text(encoding="utf-8"))["docid_to_pid"]

N_DOCS = len(docs_raw)

INDEXED_TEXT_FIELDS = ["title_clean", "description_clean", "metadata_clean"]

# Helpers
def _doc_tokens(record: Dict[str, Any], fields: Iterable[str]) -> List[str]:
    toks: List[str] = []
    for f in fields:
        val = record.get(f)
        if val:
            toks.extend(str(val).split())
    return toks

def _query_tokens(q: str) -> List[str]:
    return preprocess_text_field(q or "")["tokens"]

def _intersect_sorted(a: List[int], b: List[int]) -> List[int]:
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out

def _candidate_docs_and(q_terms: List[str]) -> List[int]:
    """AND semantics via boolean index."""
    if not q_terms:
        return []
    postings = []
    for t in set(q_terms):
        pl = inverted_index.get(t)
        if not pl:
            return []
        postings.append(pl)
    postings.sort(key=len)
    res = postings[0]
    for pl in postings[1:]:
        res = _intersect_sorted(res, pl)
        if not res:
            break
    return res

def _candidate_docs_or(q_terms: List[str]) -> List[int]:
    """Union fallback."""
    cands = set()
    for t in set(q_terms):
        cands.update(inverted_index.get(t, []))
    return sorted(list(cands))


# Precompute TF, DF, norms
term_df: Dict[str, int] = {t: len(pl) for t, pl in inverted_index.items()}

doc_tf: Dict[int, Dict[str, int]] = {}
doc_len: Dict[int, int] = {}

for did, rec in enumerate(docs_raw):
    toks = _doc_tokens(rec, INDEXED_TEXT_FIELDS)
    tf = Counter(toks)
    doc_tf[did] = dict(tf)
    doc_len[did] = sum(tf.values())

avg_doc_len = sum(doc_len.values()) / max(N_DOCS, 1)


# TF-IDF (log2, no smoothing) 
idf_tfidf: Dict[str, float] = {}
for t, df in term_df.items():
    idf_tfidf[t] = math.log2(N_DOCS / df) if df > 0 else 0.0

tfidf_weights: Dict[int, Dict[str, float]] = {}
doc_norms: Dict[int, float] = {}

for did, tf_map in doc_tf.items():
    w_map = {}
    sq = 0.0
    for t, f in tf_map.items():
        if f <= 0:
            continue
        w = (1.0 + math.log2(f)) * idf_tfidf.get(t, 0.0)
        if w != 0:
            w_map[t] = w
            sq += w * w
    tfidf_weights[did] = w_map
    doc_norms[did] = math.sqrt(sq) if sq > 0 else 0.0


# BM25
idf_bm25: Dict[str, float] = {}
for t, df in term_df.items():
    idf_bm25[t] = math.log((N_DOCS - df + 0.5) / (df + 0.5) + 1.0)

k1 = 1.5
b = 0.75


# Core scoring functions
def _tfidf_cosine_scores(q_terms: List[str], cand_ids: List[int]) -> Dict[int, float]:
    if not cand_ids:
        return {}
    q_tf = Counter(q_terms)
    q_w = {}
    q_sq = 0.0
    for t, f in q_tf.items():
        w = (1.0 + math.log2(f)) * idf_tfidf.get(t, 0.0)
        if w != 0:
            q_w[t] = w
            q_sq += w * w
    q_norm = math.sqrt(q_sq)
    if q_norm == 0:
        return {}

    scores = {}
    for did in cand_ids:
        d_w = tfidf_weights.get(did, {})
        d_norm = doc_norms.get(did, 0.0)
        if d_norm == 0.0:
            continue
        dot = sum(q_w[t] * d_w.get(t, 0.0) for t in q_w)
        if dot > 0:
            scores[did] = dot / (q_norm * d_norm)
    return scores

def _bm25_scores(q_terms: List[str], cand_ids: List[int]) -> Dict[int, float]:
    if not cand_ids:
        return {}
    q_unique = list(set(q_terms))
    scores = {}
    for did in cand_ids:
        tf_map = doc_tf.get(did, {})
        dl = doc_len.get(did, 0)
        if dl == 0:
            continue
        s = 0.0
        for t in q_unique:
            f = tf_map.get(t, 0)
            if f <= 0:
                continue
            idf = idf_bm25.get(t, 0.0)
            denom = f + k1 * (1.0 - b + b * dl / avg_doc_len)
            s += idf * (f * (k1 + 1.0) / denom)
        if s != 0:
            scores[did] = s
    return scores

def _numeric_boost(rec: Dict[str, Any]) -> float:
    rating = rec.get("average_rating_num") or 0.0
    discount = rec.get("discount_pct") or 0
    price = rec.get("selling_price_num") or rec.get("actual_price_num") or 0.0
    out_of_stock = rec.get("out_of_stock_bool")

    rating_norm = max(0.0, min(rating / 5.0, 1.0))
    discount_norm = max(0.0, min(discount / 80.0, 1.0))

    price_cap = 4000.0
    price_norm = 0.5 if price <= 0 else 1.0 - min(price, price_cap) / price_cap

    stock_factor = 1.0 if not out_of_stock else 0.2
    boost = 1.0 + 0.5 * rating_norm + 0.4 * discount_norm + 0.3 * price_norm
    return boost * stock_factor


# Public function used by SearchEngine
def search_in_corpus(
    query: str,
    search_id: int,
    corpus: Dict[str, Document],
    method: str = "bm25",
    k: int = 20,
    use_and: bool = True
) -> List[ResultItem]:
    """
    Returns top-k ResultItem objects (safe for UI rendering).
    Each item includes ranking + product fields + internal + source URLs.
    """
    q_terms = _query_tokens(query)

    # candidate selection
    if use_and:
        cand_ids = _candidate_docs_and(q_terms)
        if not cand_ids:
            cand_ids = _candidate_docs_or(q_terms)
    else:
        cand_ids = _candidate_docs_or(q_terms)

    if not cand_ids:
        return []

    # scoring
    if method == "tfidf":
        scores = _tfidf_cosine_scores(q_terms, cand_ids)
    elif method == "custom":
        base = _tfidf_cosine_scores(q_terms, cand_ids)
        scores = {did: sc * _numeric_boost(docs_raw[did]) for did, sc in base.items()}
    else:
        scores = _bm25_scores(q_terms, cand_ids)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

    results: List[ResultItem] = []
    for did, score in ranked:
        pid = docs_raw[did].get("pid") or docid_to_pid.get(str(did))
        doc_obj = corpus.get(pid)
        if not doc_obj:
            continue
        results.append(
            ResultItem(
                pid=doc_obj.pid,
                title=doc_obj.title,
                description=doc_obj.description,
                selling_price=doc_obj.selling_price,
                discount=doc_obj.discount,
                actual_price=doc_obj.actual_price,
                average_rating=doc_obj.average_rating,
                out_of_stock=doc_obj.out_of_stock,
                ranking=float(score),

                # internal link to your details page
                url=f"/doc_details?pid={pid}&search_id={search_id}",

                # original Flipkart link
                source_url=doc_obj.url
            )
        )

    return results