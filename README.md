# BridgeUp 🚀

**A Hybrid Multi-Agentic Learning Orchestration Framework for Personalized Skill Development**

BridgeUp is an AI-powered learning platform that turns a career goal (e.g. *"Backend Developer"*) into a fully personalized journey: it plans a skill-gap-aware learning roadmap, schedules it around your weekly availability, teaches each lesson through an LLM tutor, monitors your learning behavior, **adaptively re-plans itself when dropoff risk rises**, and finally surfaces matching career opportunities — all from one Streamlit workspace.

> *From Learning to Earning.*

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [The Agents](#the-agents)
- [The Adaptive Loop (LangGraph)](#the-adaptive-loop-langgraph)
- [AI Tutor](#ai-tutor)
- [Unified Event System](#unified-event-system)
- [External Integrations](#external-integrations)
- [Data Layer (D1–D4 Datasets)](#data-layer-d1d4-datasets)
- [Machine Learning: Dropout Risk Prediction](#machine-learning-dropout-risk-prediction)
- [Web UI](#web-ui)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Entry Points](#entry-points)
- [Known Limitations & Notes](#known-limitations--notes)
- [License](#license)

---

## Overview

Traditional online-learning systems generate static course lists. BridgeUp treats learning as an **orchestrated, monitored, self-adapting process**, modeled as a multi-agent system:

1. **Plan** — a deterministic Planning Agent computes the skill gap between your current skills and your target role, resolves prerequisite dependencies, and assembles a learning roadmap from a curated resource catalog. Three plan strategies are generated: `fast`, `balanced`, and `deep`.
2. **Schedule & Execute** — an Action Agent converts the roadmap into granular micro-tasks (2-hour chunks) and allocates them deterministically across a 5-day study week.
3. **Monitor** — a Monitoring Agent ingests task lifecycle events, computes behavioral metrics (completion rate, delay index, workload utilization, stability, consistency, dropoff risk), and produces a risk profile.
4. **Adapt** — an LLM-backed decision node inspects the metrics and chooses to `continue`, `replan` (switch strategy), or `adjust` (reschedule) — with hard guardrails and loop protection. The whole flow runs as a **LangGraph state graph** with conditional edges, so the system literally re-runs its own pipeline until it stabilizes.
5. **Teach** — a personal AI Tutor generates contextual lessons (explanation, example, practice task, reflection question) for each task and answers follow-up questions with short-term conversational memory.
6. **Bridge to Career** — live integrations fetch real remote jobs (Remotive / Adzuna), GitHub project ideas, courses, and tutorials matched to the skills being learned.

A Streamlit frontend wraps the entire engine: generate a plan, walk through the learning journey, learn with the tutor chat, mark tasks complete/missed, and watch the dashboard metrics react in real time.

---

## Key Features

- 🧭 **Skill-gap roadmap planning** — weighted skill gap computation against a job-role model, hard/soft prerequisite dependency graph, constraint-aware topological ordering, duration-based resource selection.
- 🎚️ **Multi-strategy planning** — every request produces three alternative roadmaps (`fast` / `balanced` / `deep`) with strategy-aware mastery levels and week-wise schedules.
- 🤖 **LLM advisory layer** — GPT-4o-mini used in *suggest-only* mode: strategy suggestions, roadmap explainability, resource ranking, learning-plan generation, monitoring feedback, and reflection/coaching summaries — all validated against **Pydantic schemas** with JSON mode, retries, and caching.
- 🔁 **Self-adaptive LangGraph loop** — `strategy → plan → action → monitor → jobs → risk → decision → (replan | adjust | continue)` with conditional routing, guardrails (high risk can never `continue`), and a 3-cycle loop guard.
- 📊 **Behavioral monitoring engine** — task/session signal models, metric snapshots, and a rule-based risk analyzer detecting low engagement, overload, chronic delay, unstable execution, and strategy mismatch.
- 🧑‍🏫 **AI Tutor with memory** — teach / quiz / practice mode detection, bounded conversation memory, strictly on-topic structured JSON lessons.
- 📡 **Unified, validated event system** — append-only, schema-versioned JSONL event logs per session with per-event-type payload validation and thread-safe writes.
- 🌐 **Live resource intelligence** — jobs, GitHub repos, courses, and tutorials aggregated per skill with graceful demo fallbacks.
- 🧪 **ML research pipeline** — dropout-risk classification (Logistic Regression vs Random Forest vs XGBoost), stratified k-fold evaluation, SHAP explainability, ROC/confusion-matrix plots.
- 🖥️ **Streamlit dashboard** — progress stats, learning-balance & consistency insights, interactive journey tracker, tutor workspace, and career-match scoring.

---

## System Architecture

```
                          ┌────────────────────────────────────────┐
                          │            Streamlit UI (app.py)       │
                          │  Dashboard · Journey · Learn · Career  │
                          └───────────────────┬────────────────────┘
                                              │ run_bridgeup()
                                              ▼
┌─────────────────────────── LangGraph StateGraph ───────────────────────────┐
│                                                                            │
│  strategy_node ──► plan_node ──► action_node ──► monitor_node              │
│                        ▲               ▲               │                   │
│                        │               │               ▼                   │
│                        │               └── adjust ── job_fetch_node        │
│                        │                               │                   │
│                        └──────── replan ── decision_node ◄─ risk_eval_node │
│                                              (LLM + guardrails)            │
└────────────────────────────────────────────────────────────────────────────┘
        │                    │                     │                  │
        ▼                    ▼                     ▼                  ▼
  Planning Agent       Action Agent         Monitoring Agent    Integrations
  (skill-gap,          (task chunking,      (event ingestion,   (Remotive, Adzuna,
   dependency graph,    scheduling,          metrics, risk        GitHub, SerpAPI,
   roadmaps D1–D4)      rescheduling)        profiles)            dev.to)
        │                    │                     │
        └──────────── Orchestrator (agent registry, adapters,
                      session state machine, workflow router)
                                     │
                                     ▼
                        Unified Event System (events/)
                        JSONL logs → data/events/session_*.jsonl
```

The **Orchestrator** (`agents/orchestrator_agent/`) is the core engine: it registers agents behind a uniform `AgentRequest → AgentResponse` adapter protocol, drives a `SessionState` state machine (`INIT → VALIDATED → PLANNING → PLAN_READY → EXECUTING → MONITORING → COMPLETED/ERROR`), routes workflows (`planning_only`, `planning_action_monitor`, `replanning`, …), and emits lifecycle events. The LangGraph layer *wraps* these agents without modifying them.

---

## The Agents

| Agent | Location | Responsibility |
|---|---|---|
| **Planning Agent** | `agents/planning_agent/` | Skill-gap computation, dependency graph (hard/soft prerequisites), constraint-aware ordering with cycle detection, resource selection, roadmap assembly, mastery levels, weekly scheduling, explainability notes. |
| **Action Agent** | `agents/action_agent/` | Deterministic executor (roadmap → 120-min micro-tasks), capacity-aware scheduler (5 study days/week, deadline assignment), task tracker (state transitions + progress snapshots), rescheduler for `adjust` cycles. |
| **Monitoring Agent** | `agents/monitoring_agent/` | Collector (idempotent event ingestion, session snapshots), MetricsEngine (completion rate, delay index, workload utilization, stability score, dropoff risk, consistency), Analyzer (weighted issue detection → risk profile + execution summary). |
| **Orchestrator Agent** | `agents/orchestrator_agent/` | Agent registry/adapters, workflow routing, session state machine, error records, event emission, LLM advisory wiring. |
| **LLM Agent** | `agents/llm_agent/` | `LLMClient` (OpenAI JSON-mode calls, markdown-fence stripping, Pydantic validation, retries, prompt caching) + `LLMReasoningEngine` (8 prompt templates): strategy suggestion, roadmap explanation, monitoring feedback, API intent detection, reflection, resource ranking & explanation, learning plan generation. |
| **Learning Tutor** | `learning_tutor/` | Contextual lesson generation, mode detection (teach/quiz/practice), bounded `TutorMemory`, structured `TutorResponse`/`QuizResponse` schemas. |

---

## The Adaptive Loop (LangGraph)

The heart of the framework is `bridgeup_langgraph/graph.py` — a compiled LangGraph `StateGraph` over a typed `BridgeUpGraphState`:

| Node | What it does |
|---|---|
| `strategy_node` | Selects `fast` / `balanced` / `deep` from user context (mock-LLM heuristic; production-swappable). |
| `plan_node` | Runs the Planning Agent via the Orchestrator → roadmap for the selected strategy. |
| `action_node` | Curriculum-aware task generation + scheduling; supports `adjust` rescheduling of incomplete tasks. |
| `monitor_node` | Simulates/executes the task lifecycle (`TASK_CREATED → STARTED → COMPLETED/MISSED`) with strategy-dependent behavior profiles and builds the metric snapshot. |
| `job_fetch_node` | Extracts skills from tasks and fetches live remote jobs (India/Remote filter, URL dedup). |
| `risk_eval_node` | Pulls `RiskProfile` + `ExecutionSummary` from the Monitoring Agent. |
| `decision_node` | **LLM decision (gpt-4o-mini)** returning JSON `{action, new_strategy, reason, explanation}` with hard guardrails: risk < 0.25 forces `continue`; risk ≥ 0.3 overrides `continue` → `replan`; repeated `replan` → `adjust`; deterministic fallback if the LLM fails. |

**Conditional routing** after the decision: `replan → plan_node` (strategy change), `adjust → action_node` (reschedule), `continue → END` — with a **loop guard at 3 adaptation cycles**.

---

## AI Tutor

`learning_tutor/tutor.py` implements a strict, on-topic personal tutor on top of the shared `LLMClient`:

- **Modes** auto-detected from user input: `teach`, `quiz` ("quiz", "test me", …), `practice` ("I tried", "check", …).
- **Lessons** are structured JSON: `explanation`, `example`, `practice_task`, `follow_up_question`, `difficulty_level`.
- **Memory**: a bounded `deque` (last 3 interactions) + last-5 chat lines injected into the prompt.
- Used both by the interactive CLI (`bridgeup_langgraph/run_graph.py`) and the Streamlit **Learn** page.

---

## Unified Event System

`events/` provides an append-only observability backbone:

- **Schema v1.0** (`events/schema.py`): canonical `EventType` enum (session + task + monitoring events) and `AgentName` registry — append-only evolution rules.
- **Validation** (`events/validator.py`): per-event-type required/optional payload schemas.
- **Emission** (`events/emitter.py`): agent-safe wrappers (`emit_orchestrator_event`, `emit_action_event`, `emit_monitoring_event`).
- **Logging** (`events/logger.py`): thread-safe JSONL append to `data/events/session_<id>.jsonl`, designed to never raise fatal errors.

The repository already contains **500+ recorded session event logs** and 150+ monitoring session snapshots generated during experimentation.

---

## External Integrations

`integrations/` aggregates live learning & career resources per skill, with graceful fallbacks:

| Client | Source | Resources |
|---|---|---|
| `JobAPIClient` | Remotive + Adzuna | Remote job postings (title, company, location, salary, URL) |
| `GitHubAPIClient` | GitHub Search API | Popular project repos for hands-on practice |
| `CourseAPIClient` | SerpAPI (Google) | Online courses for a skill |
| `TutorialAPIClient` | dev.to API | Community tutorials by tag |

Shared plumbing: `BaseAPIClient` with timeout handling, a simple token-bucket-style `RateLimiter`, typed `APIError`, dataclass schemas, and a `ResourceAggregator` that combines all sources (with demo fallback content when APIs are unavailable).

---

## Data Layer (D1–D4 Datasets)

The Planning Agent is grounded in four curated datasets (builders in `data/code/`, outputs in `data/processed/`):

| Dataset | Contents | Source/Build |
|---|---|---|
| **D1** — `D1_final.csv` | ~120 learning resources (title, provider, domain, skill tags, difficulty, duration, cost, URL) | Cleaned from an 8.8k-row Kaggle course catalog (`data/raw/D1_kaggle_raw.csv`) with duration parsing & difficulty inference |
| **D2** — `D2_skill_domain_taxonomy.csv` | 150-skill taxonomy (domain, parent skill, level) | Generated from D1 tags + D3 role requirements |
| **D3** — `D3_skill_job_mapping.csv` | 8 job roles with required skills + weightage (Software Engineer, Data Analyst, Data Scientist, ML Engineer, Full Stack, …) | Curated role→skill mapping |
| **D4** — `D4_skill_prerequisites.csv` | Prerequisite edges classified as `hard` / `soft` | Rule-based dependency classification over D2 |

`data/data_loader.py` provides mock loaders (skills, prerequisites, resources, job requirements) used by the Orchestrator for orchestration testing.

---

## Machine Learning: Dropout Risk Prediction

`ml/` contains a research-style experiment pipeline that learns to predict learner dropout from monitoring metrics:

1. **`build_ml_dataset.py`** — converts session metrics into `metrics_ml_ready.csv` with a binary `dropout_label` (`dropoff_risk ≥ 0.3`).
2. **`preprocessing.py`** — strategy encoding, interaction features (`delay×workload`, `stability×consistency`), standard scaling.
3. **`train_model.py`** — trains **Logistic Regression, Random Forest, and XGBoost**; the winner is serialized with its scaler to `models/bridgeup_dropout_model.pkl`.
4. **`evaluate_models.py`** — 5-fold stratified cross-validation comparison.
5. **`predict.py`** — single-session dropout-probability inference from live metrics.
6. **`generate_plots.py` / `correlation_heatmap.py` / `shap_analysis.py`** — confusion matrix, ROC curves, metric correlation heatmap, and SHAP (TreeExplainer) feature-attribution plots into `paper_assets/`.

---

## Web UI

`app.py` is a single-page Streamlit app with a custom design system (CSS variables, cards, pills, chat bubbles) and four views:

- **Dashboard** — tasks completed, active lessons, learning-balance (dropoff-risk based), study consistency, AI insights, activity timeline.
- **Learning Journey** — phase-by-phase roadmap cards with Complete / Learning / Missed actions that feed the Monitoring Agent and refresh metrics live.
- **Learn** — AI Tutor workspace: generate a lesson for any task, read explanation/example/practice/reflection, chat with the tutor, complete the lesson.
- **Career Opportunities** — job recommendations with keyword match scoring against your goal and skills.

Sidebar inputs: **Career Goal**, **Existing Skills**, **Weekly Study Hours** → one click runs the full LangGraph pipeline.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | **Python 3.11** |
| Agent orchestration | **LangGraph** (`StateGraph`, conditional edges, typed shared state) |
| LLM | **OpenAI API — gpt-4o-mini** (JSON mode, temperature 0 for decisions), via the `openai` SDK |
| Structured outputs | **Pydantic** (schema-validated LLM generation with retries) |
| Web UI | **Streamlit** (custom CSS theme) |
| ML / experiments | **scikit-learn, XGBoost, SHAP, joblib** |
| Data wrangling | **pandas, NumPy** |
| Visualization | **matplotlib, seaborn** |
| HTTP / APIs | **requests** — Remotive, Adzuna, GitHub Search, SerpAPI, dev.to |
| Persistence | File-based: **JSONL event logs**, CSV datasets, pickled models, per-session monitoring snapshots (no external DB) |
| Concurrency safety | Thread-locked event writer |

---

## Project Structure

```
├── app.py                        # Streamlit frontend (4 pages)
├── agents/
│   ├── orchestrator_agent/       # Orchestrator, adapters, router, session state
│   ├── planning_agent/           # Skill-gap planning, strategies, models, service
│   ├── action_agent/             # Executor, scheduler, tracker, rescheduler
│   ├── monitoring_agent/         # Collector, metrics engine, risk analyzer
│   └── llm_agent/                # LLM client, reasoning engine, prompts, schemas
├── bridgeup_langgraph/
│   ├── graph.py                  # LangGraph StateGraph (adaptive loop)
│   ├── ui_runner.py              # One-shot invocation used by the UI
│   ├── run_graph.py              # Interactive CLI with tutor loop
│   └── tutor_node.py             # Tutor node wrapper
├── learning_tutor/               # AI tutor, memory, schemas
├── events/                       # Unified event schema, emitter, validator, logger
├── integrations/                 # Job/GitHub/Course/Tutorial API clients + aggregator
├── ml/                           # Dropout-prediction experiment pipeline
├── data/
│   ├── raw/                      # D1 raw Kaggle catalog
│   ├── processed/                # D1–D4 cleaned datasets
│   ├── code/                     # Dataset generation scripts
│   ├── events/                   # Recorded session JSONL event logs
│   └── monitoring_logs/          # Per-session monitoring snapshots
├── models/                       # Serialized dropout model (.pkl)
├── backend/                      # Reserved package
└── LICENSE                       # MIT
```

---

## Getting Started

### 1. Clone & install

```bash
git clone https://github.com/Rishiram20757/BridgeUp-A-Hybrid-Multi-Agentic-Learning-Orchestration-Framework-for-Personalized-Skill-Development.git
cd BridgeUp-A-Hybrid-Multi-Agentic-Learning-Orchestration-Framework-for-Personalized-Skill-Development
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install streamlit langgraph openai pydantic requests \
            pandas numpy scikit-learn xgboost shap joblib matplotlib seaborn
```

### 2. Configure environment

```bash
export OPENAI_API_KEY="sk-..."   # required for the tutor, LLM advisory layer & decision node
```

> Optional live-resource integrations use Remotive/GitHub/dev.to (no key) and Adzuna/SerpAPI keys currently embedded in `integrations/` — rotate them and move them to environment variables before deploying.

### 3. Run

```bash
# Web app (http://localhost:8501)
streamlit run app.py

# Interactive CLI session (graph + tutor chat)
python -m bridgeup_langgraph.run_graph
```

---

## Entry Points

| Command | Purpose |
|---|---|
| `streamlit run app.py` | Full web experience: plan → learn → monitor → career |
| `python -m bridgeup_langgraph.run_graph` | Terminal demo: one graph run + interactive tutor loop (`complete` / `exit`) |
| `python ml/train_model.py` etc. | ML experiment scripts (expect `paper_assets/03_metrics/metrics_ml_ready.csv`) |
| `python data/code/D*.py` | Rebuild the D1–D4 datasets |

---

## Known Limitations & Notes

- `strategy_node` and the `monitor_node` execution simulation use deterministic heuristics as **mock-LLM / simulation placeholders** — swap in real user telemetry for production.
- API keys (Adzuna, SerpAPI) are hardcoded in `integrations/`; treat them as compromised and migrate to environment variables.
- `__pycache__/` directories are currently committed; a `.gitignore` is recommended.
- Persistence is file-based (JSONL/CSV/pickle) by design — no database layer yet (`backend/` is reserved for it).
- The ML pipeline reads from `paper_assets/`, which is generated by the experiment harness and not bundled.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

© 2026 Rishiram B
