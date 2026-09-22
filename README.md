# NEXUS Ã¢â‚¬â€ Multi-Agent Business Assistant

NEXUS is an AI-103 course project that combines Azure AI Foundry routing, deterministic specialist agents, verified business tools, SQLite analytics, risk analysis, and demand forecasting in one retail business workspace.

## Final Architecture

```text
User
  Ã¢â€ â€œ
React / Vite workspace
  Ã¢â€ â€œ
FastAPI backend
  Ã¢â€ â€œ
Azure AI Foundry gpt-5-mini Manager routing
  Ã¢â€ â€œ
Validated execution plan
  Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Sales Agent
  Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ Inventory Agent
  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ People Agent
        Ã¢â€ â€œ
Deterministic tools / services
        Ã¢â€ â€œ
SQLite
  Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ nexus_analytics.db  Ã¢â€ â€™ retail sales, inventory, performance, risk, forecasting
  Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ nexus.db            Ã¢â€ â€™ synthetic People Management + activity logs
```

The LLM does not invent business metrics. Foundry `gpt-5-mini` selects a validated intent/workflow; business values come from deterministic tools and SQLite queries.

## Main Capabilities

- **Overview** Ã¢â‚¬â€ unified retail KPIs, activity, and cross-domain shortcuts.
- **Assistant** Ã¢â‚¬â€ Foundry-powered natural-language routing with traceable multi-agent execution.
- **Sales** Ã¢â‚¬â€ Kaggle-backed USD sales analytics, monthly trend, categories, and top products.
- **Inventory** Ã¢â‚¬â€ Kaggle-backed stock snapshot, product placement counts, zero-stock exposure, and valuation.
- **People Management** Ã¢â‚¬â€ separate synthetic internal HR domain with 180 employees across 12 departments.
- **Business Performance** Ã¢â‚¬â€ cross-business performance analytics over the USA Toy Sales dataset.
- **Insights & Risk** Ã¢â‚¬â€ deterministic stockout exposure, inventory pressure, slow-moving exposure, velocity risk, and portfolio concentration.
- **Forecasting & Planning** Ã¢â‚¬â€ 4-week demand forecasting with walk-forward validation, per-series model selection, historical MAE references, and demand coverage metrics.
- **Activity** Ã¢â‚¬â€ real agent/tool execution log.
- **About** Ã¢â‚¬â€ architecture, lifecycle, responsible-AI guardrails, and roadmap.

## Data Domains

### Retail analytics domain

Source: **USA Toy Sales Dataset (Kaggle)**
Nature: synthetic retail business dataset
Currency: **USD**
Sales period: **JanÃ¢â‚¬â€œDec 2025**
Analytics database: `backend/data/nexus_analytics.db`

The raw source does not provide an inventory snapshot date. NEXUS uses **Dec 31, 2025 as an explicit analytical assumption** and exposes `snapshot_date_is_assumed = true`.

### People Management domain

The Kaggle dataset contains no employee data. People Management therefore remains a **separate synthetic internal HR domain** stored in `backend/data/nexus.db`.

## Azure AI Foundry

Runtime configuration supports:

```env
ORCHESTRATION_MODE=foundry_manager
FOUNDRY_FALLBACK_TO_LOCAL=true
FOUNDRY_MODEL=gpt-5-mini
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
```

Authentication uses `AzureCliCredential`, so local development requires an authorized Azure CLI session:

```powershell
az login
az account show
```

When Foundry mode is active, the Assistant health/status UI reports:

```text
Azure Foundry Routing Active Ã‚Â· gpt-5-mini
```

A successful Developer View trace contains metadata similar to:

```json
{
  "routing_source": "foundry",
  "model": "gpt-5-mini",
  "intent": "compound_sales_inventory"
}
```

## Setup

### 1. Backend

```powershell
cd "C:\Users\HP\OneDrive\Desktop\NEXUS\backend"

.\.venv\Scripts\python.exe scripts\import_kaggle_dataset.py

.\.venv\Scripts\python.exe -m uvicorn app.main:app `
  --host 127.0.0.1 `
  --port 8000 `
  --reload
```

Backend: `http://127.0.0.1:8000`

### 2. Frontend

```powershell
cd "C:\Users\HP\OneDrive\Desktop\NEXUS\frontend"

npm.cmd run dev
```

Frontend: `http://localhost:5173`

## Testing

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -W default
```

Frontend production build:

```powershell
cd frontend
npm.cmd run build
```

A Windows regression helper is also provided:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\final_regression.ps1
```

## Important API Groups

- `/api/health` Ã¢â‚¬â€ backend / Foundry configuration status
- `/api/chat` Ã¢â‚¬â€ multi-agent Assistant
- `/api/analytics/*` Ã¢â‚¬â€ read-only retail analytics
- `/api/risk/*` Ã¢â‚¬â€ deterministic risk management
- `/api/forecast/*` Ã¢â‚¬â€ deterministic forecasting / planning
- `/api/hr` Ã¢â‚¬â€ People Management
- `/api/activity` Ã¢â‚¬â€ execution audit log

Legacy `/api/sales`, `/api/inventory`, and `/api/dashboard` routes are retained for earlier regression compatibility. The final user-facing Overview, Sales, and Inventory pages use the unified analytics domain.

## Responsible-AI / Data Guardrails

- Foundry chooses a **validated workflow**, not arbitrary SQL or tool names.
- Business metrics come from deterministic tools and databases.
- Unsupported requests execute zero specialist business tools.
- No employee risk / attrition scoring is implemented.
- Risk thresholds are centralized and exposed through `/api/risk/config`.
- Forecasts are clearly labelled as model outputs, not known facts.
- Historical MAE references are not presented as statistical confidence intervals.
- No reorder levels are invented for the Kaggle inventory dataset.
- Synthetic dataset and inventory-date assumptions are disclosed in the UI.

## Repository Safety

Do not commit:

- `.env`
- Azure credentials / tokens
- `.venv`
- `node_modules`
- generated `nexus_analytics.db`

Raw Kaggle CSVs are retained so the analytics database can be rebuilt reproducibly with `scripts/import_kaggle_dataset.py`.

## Presentation

See:

- `docs/DEMO_SCRIPT.md`
- `docs/FINAL_CHECKLIST.md`
