# NEXUS â€” Multi-Agent Business Assistant

> **AI-103 academic proof of concept** combining Azure AI Foundry, GPT-5-mini, deterministic specialist agents, reproducible retail analytics, risk analysis, and demand forecasting in one full-stack business workspace.

NEXUS demonstrates a hybrid AI architecture in which a language model understands and routes natural-language requests, while trusted server-side agents and tools remain responsible for executing business logic and retrieving factual data.

> **Core principle:** GPT decides **which workflow is needed**; NEXUS deterministic tools decide **what the business facts are**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Key Capabilities](#key-capabilities)
- [System Architecture](#system-architecture)
- [How the Multi-Agent Assistant Works](#how-the-multi-agent-assistant-works)
- [Agents and Supported Intents](#agents-and-supported-intents)
- [Data Architecture](#data-architecture)
- [Dataset and Verified Metrics](#dataset-and-verified-metrics)
- [Business Analytics](#business-analytics)
- [Insights and Risk](#insights-and-risk)
- [Forecasting and Planning](#forecasting-and-planning)
- [People Management](#people-management)
- [Frontend Pages](#frontend-pages)
- [Backend APIs](#backend-apis)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Environment Configuration](#environment-configuration)
- [Installation and Running](#installation-and-running)
- [Testing](#testing)
- [Azure AI Foundry Verification](#azure-ai-foundry-verification)
- [Responsible AI and Security](#responsible-ai-and-security)
- [Known Limitations](#known-limitations)
- [Future Scope](#future-scope)
- [Demo Flow](#demo-flow)

---

## Project Overview

**NEXUS** is a full-stack multi-agent business intelligence assistant developed as an AI-103 course project.

The platform combines:

- **Azure AI Foundry** with a deployed `gpt-5-mini` model for natural-language intent routing.
- A **trusted server-side execution-plan layer** that validates model output before anything runs.
- **Sales, Inventory, and People/HR specialist agents**.
- **Deterministic business tools** for factual data retrieval.
- A reproducible **SQLite analytics database** generated from versioned Kaggle CSV files.
- **Business performance analytics** across products, categories, stores, and locations.
- **Deterministic risk analytics** for stockouts, inventory pressure, sales velocity, and concentration.
- **Four-week demand forecasting** with rolling-origin validation.
- A modern **React + Vite** dashboard.
- Full **agent/tool execution traces** for transparency and debugging.

The project intentionally separates **AI reasoning** from **business execution**. The LLM is not allowed to generate arbitrary SQL, choose unregistered tools, or invent numerical business metrics.

---

## Problem Statement

Business data is commonly distributed across separate systems for sales, inventory, workforce management, and analytics. Users often need to switch between dashboards and manually combine information before reaching a decision.

A general-purpose chatbot solves the interaction problem but introduces another risk: it can provide fluent answers that contain unsupported or hallucinated numbers.

NEXUS addresses both problems by combining:

1. **Natural-language interaction** through Azure AI Foundry.
2. **Controlled intent routing** through a validated intent taxonomy.
3. **Server-generated execution plans** rather than model-generated executable code.
4. **Deterministic specialist tools** for actual business values.
5. **Traceable multi-agent execution** visible in the UI.
6. Traditional dashboards for users who prefer visual analytics instead of chat.

---

## Key Capabilities

### Executive Overview

The Overview page provides a single management snapshot of the retail business, including sales, inventory, workforce summaries, and links to deeper modules.

### Multi-Agent Assistant

Users can ask business questions in natural language, for example:

```text
Can you figure out which three products generated the highest sales and compare each one's current inventory?
```

A compound request can execute this workflow:

```text
Azure AI Foundry / gpt-5-mini
        â†“
compound_sales_inventory
        â†“
Sales Agent
        â†“
get_top_products()
        â†“
product IDs passed as context
        â†“
Inventory Agent
        â†“
get_product_stock() Ã— 3
        â†“
verified response
```

### Sales Analytics

- Total revenue
- Units sold
- Transaction count
- Gross profit
- Gross margin
- Monthly trends
- Category performance
- Product performance
- Top-selling products
- Store performance
- Location performance

Retail monetary values are presented in **USD**.

### Inventory Analytics

- Total units on hand
- Store-product placement counts
- Zero-stock placements
- In-stock placements
- Stockout rate
- Inventory cost value
- Inventory retail value
- Product-level stock views
- Inventory pressure analysis

The source dataset does **not** contain reorder levels, so NEXUS does not invent them.

### Business Performance

A dedicated analytics view combines revenue, profitability, margin, products, categories, stores, locations, and inventory valuation.

### Insights & Risk

Risk signals are deterministic and remain separate instead of being collapsed into a single opaque score:

- Stockout exposure
- Inventory pressure
- Slow-moving candidates
- Sales velocity changes
- Internal revenue concentration

### Forecasting & Planning

- Four-week unit forecasts
- Four-week revenue forecasts
- Category-level forecasts
- Historical validation metrics
- Reliability labels based on validation WAPE
- Demand coverage ratios
- Forecast coverage in weeks

### People Management

A separate synthetic internal domain provides:

- 180 employees
- 12 departments
- Leave information
- Employee directory
- HR policies
- Open employee requests

---

## System Architecture

```text
User / Browser
      â†“
React + Vite Frontend
      â†“ HTTP / JSON
FastAPI Backend
      â†“
ChatService / Manager Agent
      â†“
Azure AI Foundry â€” gpt-5-mini
      â†“
Validated Intent
      â†“
Trusted Server Execution Plan
      â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Sales Agent â”‚ Inventory Agent â”‚ People Agent â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“
Deterministic Verified Tools
      â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ nexus_analytics.db     â”‚ nexus.db             â”‚
â”‚ Retail analytics      â”‚ People + activity    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“
Verified Response + Agent Trace
```

The Manager does not directly execute arbitrary model output. The model selects from a controlled intent schema, and the backend converts that selection into a trusted execution plan.

---

## How the Multi-Agent Assistant Works

### 1. User request

The frontend sends a natural-language request to:

```text
POST /api/chat
```

### 2. Manager routing

With Foundry enabled:

```env
ORCHESTRATION_MODE=foundry_manager
```

NEXUS sends the routing request to the configured Azure AI Foundry deployment.

### 3. Structured model decision

The model returns a constrained routing decision such as:

```json
{
  "intent": "compound_sales_inventory",
  "limit": 3
}
```

The model does **not** return arbitrary SQL or executable Python.

### 4. Trusted execution plan

The backend maps the validated intent to known operations, for example:

```text
Step 1 â†’ Sales Agent â†’ get_top_products
Step 2 â†’ Inventory Agent â†’ get_product_stock
```

### 5. Agent-to-agent context passing

For compound requests, the Manager can pass outputs from one specialist to another. In the verified sales/inventory example, product IDs from the Sales Agent are passed to the Inventory Agent.

### 6. Final response

The response is assembled from deterministic tool outputs. Business facts come from SQLite-backed services, not from model memory.

---

## Agents and Supported Intents

| Agent | Responsibility | Main data domain |
|---|---|---|
| Manager Agent | Understand request, validate route, orchestrate specialists | Routing/orchestration |
| Sales Agent | Revenue, units, monthly sales, top products, trends | `nexus_analytics.db` |
| Inventory Agent | Product stock, stockouts, inventory summaries, pressure | `nexus_analytics.db` |
| HR / People Agent | Employee summary, employee lookup, HR policies | `nexus.db` |

Supported intent families include:

```text
sales_total
sales_monthly
sales_top_products
sales_trend
inventory_product_stock
inventory_low_stock
inventory_summary
hr_summary
hr_employee
hr_policy
hr_policies
compound_sales_inventory
business_overview
unsupported
```

Out-of-domain questions such as weather are classified as `unsupported` and execute zero specialist business tools.

---

## Data Architecture

NEXUS intentionally uses **two separate data domains**.

### Retail analytics domain

```text
backend/data/nexus_analytics.db
```

Used by:

- Overview
- Sales
- Inventory
- Business Performance
- Insights & Risk
- Forecasting
- Sales/Inventory Assistant tools

This database is generated from raw CSV files and should not be committed.

### Internal operational domain

```text
backend/data/nexus.db
```

Used by:

- People Management
- HR policies
- Activity logs
- Operational compatibility data

Keeping these domains separate preserves data provenance because the Kaggle retail dataset contains no employee records.

---

## Dataset and Verified Metrics

NEXUS uses the **USA Toy Sales Dataset** from Kaggle as a synthetic/fictitious retail dataset for academic analysis.

Source:

```text
https://www.kaggle.com/datasets/intrudershanky/usa-toy-sales-dataset
```

Raw files:

```text
stores.csv
products.csv
inventory.csv
sales.csv
```

Verified ingestion totals:

| Metric | Value |
|---|---:|
| Stores | 120 |
| Products | 180 |
| Inventory placements | 14,143 |
| Sales transactions | 245,800 |
| Units sold | 567,270 |
| Sales period | Janâ€“Dec 2025 |
| Revenue | $9,862,933.25 |
| COGS | $5,556,827.27 |
| Gross profit | $4,306,105.98 |
| Gross margin | 43.66% |
| Current inventory units | 338,993 |
| Zero-stock placements | 321 |
| Categories | 16 |
| Foreign-key violations after import | 0 |

### Reproducible ingestion

The importer is located at:

```text
backend/scripts/import_kaggle_dataset.py
```

It validates source files, expected row counts, checksums, primary/foreign keys, financial totals, and database integrity before atomically promoting the generated analytics database.

Money is stored internally as **integer cents** to avoid floating-point accounting errors.

### Inventory snapshot assumption

The source inventory file does not provide a date. NEXUS explicitly assumes:

```text
Inventory snapshot date: 2025-12-31
snapshot_date_is_assumed: true
```

This assumption is disclosed in the API/UI rather than hidden.

---

## Business Analytics

The analytics layer follows a read-only repository/service design:

```text
API â†’ AnalyticsService â†’ AnalyticsRepository â†’ nexus_analytics.db
```

Available analytics include:

- Company summary
- Monthly performance
- Category performance
- Product performance
- Store performance
- Location performance
- Inventory summary
- Product inventory

The analytics database is opened in read-only mode for analytical services.

---

## Insights and Risk

Risk logic is deterministic and empirically calibrated to the project dataset.

### Days of Supply

```text
annual_daily_velocity = total_2025_units / 365
days_of_supply = current_stock / annual_daily_velocity
```

Placement coverage tiers:

| Tier | Rule |
|---|---|
| Stockout | stock = 0 or DOS = 0 |
| High Pressure | 0 < DOS â‰¤ 130.87 |
| Moderate Pressure | 130.87 < DOS â‰¤ 171.76 |
| Typical | 171.76 < DOS â‰¤ 298.64 |
| Elevated Coverage | 298.64 < DOS â‰¤ 392.04 |
| Slow-Moving Candidate | DOS > 392.04 |

Material slow-moving placement logic also requires meaningful inventory capital exposure.

### Sales velocity

NEXUS compares two 28-day windows near the end of 2025 and classifies eligible products using deterministic percentile-derived thresholds.

### Concentration

HHI-style metrics describe **internal portfolio revenue concentration** across products, categories, and stores. They are not presented as legal or regulatory market-concentration findings.

### No unified risk score

Stockout, inventory pressure, slow-moving inventory, velocity, and concentration remain independent analytical domains so the evidence behind each signal stays inspectable.

---

## Forecasting and Planning

Forecasting is implemented deterministically in Python.

### Weekly preparation

Daily 2025 sales are aggregated into Monday-start weekly buckets. Partial boundary weeks are tracked explicitly, while **51 complete weeks** are used for clean validation/training.

### Forecast horizon

```text
4 weeks
```

### Candidate models

```text
Naive
MA4
MA8
OLS trend
SES
```

### Validation

NEXUS uses **rolling-origin time-series validation**, not a random train/test split.

Primary selection metric:

```text
Aggregate H1â€“H4 WAPE
```

Project-defined reliability bands:

```text
Strong   â†’ WAPE â‰¤ 0.10
Moderate â†’ 0.10 < WAPE â‰¤ 0.20
Limited  â†’ WAPE > 0.20
```

These labels are project reliability bands, **not statistical confidence intervals**.

### Demand coverage

```text
coverage_ratio = current_stock_units / forecast_4w_units
forecast_coverage_weeks = current_stock_units / (forecast_4w_units / 4)
```

NEXUS does not turn these values into automatic purchase orders because supplier lead time, safety stock policy, and procurement constraints are absent from the dataset.

---

## People Management

People Management is a deterministic synthetic internal domain stored in `nexus.db`.

Current demo scale:

| Metric | Value |
|---|---:|
| Employees | 180 |
| Departments | 12 |
| Employees on leave | 17 |
| Open requests | 27 |

No employee risk scoring, attrition prediction, personnel ranking, or automated employment decisions are implemented.

---

## Frontend Pages

| Route | Page | Purpose |
|---|---|---|
| `/` | Overview | Executive business snapshot |
| `/assistant` | Assistant | Multi-agent natural-language workspace |
| `/sales` | Sales | Sales metrics and trends |
| `/inventory` | Inventory | Inventory snapshot and stock analysis |
| `/hr` | People Management | Workforce and policy views |
| `/performance` | Business Performance | Detailed retail analytics |
| `/risk` | Insights & Risk | Deterministic risk analytics |
| `/forecast` | Forecasting & Planning | Forecasts and demand coverage |
| `/activity` | Activity | Agent/tool execution history |
| `/about` | About Nexus | Architecture, guardrails, roadmap |

---

## Backend APIs

FastAPI documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

Important API groups:

```text
GET  /api/health
POST /api/chat

GET  /api/analytics/*
GET  /api/risk/*
GET  /api/forecast/*
GET  /api/hr
GET  /api/activity
```

Legacy sales/inventory/dashboard routes remain for regression compatibility, while final user-facing retail pages use the unified analytics domain.

---

## Technology Stack

### Frontend

- React
- Vite
- React Router
- Tailwind CSS
- Recharts
- Framer Motion
- Lucide React
- Inter font

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLite
- Pytest
- HTTPX

### Azure / AI

- Azure AI Foundry
- GPT-5-mini
- Azure CLI authentication
- `AzureCliCredential`
- Structured routing outputs

### Data

- Kaggle USA Toy Sales CSVs
- Reproducible SQLite ingestion
- Integer-cent monetary storage
- Read-only analytics repositories

---

## Repository Structure

```text
NEXUS/
â”œâ”€â”€ README.md
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ DEMO_SCRIPT.md
â”‚   â””â”€â”€ FINAL_CHECKLIST.md
â”œâ”€â”€ scripts/
â”‚   â””â”€â”€ final_regression.ps1
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ .env.example
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ agents/
â”‚   â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ orchestration/
â”‚   â”‚   â”œâ”€â”€ repositories/
â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â””â”€â”€ tools/
â”‚   â”œâ”€â”€ data/
â”‚   â”‚   â”œâ”€â”€ nexus.db
â”‚   â”‚   â””â”€â”€ external/usa_toy_sales/raw/
â”‚   â”œâ”€â”€ scripts/
â”‚   â”‚   â”œâ”€â”€ import_kaggle_dataset.py
â”‚   â”‚   â””â”€â”€ d3a*_forecast_*.py
â”‚   â””â”€â”€ tests/
â””â”€â”€ frontend/
    â”œâ”€â”€ package.json
    â””â”€â”€ src/
        â”œâ”€â”€ components/
        â”œâ”€â”€ pages/
        â””â”€â”€ services/
```

Generated folders, credentials, virtual environments, and `nexus_analytics.db` are intentionally excluded from version control.

---

## Environment Configuration

Create:

```text
backend/.env
```

Example:

```env
APP_NAME=Nexus API
APP_ENV=development
FRONTEND_ORIGIN=http://localhost:5173

DATABASE_PATH=data/nexus.db
ANALYTICS_DATABASE_PATH=data/nexus_analytics.db

FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_MODEL=gpt-5-mini
ORCHESTRATION_MODE=foundry_manager
FOUNDRY_FALLBACK_TO_LOCAL=true
FOUNDRY_ROUTING_TIMEOUT_SECONDS=15
```

Do **not** commit `.env`.

### Orchestration modes

Local deterministic routing:

```env
ORCHESTRATION_MODE=local
```

Azure Foundry routing:

```env
ORCHESTRATION_MODE=foundry_manager
```

For a resilient live demo:

```env
FOUNDRY_FALLBACK_TO_LOCAL=true
```

For strict Foundry verification:

```env
FOUNDRY_FALLBACK_TO_LOCAL=false
```

---

## Installation and Running

### 1. Clone

```powershell
git clone https://github.com/Garv2517/NEXUS-Multi-Agent-Business-Assistant.git
cd NEXUS-Multi-Agent-Business-Assistant
```

### 2. Backend environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment

Create `backend/.env` using `.env.example` as a reference.

For live Foundry routing:

```powershell
az login
az account show
```

### 4. Build analytics database

From `backend`:

```powershell
.\.venv\Scripts\python.exe scripts\import_kaggle_dataset.py
```

### 5. Start backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### 6. Start frontend

In another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Testing

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -W default
```

Frontend production build:

```powershell
cd frontend
npm.cmd run build
```

Full Windows regression from repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\final_regression.ps1
```

Final validated release state:

```text
Analytics ingestion: PASS
Foreign-key integrity: PASS
Backend tests: 184 passed
Frontend production build: PASS
Final regression: PASS
```

The regression suite deliberately forces deterministic/offline routing so automated tests do not spend Azure quota or depend on a live Azure login. Foundry-specific behavior is tested using mocks, while live routing is verified separately through the application trace.

---

## Azure AI Foundry Verification

A successful live routing trace includes metadata similar to:

```json
{
  "routing_source": "foundry",
  "model": "gpt-5-mini",
  "intent": "compound_sales_inventory"
}
```

The verified compound workflow demonstrates:

```text
Manager Agent
  â†“
Foundry gpt-5-mini route selection
  â†“
Sales Agent
  â†“ get_top_products()
context_passed
  â†“
Inventory Agent
  â†“ get_product_stock() Ã— 3
Final grounded response
```

For strict verification, temporarily disable fallback:

```env
FOUNDRY_FALLBACK_TO_LOCAL=false
```

If the request succeeds and the trace reports `routing_source = foundry`, the application has completed the live Foundry routing path rather than silently using the local router.

---

## Responsible AI and Security

NEXUS includes deliberate safeguards:

- The LLM selects from a **validated intent enum**.
- The LLM cannot provide arbitrary executable Python or SQL.
- The server decides which specialist operations are allowed.
- Business values come from deterministic tools and databases.
- Unsupported requests execute zero specialist business tools.
- Synthetic dataset status is disclosed.
- The assumed inventory snapshot date is disclosed.
- No reorder levels are fabricated.
- Forecasts are labelled as estimates rather than facts.
- Reliability bands are not presented as confidence intervals.
- Risk thresholds are deterministic and inspectable.
- No employee risk scoring or attrition prediction is implemented.

### Repository safety

Never commit:

```text
backend/.env
Azure tokens or credentials
API keys
.venv/
node_modules/
frontend/dist/
backend/data/nexus_analytics.db
```

Azure authentication uses the signed-in CLI identity through `AzureCliCredential` rather than a hard-coded API key.

---

## Known Limitations

NEXUS is an academic proof of concept, not a production ERP system.

Current limitations include:

1. The USA Toy Sales dataset is synthetic/fictitious.
2. Retail history covers only Janâ€“Dec 2025.
3. Inventory is point-in-time data with no source-provided snapshot date.
4. Forecasting has limited historical depth and should not be interpreted as long-term certainty.
5. Supplier lead-time and safety-stock data are unavailable.
6. No purchase-order or replenishment engine is implemented.
7. People Management data are synthetic and separate from the retail dataset.
8. SQLite is appropriate for this PoC but not the intended final production-scale data platform.
9. The Assistant supports a controlled business-domain intent set rather than unrestricted general-purpose tool use.
10. Frontend bundle size can be optimized further through code splitting.

---

## Future Scope

Potential extensions include:

- Live ERP, CRM, POS, and inventory connectors
- Azure-hosted production databases
- Authentication and role-based access control
- Real-time inventory feeds
- Supplier and purchase-order data
- Lead-time-aware replenishment planning
- Longer historical datasets for stronger seasonal forecasting
- Additional specialist agents such as Finance or Procurement
- Automated stockout and forecast exception alerts
- Semantic retrieval over company policies and documentation
- Azure production deployment and centralized observability
- Frontend route-level code splitting

---

## Demo Flow

A concise project demonstration can follow this order:

1. **Overview** â€” unified business KPIs and the two data domains.
2. **Sales + Inventory** â€” consistent Kaggle-backed retail information.
3. **Business Performance** â€” revenue, profit, product, category, store, and location analytics.
4. **Insights & Risk** â€” deterministic risk signals.
5. **Forecasting** â€” four-week forecast and inventory demand coverage.
6. **People Management** â€” separate internal workforce domain.
7. **Assistant** â€” run the compound sales/inventory question.
8. **Developer View** â€” show `routing_source: foundry`, `model: gpt-5-mini`, and agent-to-agent context passing.
9. **Guardrail** â€” ask a weather question and show `unsupported` with no specialist execution.

Prepared supporting material is available in:

```text
docs/DEMO_SCRIPT.md
docs/FINAL_CHECKLIST.md
```

---

## Summary

NEXUS demonstrates a practical hybrid AI architecture:

```text
Natural-language intelligence
        +
Controlled multi-agent orchestration
        +
Deterministic business tools
        +
Reproducible analytics data
        +
Transparent risk and forecasting logic
```

The result is a business assistant that is more flexible than a fixed dashboard while remaining substantially more traceable and data-grounded than an unrestricted LLM chatbot.

---

**Project:** NEXUS â€” Multi-Agent Business Assistant
**Course:** AI-103
**Status:** Academic Proof of Concept
