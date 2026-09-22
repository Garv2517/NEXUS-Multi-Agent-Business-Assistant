# NEXUS — 5-Minute Demo Script

## 0:00–0:35 — Problem + architecture

Open **Overview**.

Say:

> NEXUS is a multi-agent business assistant built for AI-103. It combines Azure AI Foundry GPT-5-mini for natural-language workflow routing with deterministic specialist agents and verified business tools. Retail analytics use a unified synthetic USA Toy Sales dataset, while People Management is kept separate because the retail source contains no HR data.

Point out:

- unified USD retail KPIs
- zero-stock exposure
- 180-person internal People Management domain
- shortcuts to Performance, Risk, and Forecasting

## 0:35–1:20 — Unified business analytics

Open **Sales** and then **Inventory**.

Show that the same products/categories appear across the workspace.

Mention:

> We intentionally removed the old unrelated demo sales/inventory data from the visible product. Sales, Inventory, Performance, Risk, Forecasting, and the Assistant now use the same retail analytics domain.

In Inventory mention:

> The raw dataset contains no reorder levels, so NEXUS does not invent them.

## 1:20–2:00 — Performance + Risk

Open **Business Performance**.

Show:

- annual revenue / gross profit
- monthly performance
- categories / products / stores
- external dataset disclosure

Then open **Insights & Risk**.

Say:

> Risk is deterministic, not LLM-generated. Thresholds were calibrated from the dataset and exposed through a configuration endpoint. We calculate stockout exposure, days-of-supply pressure, slow-moving capital exposure, sales-velocity changes, and portfolio revenue concentration.

## 2:00–2:40 — Forecasting

Open **Forecasting & Planning**.

Say:

> Forecasting uses chronological rolling-origin validation, not random train/test splits. We evaluate Naive, moving-average, OLS, and simple exponential-smoothing models and select the best validated model per series over a four-week horizon.

Point out:

- actual vs forecast
- validation WAPE
- historical MAE reference
- demand-coverage metrics
- inventory snapshot assumption

## 2:40–4:20 — Live Azure Foundry multi-agent proof

Open **Assistant**.

Confirm header shows:

> Azure Foundry Routing Active · gpt-5-mini

Ask:

> Can you figure out which three products generated the highest sales and compare each one's current inventory?

Show the answer and **Developer View / Agent Trace**.

Highlight:

1. `routing_source = foundry`
2. `model = gpt-5-mini`
3. `intent = compound_sales_inventory`
4. Sales Agent executes `get_top_products`
5. product IDs are passed to Inventory Agent
6. Inventory Agent executes `get_product_stock` for each product

Say:

> GPT-5-mini chooses the validated workflow. It does not invent the sales or inventory numbers. Those values come from deterministic tools and SQLite.

Then ask:

> What is the weather in Chandigarh?

Show `unsupported` route with zero specialist tools.

Say:

> Out-of-domain requests are rejected before business tools run.

## 4:20–5:00 — Activity + Responsible AI + close

Open **Activity** or **About NEXUS**.

Close with:

> NEXUS demonstrates Foundry model routing, multi-agent orchestration, context passing, deterministic tools, responsible data handling, risk analytics, and time-series planning in one coherent business system. The architecture also supports local deterministic fallback if the cloud model is temporarily unavailable.

## Best screenshots to capture

1. Overview unified KPIs
2. Risk page with methodology disclosure
3. Forecast page with model + validation metric
4. Assistant answer using Kaggle products
5. Agent Trace showing `routing_source: foundry`, `gpt-5-mini`, context passing, and tool execution
6. Foundry deployment metrics / model requests if available
