# Recommendation Engine at Scale

## Problem
Recommend items to users from large interaction logs.

## Dataset and provenance

`data/raw/sample_interactions.csv` is synthetic. For a public benchmark, download [MovieLens](https://grouplens.org/datasets/movielens/) and follow GroupLens' usage terms. Keep larger downloads under ignored `data/external/`; do not commit raw interaction logs.

## Run the ELT demo

From this directory, run `python src/main.py`. It upserts interaction snapshots by `(user_id, item_id)`, computes item popularity in SQL, and materializes top-N unseen-item recommendations in SQLite. Stable keys and timestamp-aware upserts make repeated loads idempotent; database files are ignored. Configure `--top-n`; run checks with `python -m pytest -q tests`.

## Stack
PySpark, Spark MLlib, Parquet/Delta, FastAPI

## Architecture
- Bronze / raw ingestion layer
- Silver / cleaned and validated data layer
- Gold / feature or serving layer
- Monitoring / validation and retraining feedback loop

## DE tasks
1. Ingest raw data with versioned file naming and timestamps.
2. Build idempotent and incremental transformations.
3. Add data quality checks and freshness alerts.
4. Create a reproducible run order using a Makefile or run script.
5. Store outputs in a warehouse, lake, or streaming sink with clear contracts.

## DS tasks
1. Run EDA and validate assumptions about seasonality, drift, and user behavior.
2. Benchmark a baseline model before trying a stronger approach.
3. Use proper time-based splits and avoid leakage.
4. Log experiments, tuning choices and key metrics.
5. Report limitations and next steps in a production-focused way.

## Deliverables
- Reproducible pipeline or app
- Tests for transformation and validation logic
- Dashboard, API, or report showing outputs
- Clear business summary with measurable impact

## Recommended repository structure
`	ext
recommendation-engine-at-scale/
+-- README.md
+-- requirements.txt
+-- Makefile
+-- .gitignore
+-- src/
+-- tests/
+-- notebooks/
+-- docs/
`

## Resume line
Built a Spark-based recommender over large interaction data, improving ranking quality over a popularity baseline.
