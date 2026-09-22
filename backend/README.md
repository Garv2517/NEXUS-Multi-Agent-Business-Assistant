# NEXUS Backend

FastAPI backend for the NEXUS AI-103 Multi-Agent Business Assistant.

The current backend includes:

- Azure AI Foundry `gpt-5-mini` Manager routing with deterministic local fallback
- Sales, Inventory, and People specialist agents
- Kaggle-backed read-only analytics
- deterministic Risk Management
- deterministic Forecasting & Demand Planning
- SQLite People Management and activity logging

For the complete architecture, setup commands, data-domain boundaries, and demo guidance, see the repository root `README.md`.

## Run

```powershell
.\.venv\Scripts\python.exe scripts\import_kaggle_dataset.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -W default
```

## Foundry modes

```env
ORCHESTRATION_MODE=local
```

uses deterministic routing only.

```env
ORCHESTRATION_MODE=foundry_manager
FOUNDRY_FALLBACK_TO_LOCAL=true
```

uses Azure AI Foundry for intent/workflow selection while keeping business calculations deterministic.
