# Nexus — Multi-Agent Business Assistant Backend (Phase B3)

FastAPI backend with local multi-agent orchestration layer, deterministic router, context passing, and SQLite database for Nexus Multi-Agent Business Assistant.

## Architecture

```
User Query
    ↓
Manager Agent (Local Orchestrator)
    ↓ Generates Execution Plan via DeterministicRouter
 ├── Sales Agent (sales.* operations)
 ├── Inventory Agent (inventory.* operations)
 └── HR Agent (hr.* operations)
       ↓
Business Tools (Deterministic Python Functions)
       ↓
Repositories (Pure SQL Data Access)
       ↓
SQLite (Local Database: backend/data/nexus.db)
```

> **Note on Phase B3 & Future AI Orchestration**:
> Phase B3 validates specialist agent boundaries, deterministic routing, tool delegation, and agent-to-agent context passing without external AI dependencies. All routing and task execution in Phase B3 are strictly software-level and deterministic; they do NOT represent AI reasoning.
> Microsoft Foundry and model-driven orchestration (LLM reasoning and intent classification) will be integrated in Phase B4.

---

## Agent Layer (`backend/app/agents/`)

### 1. Base Agent Contract (`base.py` & `types.py`)
- `BaseAgent`: Defines `name`, `description`, and asynchronous public contract `async def execute(task: AgentTask) -> AgentResult`.
- `AgentTask`: Carries `task_id`, `operation`, `parameters`, and `context`.
- `ToolCallRecord`: Tracks executed tool name, arguments, status, real measured `duration_ms`, and `result_summary`.
- `AgentResult`: Structured result data, list of `ToolCallRecord`s, and error details. Specialist agents do not produce conversational prose.
- `ExecutionPlan` & `PlanStep`: Encapsulates multi-agent step dependencies and routing plans.

### 2. Specialist Agents
- **`SalesAgent`** (`sales.py`):
  - Operations: `sales.total`, `sales.monthly`, `sales.top_products`, `sales.trend`.
  - Strictly calls only sales tools (`get_total_sales`, `get_monthly_sales`, `get_top_products`, `get_sales_trend`). Zero direct database or repository access.
- **`InventoryAgent`** (`inventory.py`):
  - Operations: `inventory.product_stock`, `inventory.low_stock`, `inventory.summary`.
  - Strictly calls only inventory tools (`get_product_stock`, `get_low_stock_products`, `get_inventory_summary`).
- **`HRAgent`** (`hr.py`):
  - Operations: `hr.summary`, `hr.employee`, `hr.policy`, `hr.policies`.
  - Strictly calls only HR tools (`get_employee_summary`, `get_employee_details`, `get_hr_policy`, `get_all_hr_policies_tool`).

### 3. Agent Registry (`registry.py`)
- Manages specialist agent lifecycle via dependency injection.
- Instantiated through `create_default_registry()` and passed to `ManagerAgent` constructors.

### 4. Manager Agent (`manager.py`)
- Orchestrates multi-agent workflows.
- Asks `DeterministicRouter` for an `ExecutionPlan`.
- Executes specialists, extracts intermediate data, and passes context (e.g. extracts top product IDs `[P101, P102, P103]` from `SalesAgent` and executes `InventoryAgent` for each).
- Emits real trace events (`manager_started`, `route_selected`, `agent_started`, `tool_started`, `tool_completed`, `agent_completed`, `context_passed`, `response_completed`, `agent_failed`, `tool_failed`).
- Synthesizes factual final responses using SQLite-derived tool data.

---

## Deterministic Router (`backend/app/orchestration/router.py`)

Provides small, deterministic intent routing:
1. **Compound (Sales + Inventory)**: *"Compare our top-selling products with current inventory"*
2. **Compound (Business Overview)**: *"Give me a business overview"* (invokes Sales, Inventory, and HR agents)
3. **Single-Agent Queries**:
   - Sales: *"How much revenue did we make?"*
   - Inventory: *"Which products are low in stock?"*
   - HR: *"What is our annual leave policy?"*
4. **Unsupported / Out-of-Domain**: Queries like *"What's the weather?"* return a polite domain capability message without invoking any business agents or tools.

---

## Chat Service & API

- `POST /api/chat`: Generates a dynamic UUID session ID per request (`uuid.uuid4()`), delegates query processing to `ManagerAgent`, and returns `session_id`, `answer`, `agents_used`, `tool_calls`, `trace`, and `plan`.
- `GET /api/health`: Reports `mode = "local_orchestration"`, `foundry = "not_configured"`, `model = "not_configured"`.

---

## Running & Testing

```bash
# Run test suite with warnings visible
pytest -W default

# Run backend development server
uvicorn app.main:app --port 8000
```

---

## Microsoft Foundry Connectivity (Phase B4A Preflight)

- **Active Orchestration Mode**: Phase B3 local deterministic orchestration remains the active runtime mode (`ORCHESTRATION_MODE=local`).
- **Phase B4A Scope**: Validates external Microsoft Foundry environment authentication and connectivity in isolation via `backend/scripts/foundry_smoke_test.py`.
- **Local Authentication**: Uses `AzureCliCredential()` to authenticate locally through an authorized Azure CLI login session (`az login`). No passwords, API keys, client secrets, or auth tokens are committed.
- **Environment Configuration**:
  - `FOUNDRY_PROJECT_ENDPOINT`: Team Microsoft Foundry project endpoint URL.
  - `FOUNDRY_MODEL`: Target deployed chat model deployment name.
- **Model-Driven Orchestration**: Model-driven multi-agent routing, tool exposure, and LLM reasoning will begin strictly in Phase B4B.
