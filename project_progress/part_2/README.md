# IRWA — Part 2: Indexing and Evaluation

This folder contains the solution for **Part 2** of the IRWA Final Project: building an inverted index, ranking with TF–IDF, generating test queries, and performing evaluation with manual annotations.

Notebook: [project_progress/part_2/part2_code.ipynb](project_progress/part_2/part2_code.ipynb)

---

## Table of Contents

- [Overview](#overview)  
- [Required Libraries](#required-libraries)  
- [Installation](#installation)  
- [Project structure](#project-structure)  
- [How to Run](#how-to-run)  
- [Notebook contents & key functions](#notebook-contents--key-functions)  
- [Expected outputs](#expected-outputs)  
- [Problems](#problems)  

---

## Overview

Part 2 implements:

1. A boolean inverted index built from the enriched dataset. See the index builder in [project_progress/part_2/part2_code.ipynb](project_progress/part_2/part2_code.ipynb).
2. Ranking by cosine TF–IDF with per-field weights and an optional Boolean AND pre-filter.
3. Automated proposal of candidate test queries that actually return hits.
4. Utilities for expert labeling (CSV template) and evaluation metrics (P@K, R@K, AP@K, NDCG, MRR).
5. Ablation experiments comparing field-weighting and AND filtering.

All preprocessing uses the same pipeline as Part 1 via [`preprocess_text_field`](project_progress/utils/preprocessing.py).

---

## Required Libraries

Install the packages listed in the repository root `requirements.txt`:

- Python 3.10+
- numpy, pandas
- nltk
- matplotlib, wordcloud, altair
- (Optional) jupyter / ipykernel

Install with:
```bash
pip install -r requirements.txt
```

---

## Project structure (important files)

- Notebook with code and instructions:
  - [project_progress/part_2/part2_code.ipynb](project_progress/part_2/part2_code.ipynb)

- Data (inputs & outputs):
  - Input enriched dataset: [data/fashion_products_dataset_enriched.json](data/fashion_products_dataset_enriched.json)
  - Preprocessed/enriched dataset: [data/fashion_products_dataset_preprocessed.json](data/fashion_products_dataset_preprocessed.json)
  - Index and outputs directory: `data/index/` (written by the notebook)

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
     Open: `project_progress/part_2/part2_code.ipynb`
   - Or open in VS Code and run cells interactively.

3. Run the Indexing section (STEP 1)
   - Execute the "Build inverted index" cell. It reads:
     [data/fashion_products_dataset_enriched.json](data/fashion_products_dataset_enriched.json)
   - Outputs written to `data/index/`:
     - `boolean_inverted_index.json`
     - `docid_pid_map.json`
     - `indexed_fields.json`

4. Generate proposed test queries (STEP 2)
   - Run the "Propose test queries" cells. They use the index and save:
     - `data/index/proposed_test_queries.json`

5. Ranking (STEP 3)
   - Run TF–IDF ranker cells. Main ranking functions:
     - [`search_tfidf`](project_progress/part_2/part2_code.ipynb)
     - [`search_tfidf_and`](project_progress/part_2/part2_code.ipynb)
   - You can persist ranked outputs with:
     - [`save_ranked_results`](project_progress/part_2/part2_code.ipynb) → `data/index/ranked_results.json`

6. Generate annotation template for human judges (Part 3a)
   - Run the cell that writes `data/annotations/queries_label_template.csv`. This uses the top-K from the ranker and must be labeled manually (1/0).

7. Evaluate with labeled judgments (Part 3b / 3c)
   - After human labels are filled into `data/annotations/queries_label_template.csv`, run the evaluation cells.
   - Evaluation functions:
     - [`precision_at_k`](project_progress/part_2/part2_code.ipynb)
     - [`evaluate_query_at_k`](project_progress/part_2/part2_code.ipynb)
     - [`evaluate_multiple_at_k`](project_progress/part_2/part2_code.ipynb)
   - The notebook expects either:
     - a CSV `data/validation_labels.csv` in the format (query_id, pid, labels) for quick evaluation, or
     - the annotated `data/annotations/queries_label_template.csv` for your queries.
   - Ablation experiments save to:
     - `data/index/ablation_results.json`
     - `data/index/ablation_results.csv`

---

## Notebook contents & key functions

Top-level sections in the notebook:

- PART 1: Indexing
  - Build index from `indexed_fields` (title_clean, description_clean, metadata_clean)
  - Key symbol: [`search_and`](project_progress/part_2/part2_code.ipynb) — boolean conjunctive search

- PART 2: Propose test queries
  - Vocabulary-based automatic query generation, saved to `data/index/proposed_test_queries.json`

- PART 3: Ranking
  - TF–IDF ranker with per-field weights
  - Key symbols:
    - [`search_tfidf`](project_progress/part_2/part2_code.ipynb)
    - [`search_tfidf_and`](project_progress/part_2/part2_code.ipynb)
    - [`build_tfidf_ranker`](project_progress/part_2/part2_code.ipynb)
    - [`save_ranked_results`](project_progress/part_2/part2_code.ipynb)

- PART 4: Evaluation
  - Metric implementations and evaluation loops
  - Key symbols:
    - [`precision_at_k`](project_progress/part_2/part2_code.ipynb)
    - [`recall_at_k`](project_progress/part_2/part2_code.ipynb)
    - [`average_precision_at_k`](project_progress/part_2/part2_code.ipynb)
    - [`ndcg_at_k`](project_progress/part_2/part2_code.ipynb)
    - [`evaluate_query_at_k`](project_progress/part_2/part2_code.ipynb)
    - [`evaluate_multiple_at_k`](project_progress/part_2/part2_code.ipynb)

Preprocessing helper:
- [`preprocess_text_field`](project_progress/utils/preprocessing.py) — used to normalize and stem query strings to the same vocabulary.

---

## Expected outputs

After running the notebook you should find:

- Inverted index and metadata in `data/index/`:
  - `boolean_inverted_index.json`
  - `docid_pid_map.json`
  - `indexed_fields.json`

- Proposed queries:
  - `data/index/proposed_test_queries.json`

- Ranking outputs:
  - `data/index/ranked_results.json` (saved by `save_ranked_results`)

- Annotation templates & labels:
  - `data/annotations/queries_label_template.csv` (to be labeled)
  - Optionally: `data/validation_labels.csv` (if provided by instructor)

- Evaluation results:
  - `data/index/eval_my_queries.json`
  - `data/index/ablation_results.json`
  - `data/index/ablation_results.csv`

Console output will show vocabulary size, number of docs loaded, top-ranked examples, and summary metrics (MAP, MRR, NDCG) for ablation runs.

---

## Problems

- Enriched dataset not found:
  - Ensure `data/fashion_products_dataset_enriched.json` is present. See the preprocessing notebook in Part 1 that creates it.

- NLTK resources missing:
  - Run:
    ```python
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    ```
  - The notebook imports [`preprocess_text_field`](project_progress/utils/preprocessing.py) which already attempts to download missing NLTK resources.

- CSV / annotation file problems:
  - If `data/annotations/queries_label_template.csv` already exists the notebook will not overwrite it (controlled by `OVERWRITE` flag). Delete it or set `OVERWRITE = True` to regenerate.

- Large candidate sets:
  - Ranking with the full candidate set can be slow. The notebook uses an AND pre-filter option (`search_tfidf_and`) to reduce candidates.

---