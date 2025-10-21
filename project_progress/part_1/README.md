# IRWA Project - Part 1: Text Processing & Exploratory Data Analysis (EDA)

This directory contains the solution for **Part 1** of the IRWA Final Project, which focuses on text preprocessing and exploratory data analysis of the fashion products dataset.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Required Libraries](#required-libraries)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Notebook Contents](#notebook-contents)
- [Expected Outputs](#expected-outputs)
- [Problems](#problems)

---

## 🔍 Overview

Part 1 implements a complete text preprocessing pipeline and performs exploratory data analysis on the fashion products dataset. The main tasks include:

1. **Data Preparation**: Text normalization, tokenization, stopword removal, and stemming using NLTK
2. **Statistical Analysis**: Corpus statistics, token distributions, and dataset characteristics
3. **Exploratory Data Analysis**: Visualizations including word clouds, frequency distributions, and data insights

---

## 📚 Required Libraries

The project uses the following Python libraries:

### Core Libraries
- **Python 3.10+** (required for compatibility)
- **nltk** (3.9.1) - Natural Language Toolkit for text processing
- **pandas** (2.3.2) - Data manipulation and analysis
- **numpy** (2.2.6) - Numerical computations

### Visualization Libraries
- **matplotlib** (via matplotlib-inline 0.1.7) - Plotting and visualizations
- **wordcloud**
- **altair** (5.5.0) - Declarative statistical visualizations

### Text Processing
- **unidecode** - Remove accents and normalize Unicode text
- **regex** (2025.9.1) - Advanced regular expression operations

### Additional Dependencies
- **jupyter** / **ipykernel** (6.30.1) - For running Jupyter notebooks
- **ipython** (8.37.0) - Enhanced interactive Python shell

All dependencies are listed in the root `requirements.txt` file.

---

## 🚀 Installation

### Prerequisites

Make sure you have **Python 3.10 or higher** installed on your system.

```bash
python3 --version
# Should output Python 3.10.x or higher
```

### Step 1: Clone the Repository

```bash
git clone https://github.com/lucassandreu/irwa-search-engine.git
cd irwa-search-engine
```

### Step 2: Create a Virtual Environment

**On macOS/Linux:**
```bash
python3.10 -m venv irwa_venv
source irwa_venv/bin/activate
```

**On Windows:**
```cmd
python -m venv irwa_venv
irwa_venv\Scripts\activate
```

### Step 3: Install Dependencies

With your virtual environment activated, install all required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all necessary libraries including:
- NLTK (stopwords, punkt tokenizer)
- Pandas for data manipulation
- Matplotlib for visualizations
- Jupyter for running notebooks
- And all other dependencies

---

## 📁 Project Structure

```
project_progress/part_1/
├── README.md                                    
├── part1_code.ipynb                            # Jupyter notebook with solution code
└── IRWA-2025-u214570-u-u-part-1.pdf            # Project report 
```

---

## ▶️ How to Run

### Option 1: Using Jupyter Notebook (Recommended)

1. **Ensure your virtual environment is activated:**
   ```bash
   source irwa_venv/bin/activate  # macOS/Linux
   # or
   irwa_venv\Scripts\activate     # Windows
   ```

2. **Start Jupyter Notebook:**
    - Ensure that Jupyter Notebook is installed:
    ```bash
   jupyter --version
   ```
    - You should see that the package notebook is installed.
    - If not, you install notebook with the following command:
    ```bash
   pip install jupyter notebook
   ```
   - Once installed you start Jupyter Notebook
   ```bash
   python -m notebook
   ```

3. **Navigate to the notebook:**
   - In your browser, navigate to: `project_progress/part_1/`
   - Open `part1_code.ipynb`

4. **Run all cells:**
   - Click `Cell` → `Run All` from the menu
   - Or use `Shift + Enter` to run cells sequentially

### Option 2: Using VS Code

1. **Open the project in VS Code:**
   ```bash
   code . # opens VSCode in the actual directory
   ```

2. **Select the Python interpreter:**
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from `irwa_venv`

3. **Open the notebook:**
   - Navigate to `project_progress/part_1/part1_code.ipynb`
   - Click "Run All" or run cells individually

---

## 📓 Notebook Contents

The `part1_code.ipynb` notebook is organized into the following sections:

### **Section 1: Data Preparation**

#### **Step 1 — Preprocessing Pipeline (NLTK)**
- **Main Code**: Complete implementation of the preprocessing pipeline
  - Text normalization (lowercase, accent removal, URL/number removal)
  - Tokenization using NLTK's word_tokenize
  - Stopword removal
  - Porter Stemmer for word stemming
  - JSON input/output handling

- **Verification Code**: Tests to ensure preprocessing works correctly

**Key Functions:**
- `normalize_basic(text)` - Basic text cleaning and normalization
- `tokenize(text)` - Tokenize text into words
- `remove_stopwords(tokens)` - Remove common English stopwords
- `stem(tokens)` - Apply Porter Stemmer
- `preprocess_text_field(text)` - Complete preprocessing pipeline
- `process_record(rec)` - Process entire JSON records

### **Section 2: Exploratory Data Analysis (EDA)**

- Statistical analysis of the corpus
- Token frequency distributions
- Vocabulary size calculations
- Data visualizations (word clouds, bar charts, etc.)
- Insights and observations about the dataset

---

## 📊 Expected Outputs

After running the notebook, you should see:

1. **Preprocessed Dataset File:**
   - Location: `data/fashion_products_dataset_preprocessed.json`
   - Contains all original fields plus:
     - `title_tokens`: List of preprocessed title tokens
     - `title_clean`: Cleaned title text (space-separated tokens)
     - `description_tokens`: List of preprocessed description tokens
     - `description_clean`: Cleaned description text

2. **Console Output:**
   - Number of processed records
   - Example of preprocessed data
   - Verification results
   - Statistical summaries

3. **Visualizations:**
   - Word clouds
   - Token frequency distributions
   - Statistical charts
   - EDA insights

4. **Statistics:**
   - Total number of documents
   - Vocabulary size
   - Average document length
   - Token distribution metrics

---

## 🔧 Problems

### Common Issues and Solutions

#### **Issue: NLTK Data Not Found**

**Error:** `LookupError: Resource stopwords not found`

**Solution:**
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
```

#### **Issue: Dataset File Not Found**

**Error:** `FileNotFoundError: Input file not found`

**Solution:**
- Ensure `fashion_products_dataset.json` is in the `data/` directory
- Check the file path in the notebook matches your directory structure

#### **Issue: Python Version Incompatibility**

**Error:** `ERROR: Could not find a version that satisfies the requirement click==8.2.1`

**Solution:**
- Upgrade to Python 3.10 or higher:
  ```bash
  brew install python@3.10  # macOS
  python3.10 -m venv irwa_venv
  source irwa_venv/bin/activate
  pip install -r requirements.txt
  ```

#### **Issue: Import Errors**

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
1. Ensure virtual environment is activated
2. Reinstall requirements:
   ```bash
   pip install -r requirements.txt
   ```
---

## 📝 Notes

- **Dataset:** The `fashion_products_dataset.json` file must be placed in the `data/` directory at the repository root
- **Output:** Preprocessed data is saved to `data/fashion_products_dataset_preprocessed.json`
- **Python Version:** Python 3.10+ is required due to dependency requirements

---

## 🤝 Support

If you encounter any issues:

1. Check this README's [Problems](#problems) section
2. Verify all dependencies are installed correctly
3. Ensure you're using Python 3.10 or higher
4. Check that your virtual environment is activated

---

## 📚 Additional Resources

- [NLTK Documentation](https://www.nltk.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Jupyter Notebook Documentation](https://jupyter-notebook.readthedocs.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

