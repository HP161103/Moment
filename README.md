# Moment — Data Pipeline

> **Read. Moments. Worth. Sharing.**
> DADS7305 / IE7305 · MLOps · Group 23 · Northeastern University

Moment is a private reading platform that uses machine learning to match intellectually compatible readers. Users capture book passages as visual "moments," write personal reflections, and are quietly matched with readers who think and feel similarly about literature — without performative social media posting.

This repository contains the **Data Pipeline (Assignment 1)**. It implements every required component: data acquisition, preprocessing, feature engineering, schema validation using TFDV, anomaly detection with alert generation, bias detection using data slicing, DVC versioning, Airflow DAG orchestration with Gantt optimization, and comprehensive unit testing — covering all 12 evaluation criteria.

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Dataset Overview](#2-dataset-overview)
3. [Pipeline Architecture](#3-pipeline-architecture)
4. [Environment Setup](#4-environment-setup)
5. [Running the Pipeline](#5-running-the-pipeline)
6. [Data Acquisition](#6-data-acquisition)
7. [Data Preprocessing](#7-data-preprocessing)
8. [Feature Engineering](#8-feature-engineering)
9. [Schema & Statistics Generation — TFDV](#9-schema--statistics-generation--tfdv)
10. [Anomaly Detection & Alert Generation](#10-anomaly-detection--alert-generation)
11. [Bias Detection & Mitigation](#11-bias-detection--mitigation)
12. [Airflow DAGs & Gantt Optimization](#12-airflow-dags--gantt-optimization)
13. [Data Versioning with DVC](#13-data-versioning-with-dvc)
14. [Error Handling](#14-error-handling)
15. [Logging](#15-logging)
16. [Testing](#16-testing)
17. [CI/CD Workflow](#17-cicd-workflow)
18. [Code Style & Standards](#18-code-style--standards)
19. [Reproducibility — Run on Any Machine](#19-reproducibility--run-on-any-machine)
20. [Evaluation Criteria Coverage](#20-evaluation-criteria-coverage)

---

## 1. Repository Structure

Organised following the folder structure from the assignment guidelines, and modelled after production open-source Python projects such as [scikit-learn](https://github.com/scikit-learn/scikit-learn).

```
Moment/                                      ← Project Root
│
├── data_pipeline/                           ← Main pipeline directory
│   │
│   ├── dags/                                ← Airflow DAGs
│   │   ├── data_pipeline_dag.py             ← Main pipeline DAG
│   │   └── tests_dag.py                     ← DAG that runs pytest suite
│   │
│   ├── data/                                ← All data files
│   │   ├── raw/
│   │   │   ├── pdfs/                        ← Source passage PDFs
│   │   │   │   ├── 0.Character traits - 50.pdf
│   │   │   │   ├── 1.Frankenstein/
│   │   │   │   │   ├── Frankenstein_Passage_1_SELECTABLE.pdf
│   │   │   │   │   ├── Frankenstein_Passage_2_SELECTABLE.pdf
│   │   │   │   │   └── Frankenstein_Passage_3_SELECTABLE.pdf
│   │   │   │   ├── 2.Pride and Prejudice/
│   │   │   │   │   ├── Pride_and_Prejudice_Passage_1_SELECTABLE.pdf
│   │   │   │   │   ├── Pride_and_Prejudice_Passage_2_SELECTABLE.pdf
│   │   │   │   │   └── Pride_and_Prejudice_Passage_3_SELECTABLE.pdf
│   │   │   │   └── 3.The Great Gatsby/
│   │   │   │       ├── Gatsby_Passage_1_SELECTABLE.pdf
│   │   │   │       ├── Gatsby_Passage_2_SELECTABLE.pdf
│   │   │   │       └── Gatsby_Passage_3_SELECTABLE.pdf
│   │   │   ├── csvs_jsons/
│   │   │   │   ├── all_interpretations_450_FINAL_NO_BIAS.json
│   │   │   │   ├── characters.csv
│   │   │   │   ├── passages.csv
│   │   │   │   ├── passages.json
│   │   │   │   ├── interpretations.json
│   │   │   │   └── user_interpretations.csv
│   │   │   ├── books.json
│   │   │   ├── user_data.csv
│   │   │   ├── user_interpretations.json
│   │   │   └── passage_details.csv
│   │   ├── processed/                       ← DVC-tracked preprocessed outputs
│   │   │   ├── books_processed.json
│   │   │   ├── moments_processed.json
│   │   │   └── users_processed.json
│   │   └── reports/                         ← DVC-tracked pipeline reports
│   │       ├── bias_report_FINAL.md         ← Bias findings + trade-offs
│   │       ├── schema_stats.json            ← TFDV statistics
│   │       ├── validation_report.json       ← TFDV validation results
│   │       └── notification.txt             ← Anomaly alert log
│   │
│   ├── scripts/                             ← One script per pipeline stage
│   │   ├── __init__.py
│   │   ├── data_acquisition.py              ← Stage 1
│   │   ├── preprocessor.py                  ← Stage 2
│   │   ├── feature_engineering.py           ← Stage 3
│   │   ├── validation.py                    ← Stage 4
│   │   ├── anomalies.py                     ← Stage 5
│   │   ├── bias_detection.py                ← Stage 6
│   │   ├── generate_schema_stats.py         ← Stage 7 (TFDV)
│   │   ├── generate_html_report.py          ← Stage 8
│   │   ├── generate_enhanced_dashboard.py   ← Stage 9
│   │   ├── run.py                           ← Runs all stages in sequence
│   │   └── utils.py                         ← Shared utilities
│   │
│   ├── tests/                               ← All unit and integration tests
│   │   ├── test_acquisition.py
│   │   ├── test_preprocessing.py
│   │   ├── test_validation.py
│   │   ├── test_schema_stats.py
│   │   ├── test_bias_detection.py
│   │   └── test_pipeline.py
│   │
│   ├── logs/                                ← Pipeline execution logs
│   │   └── pipeline.log
│   │
│   ├── config/
│   │   ├── config.yaml                      ← Global pipeline config
│   │   ├── preprocessing_config.yaml        ← Preprocessing rules & thresholds
│   │   └── schema.yaml                      ← Data schema definition
│   │
│   └── preprocessing/                       ← Standalone preprocessing module
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── preprocessor.py
│       │   └── anomalies.py
│       ├── data/
│       │   ├── raw/
│       │   └── processed/
│       ├── config.yaml
│       ├── requirements.txt
│       ├── run.py
│       └── test_pipeline.py
│
├── bias_detection/                          ← Standalone bias detection module
│   ├── bias_detection.py
│   ├── test_bias_detection.py
│   └── all_interpretations_450_FINAL_NO_BIAS.json
│
├── data/                                    ← Root-level extraction scripts
│   ├── character_extraction.py
│   ├── data_extraction.py
│   └── remove_new_lines.py
│
├── models/
│   └── training.py                          ← Model training (Assignment 2)
│
├── .dvc/                                    ← DVC config — committed to Git
│   ├── .gitignore
│   └── config
├── .dvcignore
├── .github/
│   └── workflows/
│       └── config.yaml                      ← GitHub Actions CI/CD
├── .gitignore
├── conftest.py                              ← Root pytest config & shared fixtures
├── docker-compose.yaml                      ← Airflow + postgres (Docker)
├── dvc.yaml                                 ← DVC pipeline stage definitions
└── requirements.txt                         ← All dependencies, version-pinned
```

> **`data_pipeline/logs/`** is created automatically on first run. It is excluded from Git via `.gitignore` but the directory is committed with `.gitkeep` so it always exists on a fresh clone.

---

## 2. Dataset Overview

### Why Synthetic Data?

Moment's core privacy principle is that user interpretations never leave the local system. Using real user data for model training would violate that promise. Synthetic data designed to reflect authentic human reading patterns lets us build and validate the full ML pipeline while preserving privacy by design.

### Dataset

| Property | Value |
|---|---|
| Final dataset file | `data_pipeline/data/raw/csvs_jsons/all_interpretations_450_FINAL_NO_BIAS.json` |
| Total interpretations | 450 |
| Character personas | 50 |
| Books | 3 — *Frankenstein*, *Pride & Prejudice*, *The Great Gatsby* |
| Passages per book | 3 (9 total) |
| Format | JSON |

### Source PDFs

All 9 passage PDFs are committed to the repository under `data_pipeline/data/raw/pdfs/`:

| Book | Author | Year |
|---|---|---|
| *Frankenstein* | Mary Shelley | 1818 |
| *Pride & Prejudice* | Jane Austen | 1813 |
| *The Great Gatsby* | F. Scott Fitzgerald | 1925 |

All books are public domain (pre-1928), sourced from [Project Gutenberg](https://www.gutenberg.org/).

---

## 3. Pipeline Architecture

Schema statistics generation and anomaly detection run **in parallel** after validation — a bottleneck identified via Airflow Gantt (see [Section 12](#12-airflow-dags--gantt-optimization)).

```
┌──────────────────────────────────────────────────────────┐
│               DATA ACQUISITION                           │
│  data/character_extraction.py                            │
│  data/data_extraction.py                                 │
│  data_pipeline/scripts/data_acquisition.py               │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│               PREPROCESSING                              │
│  scripts/preprocessor.py                                 │
│  preprocessing/pipeline/preprocessor.py                  │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│               FEATURE ENGINEERING                        │
│  scripts/feature_engineering.py                          │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│               VALIDATION                                 │
│  scripts/validation.py + config/schema.yaml              │
└──────────┬──────────────────────────┬────────────────────┘
           │ (parallel)               │ (parallel)
┌──────────▼──────────┐   ┌───────────▼──────────────────┐
│  SCHEMA & STATS     │   │   ANOMALY DETECTION          │
│  generate_schema    │   │   scripts/anomalies.py       │
│  _stats.py (TFDV)   │   │   preprocessing/anomalies.py │
│  → schema_stats.json│   │   IQR · Z-score · TF-IDF     │
│  → validation_report│   │   → notification.txt (alert) │
└──────────┬──────────┘   └───────────┬──────────────────┘
           └──────────────┬───────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│               BIAS DETECTION                             │
│  scripts/bias_detection.py                               │
│  bias_detection/bias_detection.py                        │
│  Pandas data slicing across demographic subgroups        │
│  → data/reports/bias_report_FINAL.md                     │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│               REPORT GENERATION                          │
│  scripts/generate_html_report.py                         │
│  scripts/generate_enhanced_dashboard.py                  │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│               DVC VERSIONING                             │
│  dvc.yaml — versions processed/ + reports/               │
│  .dvc pointer files committed to Git                     │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Runtime |
| Docker Desktop | Latest | Airflow and services |
| Git | Any | Version control |
| DVC | 3.x | Data versioning (via requirements.txt) |

### Step 1 — Clone

```bash
git clone https://github.com/jyothssena/Moment.git
cd Moment
```

### Step 2 — Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

All packages are version-pinned. Key packages:

| Package | Purpose |
|---|---|
| `apache-airflow` | DAG orchestration |
| `dvc` | Data versioning |
| `tensorflow-data-validation` | Schema validation and statistics |
| `scikit-learn` | TF-IDF for anomaly duplicate detection |
| `pandas`, `numpy` | Data processing and bias slicing |
| `pytest`, `pytest-cov` | Testing |

### Step 4 — Start Airflow

```bash
docker-compose up airflow-init    # first time only
docker-compose up -d
docker-compose ps                 # confirm all containers healthy
```

Airflow UI: **http://localhost:8080** — username: `airflow` / password: `airflow`

```bash
docker-compose down               # stop when done
```

### Step 5 — Pull Versioned Data

```bash
dvc pull
```

> If no remote is configured, skip this — run the pipeline directly and it will regenerate all data from the source PDFs in the repository.

---

## 5. Running the Pipeline

### Option A — Airflow UI (Full Orchestration)

1. Open **http://localhost:8080**
2. Find `moment_data_pipeline` → toggle **on**
3. Click **▶ Trigger DAG**
4. Watch progress in **Graph View**
5. Open **Gantt** tab to see per-task timing

### Option B — Runner Script (No Docker)

```bash
python data_pipeline/scripts/run.py
```

### Option C — Standalone Preprocessing Module

```bash
cd data_pipeline/preprocessing
python run.py
```

### Option D — Individual Stages

```bash
python data_pipeline/scripts/data_acquisition.py
python data_pipeline/scripts/preprocessor.py
python data_pipeline/scripts/feature_engineering.py
python data_pipeline/scripts/validation.py
python data_pipeline/scripts/generate_schema_stats.py   # parallel with anomalies
python data_pipeline/scripts/anomalies.py               # parallel with schema stats
python data_pipeline/scripts/bias_detection.py
python data_pipeline/scripts/generate_html_report.py
python data_pipeline/scripts/generate_enhanced_dashboard.py
```

---

## 6. Data Acquisition

**Requirement:** *"Write code to download or fetch data from necessary sources. Ensure reproducible. Specify dependencies in requirements.txt."*

**Scripts:**

- `data/character_extraction.py` — Parses `0.Character traits - 50.pdf` and extracts all 50 character persona definitions into `characters.csv`
- `data/data_extraction.py` — Extracts passage text from the 9 book PDFs, pairs passages with personas, and generates synthetic interpretations into `interpretations.json` and `passages.csv`
- `data/remove_new_lines.py` — Cleans newline artefacts introduced during PDF text extraction
- `data_pipeline/scripts/data_acquisition.py` — Pipeline-stage wrapper that calls the above in sequence, validates all expected outputs exist, and logs results

All 9 source PDFs are committed to `data_pipeline/data/raw/pdfs/` so acquisition runs identically on any machine with no external dependencies beyond `requirements.txt`.

---

## 7. Data Preprocessing

**Requirement:** *"Clear steps for data cleaning, transformation, and feature engineering. Modular and reusable."*

**Scripts:** `data_pipeline/scripts/preprocessor.py` · `data_pipeline/preprocessing/pipeline/preprocessor.py`

Each step below is an independent, reusable function — nothing is bundled together. Any step can be adjusted or replaced without affecting others. All thresholds are in `config/preprocessing_config.yaml`, not hardcoded.

| Step | What It Does |
|---|---|
| Whitespace normalisation | Strips leading/trailing whitespace; collapses internal multiple spaces |
| Null handling | Null required fields → record removed and logged; null optional fields → retained |
| Length enforcement | Interpretations below minimum threshold flagged and excluded from ML matching |
| Voice preservation | No stemming, lemmatisation, or stop-word removal — user voice is the matching signal |
| Encoding normalisation | All text normalised to UTF-8; special characters standardised |
| Duplicate removal | Exact-duplicate interpretations per persona detected and removed |

**Outputs:** `data_pipeline/data/processed/books_processed.json` · `moments_processed.json` · `users_processed.json`

---

## 8. Feature Engineering

**Script:** `data_pipeline/scripts/feature_engineering.py`

| Feature | Method |
|---|---|
| Interpretation length | Character count and word count per interpretation |
| Thematic tags | Keyword matching against predefined theme vocabulary (isolation, ambition, identity, class, morality, etc.) |
| Emotional tone | Rule-based classification (melancholy, optimistic, critical, reflective, etc.) |
| Reading style encoding | 5 reading style categories mapped to integer codes |
| Demographic encoding | Age group, gender, occupation encoded as categorical features |

All features are appended to existing records — original text is always preserved.

---

## 9. Schema & Statistics Generation — TFDV

**Requirement:** *"Automate schema and statistics generation using MLMD, TFDV, or similar. Validate schema and data quality over time."*
**Evaluation Criterion 7:** *"Tools like Great Expectations or TFDV."*

**Tool: [TensorFlow Data Validation (TFDV)](https://www.tensorflow.org/tfx/data_validation/get_started)**

**Scripts:** `data_pipeline/scripts/generate_schema_stats.py` · `generate_html_report.py` · `generate_enhanced_dashboard.py`
**Schema:** `data_pipeline/config/schema.yaml`
**Outputs:** `data/reports/schema_stats.json` · `data/reports/validation_report.json` · HTML report · Dashboard

### What TFDV Does in This Pipeline

1. Infers schema from the dataset (field types, value ranges, distributions)
2. Validates every record against the schema in `config/schema.yaml`
3. Generates statistics: null rates, value distributions, length distributions, categorical frequencies
4. Writes `schema_stats.json` and `validation_report.json`
5. Flags any records or fields that violate the expected schema

### Schema Definition (`config/schema.yaml`)

```yaml
persona_id:      {type: string, required: true}
age_group:       {type: string, required: true, allowed: [18-25, 26-35, 36-50, 51-65, 65+]}
gender:          {type: string, required: true}
reading_style:   {type: string, required: true}
book_title:      {type: string, required: true}
passage_id:      {type: string, required: true}
interpretation:  {type: string, required: true, min_length: 50}
emotional_tone:  {type: string, required: false}
thematic_tags:   {type: array,  required: false}
timestamp:       {type: string, format: ISO8601, required: false}
```

`generate_html_report.py` renders results into human-readable HTML.
`generate_enhanced_dashboard.py` produces a full dashboard with distribution plots and demographic breakdowns.

---

## 10. Anomaly Detection & Alert Generation

**Requirement:** *"Detect missing values, outliers, invalid formats. Pipeline triggers an alert (e.g., email, Slack)."*
**Evaluation Criterion 8:** *"Detect anomalies and generate alerts. Handle missing values, outliers, schema violations."*

**Scripts:** `data_pipeline/scripts/anomalies.py` · `data_pipeline/preprocessing/pipeline/anomalies.py`

The anomaly detection module runs on the **full batch of 450 records** after preprocessing — it needs all records together to establish statistical baselines before flagging outliers.

### Detection Methods

| Anomaly | Method | Detail |
|---|---|---|
| Word count outlier | **IQR bounds** | `lower = Q1 − multiplier × IQR`, `upper = Q3 + multiplier × IQR`. Flags `word_count_outlier = True` |
| Readability outlier | **Z-score** | Flags if `|z| > threshold` from the mean readability score across all records |
| Near-duplicate | **TF-IDF cosine similarity** (scikit-learn `TfidfVectorizer`, `cosine_similarity`) | Pairs exceeding the similarity threshold are flagged as `duplicate_risk` |
| Style mismatch | **Rule-based** | NEW READER writing complex text, or well-read reader writing very simple text — flagged as `style_mismatch` |
| Schema violations | **Type and enum validation** | Any field violating `schema.yaml` types or allowed values — pipeline halts |
| Missing required fields | **Null check** | Any null in a required field — pipeline halts |

### Alert Generation

When anomalies are detected the pipeline generates alerts through two channels:

**Channel 1 — `data_pipeline/data/reports/notification.txt`**
A persistent alert file written at the end of anomaly detection. Contains the full anomaly summary: counts per type, affected record IDs, anomaly details, and timestamps. This file exists outside Airflow and can be reviewed at any time — it is the durable alert record.

```
ANOMALY REPORT - 2025-02-15 14:32:06
=====================================
word_count_outliers  : 3
readability_outliers : 5
duplicate_risk       : 0
style_mismatches     : 2
---
[WARNING] record_id=F_042: readability_high score=85.2, z=3.1
[WARNING] record_id=P_017: word_count_low 28 words (below lower bound 45.2)
```

**Channel 2 — Python `logging` + Airflow task failure email**
Every anomaly is logged at `WARNING` level immediately when detected, with full details. For pipeline-halting anomalies (missing required fields, schema violations), the script raises an exception that causes the Airflow task to fail — automatically triggering Airflow's built-in email notification to the configured address. This is the real-time alert channel.

The alert architecture uses Python's `logging` module with a file handler for `pipeline.log` and a stream handler for Airflow's task logs. It can be extended to send email or Slack notifications by adding an `SMTPHandler` or HTTP handler in `config.yaml` without changing any pipeline code.

### Output per Record

Each record receives an `anomalies` field:

```json
{
  "anomalies": {
    "word_count_outlier": false,
    "readability_outlier": true,
    "duplicate_risk": false,
    "duplicate_of": null,
    "style_mismatch": false,
    "anomaly_details": ["readability_high: score=85.2, z=3.1"]
  }
}
```

---

## 11. Bias Detection & Mitigation

**Requirement:** *"Use tools such as SliceFinder, TFMA, or Fairlearn. Document bias found, how addressed, and trade-offs."*
**Evaluation Criterion 9:** *"Detect and mitigate bias through data slicing. Model performs equitably across subgroups."*

**Scripts:** `data_pipeline/scripts/bias_detection.py` · `bias_detection/bias_detection.py`
**Tests:** `data_pipeline/tests/test_bias_detection.py` · `bias_detection/test_bias_detection.py`
**Report:** `data_pipeline/data/reports/bias_report_FINAL.md`

### Approach

Bias detection is implemented using **custom pandas data slicing** — `value_counts()`, `crosstab()`, and `groupby()` — applied across all demographic subgroups. This approach implements the same statistical methodology as Fairlearn and TFMA: slice the data, compute per-slice metrics, compare slices against each other and against the overall mean, and flag any slice where deviation exceeds the threshold.

The reason for using pandas directly rather than Fairlearn or TFMA: our dataset is synthetic and fully controlled (450 records, 50 personas), and custom slicing gives us complete visibility into every metric and comparison. The statistical outcomes are identical to what those tools would produce on this data structure.

### Slices Analysed

| Slice | Method | Threshold |
|---|---|---|
| Age group (18-24 Gen Z, 25-34 Millennial, 35-44 Gen X/Mill, 45+ Gen X/Boom) | `value_counts()` → % deviation from equal distribution | > 10% deviation |
| Gender | `value_counts()` → % deviation | > 10% deviation |
| Reader Type (`Distribution_Category`) | `value_counts()` → % deviation | > 10% deviation |
| Personality | `value_counts()` → % deviation | > 10% deviation |
| Book distribution | `value_counts()` → count per book | Expect 150 each |
| Character representation | Count per character name | Expect 9 each |
| Interpretation length by Age | `groupby('age_group')['word_count'].mean()` | < 20% variance across groups |
| Interpretation length by Gender | `groupby('Gender')['word_count'].mean()` | < 20% variance |
| Interpretation length by Personality | `groupby('Personality')['word_count'].mean()` | Expected variance (documented) |

### Cross-tabulations

- Age × Book — all age groups reading all books equally?
- Gender × Book — any gender concentrated on a specific book?
- Personality × Book — any personality over-represented per book?

### Results

| Dimension | Deviation | Status |
|---|---|---|
| Age group | > 10% | Intentional — documented below |
| Gender | < 10% | ✅ Balanced |
| Reader Type | < 10% | ✅ Balanced |
| Personality | < 10% | ✅ Balanced |
| Book distribution | 150 each | ✅ Perfect |
| Character representation | 9 each for all 50 | ✅ Perfect |
| Age × interpretation length | < 20% variance | ✅ No age-length bias |
| Gender × book | Even | ✅ No gender-genre bias |

**Verdict: APPROVED — dataset ready for preprocessing.**

### Bias Mitigation & Trade-offs

As required by the assignment (*"document whether any trade-offs were made in terms of overall performance"*):

| Bias Dimension | Decision | Justification | Trade-off |
|---|---|---|---|
| Age distribution (> 10% deviation) | **No mitigation — intentional design** | Young adults (18-34) represent 65-70% of digital readers in the real world. Our dataset reflects this at 70% (Millennials 44%). Forcing equal distribution across age groups would produce training data that does not reflect real-world user demographics, making the matching model less useful in production. | The model trained on this data will reflect real reading demographics. If deployed to a platform with an unusual age distribution, this could be rebalanced. We accept this trade-off in favour of realism. |
| Personality vs interpretation length | **No mitigation — expected behaviour** | Analytical personas writing longer interpretations is not bias — it is accurate. Equalising interpretation length across personality types would corrupt the authentic signal the ML model uses for compatibility matching. | Analytical personas have more influence on embedding space. This is a deliberate product decision: analytical readers self-select for deeper engagement, and the matching model should recognise this. |

Full findings, all cross-tabulations, per-slice statistics, and iteration history are in `data_pipeline/data/reports/bias_report_FINAL.md`.

---

## 12. Airflow DAGs & Gantt Optimization

**Requirement:** *"Structure pipeline using Airflow DAGs, logical connections between tasks, entire workflow from download to final outputs."*
**Requirement:** *"Use Airflow's Gantt chart to identify bottlenecks. Optimize by parallelizing."*

Both DAGs live in `data_pipeline/dags/`.

### `data_pipeline_dag.py` — Main Pipeline DAG

```python
# Task dependency chain
acquire >> preprocess >> feature_engineer >> validate
validate >> [generate_schema_stats, anomaly_detection]   # parallel
[generate_schema_stats, anomaly_detection] >> bias_detection
bias_detection >> generate_reports >> dvc_version
```

Configured with daily schedule (`@daily`), 2 retries with 3-minute delay, and Airflow email notification on task failure.

### `tests_dag.py` — Tests DAG

Runs the full `pytest` suite as a scheduled Airflow task after every pipeline execution. Regressions are caught automatically.

### Gantt Chart — Bottleneck Found and Fixed

**How to view:** Airflow UI → DAGs → `moment_data_pipeline` → **Gantt tab**

**Bottleneck found:** In the initial sequential DAG, `generate_schema_stats` and `anomaly_detection` were running one after the other despite having no dependency on each other — both only needed the validated data output. The Gantt chart made this idle dead time clearly visible as a gap between the two tasks.

**Fix applied:** Both tasks set to run in parallel using Airflow's list notation `[task_a, task_b]`. `bias_detection` waits for both to complete before running.

**Result:** Duration of the combined block reduced from the **sum** of both task durations to the **maximum** of both — a measurable improvement with no change to output or correctness.

---

## 13. Data Versioning with DVC

**Requirement:** *"Use DVC to track and version data. Include .dvc files. Git tracks code and configs."*
**Evaluation Criterion 5:** *"Data versioned, history maintained alongside code in Git."*

DVC tracks data files independently of Git. Code and configs live in Git; data lives in DVC remote storage.

> **The `.dvc/` folder and all `.dvc` pointer files are committed to Git.** This is how Git knows which version of the data corresponds to which version of the code — without storing large data files in Git itself. Anyone who clones the repo can run `dvc pull` to get the exact data version that matches the current commit.

### What DVC Tracks

| File / Directory | Why Versioned |
|---|---|
| `data_pipeline/data/raw/csvs_jsons/all_interpretations_450_FINAL_NO_BIAS.json` | Core dataset — evolved through multiple bias analysis iterations |
| `data_pipeline/data/processed/` | Preprocessed outputs |
| `data_pipeline/data/reports/` | Every run's reports preserved for comparison |

### Commands

```bash
dvc status          # what has changed vs last tracked version
dvc repro           # reproduce full pipeline from dvc.yaml
dvc dag             # visualise DVC pipeline
dvc push            # push data to remote storage
dvc pull            # restore data from remote
dvc diff            # compare current state to last commit

# View dataset version history
git log --oneline data_pipeline/data/raw/csvs_jsons/all_interpretations_450_FINAL_NO_BIAS.json.dvc
```

---

## 14. Error Handling

**Requirement:** *"Implement error handling for data unavailability, file corruption. Logs provide sufficient information for troubleshooting."*
**Evaluation Criterion 12:** *"Robust error handling for potential failure points."*

All scripts implement explicit `try/except` blocks for every failure point.

### Patterns Used

**Missing input file:**
```python
try:
    with open(config["input_path"], "r") as f:
        data = json.load(f)
except FileNotFoundError as e:
    logger.critical(f"Input file not found: {e}. Pipeline cannot continue.")
    raise
except json.JSONDecodeError as e:
    logger.critical(f"Input file is corrupt or invalid JSON: {e}.")
    raise
```

**Graceful degradation — non-critical failure:**
```python
# From anomalies.py: TF-IDF failure does not stop the pipeline
try:
    matrix = vectorizer.fit_transform(texts)
    return matrix, vectorizer
except Exception as e:
    logger.warning(f"TF-IDF build failed: {e}. Duplicate detection skipped.")
    return None, None   # pipeline continues without duplicate check
```

**Schema violation — pipeline halt:**
```python
if not schema_valid:
    logger.critical("Schema validation failed. See validation_report.json.")
    raise ValueError("Schema violation — pipeline halted.")
```

### Failure Behaviour by Stage

| Stage | Failure Type | Behaviour |
|---|---|---|
| Data Acquisition | File not found / corrupt PDF | `CRITICAL` log + pipeline halts |
| Preprocessing | Unexpected null | `WARNING` log + record excluded + continues |
| Validation | Schema violation | `CRITICAL` log + pipeline halts + Airflow retry |
| Anomaly Detection | TF-IDF build failure | `WARNING` log + duplicate check skipped + continues |
| Bias Detection | Empty slice | `WARNING` log + slice skipped + report generated |
| DVC Versioning | Remote unreachable | `ERROR` log + local cache used |

Airflow's retry mechanism (2 retries, 3-minute delay) handles transient failures automatically.

---

## 15. Logging

**Requirement:** *"Python's logging library or Airflow built-in. Set up monitoring for anomalies and alerts when errors are detected."*
**Evaluation Criterion 4:** *"Proper tracking of tasks, logging throughout pipeline, error alerts for anomalies."*

Every pipeline script uses Python's `logging` module. Logs write to both stdout (visible in Airflow task logs in real time) and `data_pipeline/logs/pipeline.log` (persistent file for offline review).

### Log Format

```
[2025-02-15 14:32:01] [INFO]     [data_acquisition]  Loaded 450 records from raw dataset
[2025-02-15 14:32:03] [INFO]     [preprocessor]      Stripped whitespace from 12 records
[2025-02-15 14:32:05] [WARNING]  [anomalies]         readability_high: score=85.2, z=3.1 — flagged
[2025-02-15 14:32:06] [INFO]     [anomalies]         word_count_outliers=3, readability_outliers=5, duplicates=0, style_mismatches=2
[2025-02-15 14:32:07] [INFO]     [bias_detection]    Gender: BALANCED (< 10% deviation)
[2025-02-15 14:32:08] [INFO]     [bias_detection]    Books: PERFECT (150 each)
[2025-02-15 14:32:10] [INFO]     [pipeline]          All stages completed successfully
```

### Log Levels

| Level | Used For |
|---|---|
| `INFO` | Normal progress — stage start/complete, record counts, bias results |
| `WARNING` | Non-blocking issues — anomaly flags, skipped checks |
| `ERROR` | Recoverable failures — Airflow retry triggered |
| `CRITICAL` | Pipeline-halting failures — missing file, schema violation, corrupt data |

---

## 16. Testing

**Requirement:** *"Unit tests for each component. pytest or unittest. Test edge cases, missing values, possible anomalies."*
**Evaluation Criterion 10:** *"Unit tests for each key component, particularly preprocessing and transformation. Edge cases."*

Tests use `pytest`. Root `conftest.py` provides shared fixtures (file paths, sample records, schema) reused across all test modules.

### Run All Tests

```bash
pytest data_pipeline/tests/ -v
```

### Run with Coverage

```bash
pytest data_pipeline/tests/ --cov=data_pipeline/scripts --cov-report=term-missing
```

### Run Specific Modules

```bash
pytest data_pipeline/tests/test_bias_detection.py -v
pytest data_pipeline/preprocessing/test_pipeline.py -v
pytest bias_detection/test_bias_detection.py -v
```

### Test Coverage — Normal, Edge, and Error Cases

| Test File | Script Tested | Normal Cases | Edge Cases | Error Cases |
|---|---|---|---|---|
| `test_acquisition.py` | `data_acquisition.py` | 450 records, all fields present, output files exist | Empty PDF, single record | Missing input → `FileNotFoundError` |
| `test_preprocessing.py` | `preprocessor.py` | Whitespace stripped, duplicates removed, length filter | All-null record, zero-length interpretation, unicode | Malformed input → graceful skip + log |
| `test_validation.py` | `validation.py` | Required fields present, types correct, enums valid | Single missing field, wrong type | Schema file missing → `FileNotFoundError` |
| `test_schema_stats.py` | `generate_schema_stats.py` | Output JSON exists, all fields have stats | 100% null optional field | Empty dataset → zero-count stats |
| `test_bias_detection.py` | `bias_detection.py` | Gender < 10%, books = 150 each, characters = 9 each | Single-persona dataset, all same age group | Empty slice → skipped + warning |
| `test_pipeline.py` | `run.py` | Full pipeline completes, all outputs exist, idempotent | Pipeline with 1 record | Simulated stage failure → partial outputs + error log |

### Tests DAG

`tests_dag.py` schedules the full pytest suite as an Airflow task after every pipeline run — no manual test execution needed.

---

## 17. CI/CD Workflow

**File:** `.github/workflows/config.yaml`

GitHub Actions runs the full test suite on every push and every pull request to `main`. No code reaches `main` without passing all tests.

```yaml
on:
  push:
    branches: ["*"]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - run: pip install -r requirements.txt
      - run: pytest data_pipeline/tests/ -v
```

---

## 18. Code Style & Standards

**Requirement:** *"Modular programming practices. PEP 8. Clarity, modularity, and maintainability."*

All Python code follows **PEP 8**:

- 4-space indentation
- Maximum line length of 79 characters
- Snake_case for variables/functions; PascalCase for classes
- Docstrings on all public functions and modules
- Imports ordered: standard library → third-party → local
- No unused imports or variables

Each script in `data_pipeline/scripts/` handles exactly one pipeline stage and can run independently or as part of the full pipeline. All configuration is in YAML files — nothing hardcoded. This follows the same modular design as [scikit-learn](https://github.com/scikit-learn/scikit-learn).

---

## 19. Reproducibility — Run on Any Machine

**Requirement:** *"Anyone should be able to clone the repository, install dependencies, and run the pipeline without errors."*

All source PDFs and raw files are committed to the repository. No manual data preparation needed.

### Zero to Running — No Docker

```bash
# 1. Clone
git clone https://github.com/jyothssena/Moment.git
cd Moment

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Confirm tests pass
pytest data_pipeline/tests/ -v

# 5. Run pipeline
python data_pipeline/scripts/run.py
```

### With Airflow

```bash
# After steps 1-3 above:
docker-compose up airflow-init   # first time only
docker-compose up -d
docker-compose ps                # confirm healthy

# http://localhost:8080 | airflow / airflow
# Toggle moment_data_pipeline ON → Trigger DAG
# Graph View = progress | Gantt = timing

docker-compose down
```

### With DVC

```bash
dvc pull     # fetch data matching current Git commit
# If no remote: python data_pipeline/scripts/run.py
```

### Expected Outputs

| Output | Location |
|---|---|
| Preprocessed records | `data_pipeline/data/processed/` |
| Schema statistics | `data_pipeline/data/reports/schema_stats.json` |
| Validation report | `data_pipeline/data/reports/validation_report.json` |
| Bias report + trade-offs | `data_pipeline/data/reports/bias_report_FINAL.md` |
| Anomaly alert log | `data_pipeline/data/reports/notification.txt` |
| Full pipeline log | `data_pipeline/logs/pipeline.log` |

### Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate venv, re-run `pip install -r requirements.txt` |
| `pip install` errors | Delete `venv/`, recreate, reinstall |
| Docker not starting | Open Docker Desktop first, then `docker-compose up -d` |
| DAG not in Airflow UI | Wait 30s for scheduler to scan `dags/` folder |
| `dvc pull` fails | Run `python data_pipeline/scripts/run.py` to regenerate locally |
| Tests failing | Run `pytest data_pipeline/tests/ -v` to see which test and why |

---

## 20. Evaluation Criteria Coverage

| # | Criterion | How It Is Met | Key Files |
|---|---|---|---|
| 1 | Proper Documentation | Every stage documented in this README with code examples, diagrams, and output descriptions | `README.md`, docstrings in all scripts |
| 2 | Modular Syntax and Code | One script per stage, all config in YAML, each function independently testable | `data_pipeline/scripts/` |
| 3 | Pipeline Orchestration (Airflow) | Two DAGs with logical dependency chain, error handling, retry config, daily schedule | `dags/data_pipeline_dag.py`, `tests_dag.py` |
| 4 | Tracking and Logging | Python `logging` in every script, `pipeline.log`, Airflow task logs, `notification.txt` alerts | All scripts, `logs/pipeline.log` |
| 5 | Data Version Control (DVC) | `dvc.yaml` defines stages, `.dvc` pointer files committed to Git, full version history | `dvc.yaml`, `.dvc/` |
| 6 | Pipeline Flow Optimization | Gantt chart bottleneck found, parallel tasks implemented, runtime improvement documented | `data_pipeline_dag.py` |
| 7 | Schema and Statistics (TFDV) | TFDV validates every record against `schema.yaml`, generates `schema_stats.json` and `validation_report.json` | `generate_schema_stats.py` |
| 8 | Anomaly Detection & Alerts | IQR bounds, Z-score, TF-IDF cosine similarity, style mismatch; alerts via `notification.txt` + Airflow email | `anomalies.py`, `notification.txt` |
| 9 | Bias Detection & Mitigation | Custom pandas data slicing across 5 demographic dimensions, cross-tabulations, trade-offs documented | `bias_detection.py`, `bias_report_FINAL.md` |
| 10 | Test Modules | 6 test files covering normal cases, edge cases, and error cases for every pipeline stage | `data_pipeline/tests/` |
| 11 | Reproducibility | Step-by-step setup, run instructions for 4 options, expected outputs, troubleshooting table | Section 19 of this README |
| 12 | Error Handling and Logging | `try/except` in every script, `CRITICAL`/`ERROR` log levels, graceful degradation for non-critical failures | All scripts, Section 14 |

---

*DADS7305 / IE7305 — Machine Learning Operations · Group 23 · Northeastern University · February 2025*
