# kitefs-examples

A end-to-end demo of KiteFS using a Turkish real-estate price recommendation scenario. It shows how a feature store fits into a real ML system: from feature definition and ingestion, through model training, to live serving.

## What this demo shows

A real-estate platform wants to recommend sale prices when a user creates a listing. KiteFS manages the feature lifecycle:

- Store historical listing and market features with validation.
- Retrieve point-in-time-correct training datasets without leaking future information.
- Materialize the latest market aggregates for low-latency online serving.

## Projects

| Project | Description |
| --- | --- |
| `training/` | Feature producer — defines feature groups, ingests prepared data, retrieves training datasets, and materializes online features. |
| `backend/` | Feature consumer — a FastAPI service that reads online features from KiteFS and returns price recommendations. |
| `frontend/` | React UI — collects listing attributes from the user and displays the recommended price returned by the backend. |

## Workflow

```
training/   →  define & ingest features  →  KiteFS (local → AWS)
training/   →  retrieve training data    →  train model
backend/    →  read online features      →  serve predictions
frontend/   →  send listing inputs       →  display recommendation
```

The three projects map to the three phases in the [KiteFS Getting Started guide](../kitefs/docs/Getting-Started-kitefs.md):

- **Phase 1** — `training/`: define feature groups, ingest data, build a training dataset, train the model, publish to AWS.
- **Phase 2** — `backend/` + `frontend/`: read online features from AWS, serve real-time price recommendations.
- **Phase 3** — `training/`: ingest new monthly data, refresh the online store, retrain on the rolling window.

## Prerequisites

- Python 3.12+
- Node.js 18+
- KiteFS installed
