# IRWA — Part 3: Advanced Evaluation with Language Models

This folder contains the solution for **Part 3** of the IRWA Final Project: advanced evaluation using language models for semantic relevance assessment, including embedding-based similarity and model-based ranking.

Notebook: [project_progress/part_3/part3_code.ipynb](project_progress/part_3/part3_code.ipynb)

---

## Table of Contents

- [Overview](#overview)  
- [Required Libraries](#required-libraries)  
- [Project structure](#project-structure)  
- [How to Run](#how-to-run)  
- [Notebook contents & key functions](#notebook-contents--key-functions)  
- [Expected outputs](#expected-outputs)  
- [Problems](#problems)  

---

## Overview

Part 3 focuses on advanced ranking and filtering strategies for search engines, building on indexing from Part 2. It compares multiple ranking methods to improve relevance in product search queries:

- TF-IDF + Cosine Similarity: Baseline ranking using term frequency-inverse document frequency with cosine similarity for query-document matching.
- BM25: Probabilistic ranking function that improves on TF-IDF by handling term saturation and document length normalization.
- Custom Score: Hybrid approach combining TF-IDF with numeric boosts (e.g., ratings, discounts, stock availability) for personalized relevance.
- Word2Vec + Cosine Similarity: Semantic ranking using word embeddings trained on the dataset, capturing meaning beyond keywords.

All methods use AND-filtered candidates from the boolean index and preprocess text via preprocess_text_field from Part 1.

---

## Required Libraries

Install the packages listed in the repository root `requirements.txt`:

- Python 3.10+
- numpy, pandas
- nltk
- sentence-transformers, transformers, torch
- matplotlib, altair
- (Optional) jupyter / ipykernel

Install with:
```bash
pip install -r requirements.txt
```

---

## Project structure
- Notebook:
  - `project_progress/part_3/part3_code.ipynb`
- Data and indexes (generated in Part 2 and used here):
  - `data/fashion_products_dataset_enriched.json`
  - `data/index/boolean_inverted_index.json`
  - `data/index/docid_pid_map.json`
- Word2Vec outputs (generated in Part 3):
  - `data/index/word2vec.model`
  - `data/index/word2vec_docvecs.npy`
  - `data/index/word2vec_docmask.npy`
  - `data/index/word2vec_meta.json`
  - `data/index/w2v_results.json` (batch results for proposed queries)

---

## How to Run

Follow these step-by-step instructions to reproduce results from the notebook.

1. Prepare environment
   - Activate your virtualenv (created at project root):  
     macOS / Linux:
     ```bash
     source irwa_venv/bin/activate
     ```
     Windows:
     ```cmd
     irwa_venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. Open the notebook
   - Using Jupyter:
     ```bash
     python -m notebook
     ```
     Open: `project_progress/part_3/part3_code.ipynb`
   - Or open in VS Code and run cells interactively.

3. Load data and precompute stats (PART 1)
   - Run the initial cells that:
     - Load `data/fashion_products_dataset_enriched.json`
     - Load the boolean index from `data/index/boolean_inverted_index.json`
     - Precompute TF, IDF, TF‑IDF weights, norms, and BM25 stats (`k1`, `b`, `avg_doc_len`)

4. Test ranking methods (PART 1 — TF‑IDF, BM25, Custom)
   - Execute the testing cell:
     ```python
     compare_rankers("women full sleeve sweatshirt cotton", k=5)
     compare_rankers("men slim jeans blue", k=5)
     ```
   - You’ll see top‑K in console for:
     - TF‑IDF + cosine (`score_tfidf`)
     - BM25 (`score_bm25`)
     - Custom (`score_custom`)

5. Train/load Word2Vec and build document vectors (PART 2)
   - Run the Word2Vec section:
     - Train or load `data/index/word2vec.model`
     - Build/load:
       - `data/index/word2vec_docvecs.npy`
       - `data/index/word2vec_docmask.npy`
   - These are created automatically when calling:
     ```python
     model = get_or_train_w2v(docs, INDEXED_TEXT_FIELDS)
     doc_mat, has_vec = build_or_load_doc_matrix(model)
     ```

6. Semantic ranking with Word2Vec (single queries)
   - Run:
     ```python
     for q in ["women full sleeve sweatshirt cotton", "men slim jeans blue"]:
         res = search_w2v_cosine(q, k=5)
         print(f"\n== {q} ==")
         for r in res:
             print(f"{r['pid']} | {r['score_w2v']:.4f} | {(r.get('title') or '')[:70]}")
     ```

7. Batch run on proposed queries from Part 2
   - Ensure `data/index/proposed_test_queries.json` exists (generated in Part 2).
   - Run:
     ```python
     run_word2vec_on_proposed(k=20)
     ```
   - Output: `data/index/w2v_results.json` with top‑K per query.

---

## Notebook contents & key functions
- PART 1: Three Ranking Methods (TF‑IDF + Cosine, BM25, Custom)
  - `search_tfidf_cosine(query, k)`
  - `search_bm25(query, k)`
  - `search_custom_score(query, k)`
  - `compare_rankers(query, k)`
- PART 2: Word2Vec + Cosine Ranking
  - `get_or_train_w2v(records, fields)`
  - `build_or_load_doc_matrix(model) -> (doc_mat, has_vec)`
  - `search_w2v_cosine(query, k)`
  - `run_word2vec_on_proposed(k)`

Shared preprocessing:
- `preprocess_text_field(text)` from `project_progress/utils/preprocessing.py`

---

## Expected outputs
- Console:
  - Top‑K results with scores for TF‑IDF, BM25, Custom (via `compare_rankers`)
  - Top‑K results for Word2Vec (via `search_w2v_cosine`)
- Files under `data/index/`:
  - `word2vec.model`, `word2vec_docvecs.npy`, `word2vec_docmask.npy`, `word2vec_meta.json`
  - `w2v_results.json` with batch top‑K per proposed query

---

## Problems
- FileNotFoundError for indexes or data:
  - Run Part 2 to generate `boolean_inverted_index.json` and `docid_pid_map.json`.
  - Verify `data/fashion_products_dataset_enriched.json` exists.
- Empty results:
  - Queries must contain terms present in the boolean index (AND semantics).
- Word2Vec not training/loading:
  - Check write permissions for `data/index/`.
  - Reduce `vector_size` or increase `min_count` if memory is limited.
- VS Code kernel issues:
  - Select the correct interpreter (the `irwa_venv`) and restart the kernel.