# NEXUS — Final Submission Checklist

## Runtime

- [ ] `backend/.env` has the correct Foundry project endpoint
- [ ] `FOUNDRY_MODEL=gpt-5-mini`
- [ ] `ORCHESTRATION_MODE=foundry_manager`
- [ ] `FOUNDRY_FALLBACK_TO_LOCAL=true` for the live presentation
- [ ] `az account show` succeeds
- [ ] `nexus_analytics.db` rebuilt from raw CSVs
- [ ] Backend starts on `127.0.0.1:8000`
- [ ] Frontend starts on `localhost:5173`

## Regression

- [ ] Full backend pytest suite passes locally
- [ ] Frontend `npm.cmd run build` passes
- [ ] Overview loads unified Kaggle retail data
- [ ] Sales uses USD / Kaggle products
- [ ] Inventory uses Kaggle stock and no fabricated reorder levels
- [ ] People Management shows 180 employees / 12 departments
- [ ] Business Performance loads
- [ ] Insights & Risk loads
- [ ] Forecasting & Planning loads
- [ ] Activity page records Assistant tool executions
- [ ] About page accurately describes current architecture
- [ ] Internal navigation remains in the same browser tab

## Live Foundry proof

- [ ] Assistant header says `Azure Foundry Routing Active · gpt-5-mini`
- [ ] Compound Sales + Inventory query succeeds
- [ ] Developer View contains `routing_source: foundry`
- [ ] Developer View contains `model: gpt-5-mini`
- [ ] Trace shows Sales → context_passed → Inventory
- [ ] Unsupported weather query routes to `unsupported`
- [ ] Optional: Azure deployment metrics show model request / token activity

## Data / Responsible AI

- [ ] UI identifies retail data as synthetic Kaggle data
- [ ] Currency is USD throughout retail analytics
- [ ] Inventory snapshot date is clearly marked as assumed
- [ ] No lost-revenue claims from stockout snapshot data
- [ ] No reorder levels invented for Kaggle inventory
- [ ] No employee risk / attrition scoring
- [ ] Forecasts are labelled as forecasts
- [ ] Historical MAE is not labelled as a confidence interval

## Git / security

- [ ] `.env` is not staged
- [ ] `backend/data/nexus_analytics.db` is not staged
- [ ] `backend/data/nexus.db` has no accidental runtime-only changes staged
- [ ] No credentials / access tokens appear in `git diff --cached`
- [ ] `git status --short` reviewed before final commit

## Submission

- [ ] Root README included
- [ ] GitHub repository pushed
- [ ] 5-minute demo recorded
- [ ] YouTube link works
- [ ] LMS submission includes repository + video link
