"""
BridgeUp LangGraph Implementation
----------------------------------
Wraps existing BridgeUp agents into a LangGraph state graph.
Agents are NOT modified — only wrapped.
"""

import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

# ── Existing agent imports ────────────────────────────────────────────────────
from agents.orchestrator_agent.orchestrator import Orchestrator
from agents.orchestrator_agent.state import SessionState
from agents.monitoring_agent import MonitoringAgent
from bridgeup_langgraph.tutor_node import tutor_node

# =============================================================================
# 1. SHARED STATE DEFINITION
# =============================================================================

class BridgeUpGraphState(TypedDict):
    # ── User inputs ────────────────────────────────────────────────────────────
    session_id:          str
    user_goal:           str
    known_skills:        list
    weekly_hours:        int
    start_date:          Any           # datetime

    # ── strategy_node outputs ─────────────────────────────────────────────────
    selected_strategy:   str
    strategy_rationale:  str

    # ── plan_node outputs ─────────────────────────────────────────────────────
    roadmap:             Optional[Any]

    # ── action_node outputs ───────────────────────────────────────────────────
    tasks:               list
    schedule_blocks:     list

    # ── monitor_node outputs ──────────────────────────────────────────────────
    metric_snapshot:     Optional[Any]

    # ── risk_eval_node outputs ────────────────────────────────────────────────
    risk_profile:        Optional[Any]
    execution_summary:   Optional[Any]

    # ── decision_node outputs ─────────────────────────────────────────────────
    decision_action:     str           # "continue" | "replan" | "adjust"
    decision_reason:     str

    # ── loop guard ────────────────────────────────────────────────────────────
    adaptation_cycles:   int

    # ── internal session state (passed through nodes) ─────────────────────────
    _session_state:      Optional[Any]  # SessionState object
    _monitor:            Optional[Any]  # MonitoringAgent object
    job_recommendations: Optional[list]

    current_task: Optional[dict]
    current_task_index: int
    user_input: Optional[str]
    tutor_output: Optional[Any]


# =============================================================================
# 2. NODE IMPLEMENTATIONS
# =============================================================================

# ── strategy_node (Mock LLM) ──────────────────────────────────────────────────

def strategy_node(state: BridgeUpGraphState) -> dict:
    """
    Mock LLM node. Reads user context and selects a strategy.
    In production: replace body with real LLM call returning JSON.
    """
    user_goal    = state["user_goal"]
    known_skills = state["known_skills"]
    weekly_hours = state["weekly_hours"]
    cycles       = state["adaptation_cycles"]

    # ── Mock LLM logic ────────────────────────────────────────────────────────
    # On a replan loop the strategy may have already been updated by
    # decision_node. We respect whatever is already in state["selected_strategy"]
    # if this is not the first entry (cycles > 0).
    if cycles > 0:
        # Keep the strategy that decision_node already wrote
        strategy  = state["selected_strategy"]
        rationale = (
            f"Adaptation cycle {cycles}: retaining strategy '{strategy}' "
            f"as directed by decision_node."
        )
    else:
        # First pass: choose based on simple heuristics (mock LLM placeholder)
        if weekly_hours <= 5:
            strategy  = "fast"
            rationale = "Limited weekly hours → fast strategy minimises overload."
        elif weekly_hours >= 15:
            strategy  = "deep"
            rationale = "High weekly hours available → deep strategy maximises coverage."
        else:
            strategy  = "balanced"
            rationale = "Moderate weekly hours → balanced strategy suits the learner."

    print(f"\n[strategy_node] strategy={strategy!r}  rationale={rationale!r}")

    return {
        "selected_strategy": strategy,
        "strategy_rationale": rationale,
    }


# ── plan_node ─────────────────────────────────────────────────────────────────

def plan_node(state: BridgeUpGraphState) -> dict:
    """
    Wraps Planning Agent via the existing Orchestrator.handle_request().
    Reads strategy from state; writes roadmap + internal SessionState back.
    """
    orchestrator  = Orchestrator()
    session_state = SessionState(session_id=state["session_id"])

    request = {
        "job_requirement": state["user_goal"],
        "known_skills":    state["known_skills"],
        "weekly_time_hours": state["weekly_hours"],
        "strategy":        state["selected_strategy"],
        "request_type":    "generate_plan_only",      # planning step only
        "start_date":      state["start_date"],
    }

    orchestrator.handle_request(request, session_state)

    roadmap = session_state.planning_state.roadmap_options.get(
        session_state.planning_state.selected_strategy
    )

    print(
        f"\n[plan_node] strategy={state['selected_strategy']!r}  "
        f"roadmap_steps={len(roadmap.steps) if roadmap else 0}"
    )

    return {
        "roadmap":        roadmap,
        "_session_state": session_state,
    }


# ── action_node ───────────────────────────────────────────────────────────────

def action_node(state: BridgeUpGraphState) -> dict:
    """
    FINAL Stable Action Node

    ✔ Curriculum-based tasks
    ✔ Fully backward compatible
    ✔ Supports tutor, monitor, UI
    ✔ No more missing field errors
    """

    from agents.action_agent.executor  import generate_tasks_from_roadmap
    from agents.action_agent.scheduler import generate_schedule, reschedule
    from datetime import datetime

    weekly_capacity = state["weekly_hours"] * 60
    start_date      = state["start_date"]
    user_goal       = state.get("user_goal", "General")

    # ------------------------------------------------------
    # 🧠 CURRICULUM GENERATOR
    # ------------------------------------------------------
    def transform_to_curriculum(task_objects):
        structured = []
        goal = user_goal.lower()

        # ---------- CURRICULUM ----------
        if "python" in goal:
            curriculum = [
                ("Variables and Data Types", ["variables", "data types", "type casting"]),
                ("Lists and Indexing", ["lists", "indexing", "slicing"]),
                ("Control Flow (if/else)", ["if", "else", "conditions"]),
                ("Loops", ["for loop", "while loop"]),
                ("Functions", ["functions", "parameters", "return"]),
                ("Dictionaries", ["dict", "key-value pairs"]),
            ]

        elif "backend" in goal:
            curriculum = [
                ("HTTP Fundamentals", ["HTTP", "request/response", "status codes"]),
                ("Building APIs", ["REST APIs", "routing", "endpoints"]),
                ("Databases and SQL", ["SQL", "tables", "queries"]),
                ("Authentication", ["JWT", "sessions", "auth"]),
            ]

        else:
            curriculum = [
                (f"Introduction to {user_goal}", [user_goal.lower()])
            ]

        # ---------- TASK BUILD ----------
        for idx, (title, concepts) in enumerate(curriculum):
            raw = task_objects[idx] if idx < len(task_objects) else None

            structured.append({
                # Core IDs
                "task_id": f"t{idx+1}",
                "id": f"t{idx+1}",

                # Display + tutor
                "title": title,
                "skill": title,
                "level": "beginner",
                "goal": user_goal,

                # Learning structure
                "concepts": concepts,
                "description": f"Learn {title.lower()} in detail",
                "outcome": f"Able to understand and apply {title.lower()}",
                "difficulty": "beginner",
                "estimated_time": "2 hours",

                # Compatibility
                "raw": raw
            })

        return structured

    # ------------------------------------------------------
    # 🔁 ADJUST MODE
    # ------------------------------------------------------
    if state.get("decision_action") == "adjust" and state.get("tasks"):

        existing_tasks = state["tasks"]
        raw_tasks = [t["raw"] for t in existing_tasks if "raw" in t]

        blocks, updated_tasks = reschedule(
            incomplete_tasks        = raw_tasks,
            weekly_capacity_minutes = weekly_capacity,
            new_start_date          = datetime.now(),
        )

        structured_tasks = transform_to_curriculum(updated_tasks)

        return {
            "tasks": structured_tasks,
            "schedule_blocks": blocks,
            "current_task_index": 0,
            "current_task": structured_tasks[0] if structured_tasks else None
        }

    # ------------------------------------------------------
    # 🚀 FULL GENERATION
    # ------------------------------------------------------
    else:
        roadmap = state["roadmap"]

        tasks = generate_tasks_from_roadmap(roadmap)

        blocks, tasks_with_deadlines = generate_schedule(
            tasks                   = tasks,
            weekly_capacity_minutes = weekly_capacity,
            start_date              = start_date,
        )

        structured_tasks = transform_to_curriculum(tasks_with_deadlines)

        return {
            "tasks": structured_tasks,
            "schedule_blocks": blocks,
            "current_task_index": 0,
            "current_task": structured_tasks[0] if structured_tasks else None
        }

# ── monitor_node ──────────────────────────────────────────────────────────────

def monitor_node(state: BridgeUpGraphState) -> dict:
    """
    Monitoring + Lifecycle Simulation (UPDATED)

    ✔ Supports dict-based tasks (new)
    ✔ Backward compatible with object tasks
    ✔ Uses raw task internally for scheduling + deadlines
    ✔ Keeps full monitoring behavior unchanged
    """

    from pathlib import Path
    from datetime import datetime, timedelta

    session_id = state["session_id"]
    tasks      = state["tasks"]
    blocks     = state["schedule_blocks"]
    strategy   = state["selected_strategy"]

    is_adjust_phase = state.get("decision_action") == "adjust"

    monitor = MonitoringAgent(base_path=Path("data/monitoring_logs"))

    # ------------------------------------------------------
    # Helper: safely extract raw task + task_id
    # ------------------------------------------------------
    def get_raw_task(task):
        if isinstance(task, dict):
            return task.get("raw", None)
        return task

    def get_task_id(task):
        if isinstance(task, dict):
            return task.get("id")
        return getattr(task, "task_id", None)

    # ------------------------------------------------------
    # Map task_id → blocks
    # ------------------------------------------------------
    task_blocks_map: dict = {}
    for block in blocks:
        task_blocks_map.setdefault(block.task_id, []).append(block)

    # ------------------------------------------------------
    # Strategy config
    # ------------------------------------------------------
    if strategy == "fast":
        completion_ratio = 0.55
        delay_seconds    = -1800
        extra_miss_bias  = 0.10

    elif strategy == "balanced":
        completion_ratio = 0.75
        delay_seconds    = 1800
        extra_miss_bias  = 0.00

    else:  # deep
        completion_ratio = 0.65
        delay_seconds    = 8 * 3600
        extra_miss_bias  = 0.05

    # ------------------------------------------------------
    # Adjust phase improvement
    # ------------------------------------------------------
    if is_adjust_phase:
        completion_ratio += 0.15
        delay_seconds    *= 0.3
        extra_miss_bias  *= 0.5

    completion_ratio = min(completion_ratio, 0.95)

    total_tasks  = len(tasks)
    burnout_cut  = int(total_tasks * 0.85)
    adjusted_cut = int(total_tasks * (completion_ratio - extra_miss_bias))

    # ------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------
    for idx, task in enumerate(tasks):

        raw_task = get_raw_task(task)
        task_id  = get_task_id(task)

        # Fallback safety
        if task_id is None:
            task_id = f"task_{idx}"

        task_blocks = sorted(
            task_blocks_map.get(task_id, []),
            key=lambda b: b.start_time,
        )

        scheduled_start = (
            task_blocks[0].start_time if task_blocks else datetime.utcnow()
        )

        deadline = (
            getattr(raw_task, "deadline", None)
            or (task_blocks[-1].end_time if task_blocks else datetime.utcnow())
        )

        # ---------------------------
        # TASK_CREATED
        # ---------------------------
        monitor.collector.record_task_event({
            "event_type": "TASK_CREATED",
            "task_id": task_id,
            "session_id": session_id,
            "timestamp": scheduled_start.isoformat(),
            "payload": {
                "strategy_type": strategy,
                "scheduled_start": scheduled_start.isoformat(),
                "deadline": deadline.isoformat(),
            },
        })

        # ---------------------------
        # TASK_STARTED
        # ---------------------------
        monitor.collector.record_task_event({
            "event_type": "TASK_STARTED",
            "task_id": task_id,
            "session_id": session_id,
            "timestamp": scheduled_start.isoformat(),
            "payload": {},
        })

        # ---------------------------
        # COMPLETION / MISS
        # ---------------------------
        if idx < adjusted_cut and idx < burnout_cut:

            end_time = (
                task_blocks[-1].end_time if task_blocks else scheduled_start
            )

            completed_time = end_time + timedelta(seconds=delay_seconds)

            monitor.collector.record_task_event({
                "event_type": "TASK_COMPLETED",
                "task_id": task_id,
                "session_id": session_id,
                "timestamp": completed_time.isoformat(),
                "payload": {},
            })

        else:
            missed_time = deadline + timedelta(hours=12)

            monitor.collector.record_task_event({
                "event_type": "TASK_MISSED",
                "task_id": task_id,
                "session_id": session_id,
                "timestamp": missed_time.isoformat(),
                "payload": {},
            })

    # ------------------------------------------------------
    # Build snapshot
    # ------------------------------------------------------
    monitor.collector.build_session_snapshot(
        session_id=session_id,
        weekly_hours_allocated=state["weekly_hours"],
        planned_days=5,
    )

    metric_snapshot = monitor.get_session_metrics(session_id)

    print(
        f"\n[monitor_node] completion_rate={metric_snapshot.completion_rate:.2f}  "
        f"dropoff_risk={metric_snapshot.dropoff_risk_score:.2f}"
    )

    return {
        "metric_snapshot": metric_snapshot,
        "_monitor": monitor,
    }

def job_fetch_node(state: BridgeUpGraphState) -> dict:
    """
    Fetch real-time job opportunities based on learned skills
    """

    # ✅ Correct import based on your project
    from integrations.job_api_client import JobAPIClient

    client = JobAPIClient()

    # ── 1. Extract skills from tasks ──────────────────────────
    tasks = state.get("tasks", [])
    skills = set()

    for task in tasks:
        title = getattr(task, "title", "").lower()

        if "python" in title:
            skills.add("python")
        if "backend" in title:
            skills.add("backend developer")
        if "api" in title:
            skills.add("api developer")
        if "sql" in title:
            skills.add("sql")

    # fallback
    if not skills:
        skills = {"software developer"}

    # ── 2. Improve search queries (🔥 FIX for empty results) ──
    search_queries = set()

    # base strong queries (always work better with APIs)
    search_queries.update([
        "python developer",
        "backend developer",
        "software engineer"
    ])

    # add extracted skills
    for skill in skills:
        search_queries.add(skill)

    # ── 3. Fetch jobs ─────────────────────────────────────────
    all_jobs = []

    for query in search_queries:
        jobs = client.query_by_skill(query)
        all_jobs.extend(jobs)

    # ── 4. Deduplicate jobs (by URL) ───────────────────────────
    unique_jobs = {}
    for job in all_jobs:
        if job.url:
            unique_jobs[job.url] = job

    all_jobs = list(unique_jobs.values())

    # ── 5. Filter (India + Remote) ────────────────────────────
    filtered_jobs = []

    for job in all_jobs:
        if job.location:
            loc = job.location.lower()
            if "india" in loc or "remote" in loc:
                filtered_jobs.append(job)

    # limit results
    filtered_jobs = filtered_jobs[:10]

    # ── 6. Print (DEMO OUTPUT) ────────────────────────────────
    print("\n[job_fetch_node] Recommended Jobs:\n")

    if not filtered_jobs:
        print("⚠️ No jobs found (API may have returned empty results)\n")

    for i, job in enumerate(filtered_jobs, 1):
        print(f"{i}. {job.title} | {job.company}")
        print(f"   📍 {job.location}")
        print(f"   💰 {job.salary_range}")
        print(f"   🔗 {job.url}\n")

    print(f"💡 Based on your progress, {len(filtered_jobs)} opportunities found.\n")

    # ── 7. Return to state ────────────────────────────────────
    return {
        "job_recommendations": filtered_jobs
    }
# ── risk_eval_node ────────────────────────────────────────────────────────────

def risk_eval_node(state: BridgeUpGraphState) -> dict:
    """
    Queries RiskProfile and ExecutionSummary from the Monitoring Agent.
    Rule-based, no LLM. Only reads already-computed monitoring data.
    """
    from pathlib import Path

    session_id = state["session_id"]
    monitor    = state.get("_monitor") or MonitoringAgent(
        base_path=Path("data/monitoring_logs")
    )

    risk_profile      = monitor.get_risk_profile(session_id)
    execution_summary = monitor.get_execution_summary(session_id)

    print(
        f"\n[risk_eval_node] risk_level={risk_profile.risk_level!r}  "
        f"primary_issue={risk_profile.primary_issue!r}  "
        f"recommended_action={risk_profile.recommended_action!r}"
    )

    return {
        "risk_profile":      risk_profile,
        "execution_summary": execution_summary,
    }


# ── decision_node (Mock LLM) ──────────────────────────────────────────────────

def decision_node(state: BridgeUpGraphState) -> dict:
    import json

    cycles        = state["adaptation_cycles"]
    metrics       = state.get("metric_snapshot")
    current_strat = state["selected_strategy"]

    completion   = getattr(metrics, "completion_rate", 0.0) if metrics else 0.0
    dropoff_risk = getattr(metrics, "dropoff_risk_score", 0.0) if metrics else 0.0
    delay        = getattr(metrics, "average_delay_seconds", 0.0) if metrics else 0.0
    stability    = getattr(metrics, "stability_score", 0.0) if metrics else 0.0

    # ── 1. HARD CONVERGENCE ──────────────────────────────────
    if dropoff_risk < 0.25:
        decision = {
            "action": "continue",
            "new_strategy": None,
            "reason": f"System stabilized (risk={dropoff_risk:.2f})",
            "explanation": {
                "key_metrics": {
                    "completion_rate": completion,
                    "dropoff_risk": dropoff_risk,
                    "delay_index": delay
                },
                "decision_basis": "Dropoff risk below threshold",
                "expected_effect": "System will continue stable execution"
            }
        }

        print(f"\n[decision_node][FORCED CONTINUE] {json.dumps(decision, indent=2)}")

        return {
            "decision_action": decision["action"],
            "decision_reason": decision["reason"],
            "_prev_dropoff_risk": dropoff_risk,
        }

    # ── 2. TRY LLM ────────────────────────────────────────────
    try:
        decision = call_llm_decision(state)

        # Normalize strategy
        if decision.get("new_strategy") in ["null", "", "None"]:
            decision["new_strategy"] = None

        if decision["action"] not in ["continue", "replan", "adjust"]:
            raise ValueError("Invalid action from LLM")

        print(f"\n[decision_node][LLM] {json.dumps(decision, indent=2)}")

        # Ensure explanation exists
        if "explanation" not in decision:
            decision["explanation"] = {
                "key_metrics": {
                    "completion_rate": completion,
                    "dropoff_risk": dropoff_risk,
                    "delay_index": delay
                },
                "decision_basis": "LLM decision",
                "expected_effect": "System adapts"
            }

        # ── 🔧 CRITICAL FIX: ensure valid strategy ─────────────
        if decision["action"] == "replan" and decision["new_strategy"] is None:
            print("[decision_node] Fix: null strategy → assigning fallback")

            strategy_cycle = {
                "fast": "balanced",
                "balanced": "deep",
                "deep": "fast"
            }

            decision["new_strategy"] = strategy_cycle.get(current_strat, "balanced")

            decision["explanation"]["decision_basis"] += " | Fix: missing strategy"
            decision["explanation"]["expected_effect"] = "Fallback strategy ensures valid replanning"

        # ── 3. GUARDRAILS ─────────────────────────────────────

        if decision["action"] == "continue" and dropoff_risk >= 0.3:
            print("[decision_node] Override: high risk → replan")

            strategy_cycle = {
                "fast": "balanced",
                "balanced": "deep",
                "deep": "fast"
            }

            decision["action"] = "replan"
            decision["new_strategy"] = strategy_cycle.get(current_strat, "balanced")
            decision["reason"] = f"Override: dropoff risk ({dropoff_risk:.2f}) too high"

            decision["explanation"]["decision_basis"] += " | Override: high risk"
            decision["explanation"]["expected_effect"] = "Strategy change to reduce risk"

        if decision["action"] == "replan" and cycles >= 1:
            print("[decision_node] Override: avoid loop → adjust")

            decision["action"] = "adjust"
            decision["new_strategy"] = None
            decision["reason"] = "Override: repeated replan avoided"

            decision["explanation"]["decision_basis"] += " | Override: loop prevention"
            decision["explanation"]["expected_effect"] = "Rescheduling improves execution"

    except Exception as e:
        print(f"\n[decision_node] LLM failed → fallback. Error: {e}")

        strategy_cycle = {
            "fast": "balanced",
            "balanced": "deep",
            "deep": "fast"
        }

        if cycles >= 1:
            decision = {
                "action": "adjust",
                "new_strategy": None,
                "reason": "No improvement → adjust",
                "explanation": {
                    "key_metrics": {
                        "completion_rate": completion,
                        "dropoff_risk": dropoff_risk,
                        "delay_index": delay
                    },
                    "decision_basis": "Repeated failure",
                    "expected_effect": "Reschedule improves execution"
                }
            }
        else:
            decision = {
                "action": "replan",
                "new_strategy": strategy_cycle.get(current_strat, "balanced"),
                "reason": "High dropoff risk",
                "explanation": {
                    "key_metrics": {
                        "completion_rate": completion,
                        "dropoff_risk": dropoff_risk,
                        "delay_index": delay
                    },
                    "decision_basis": "Risk threshold exceeded",
                    "expected_effect": "Strategy improves engagement"
                }
            }

    # ── EXPLANATION PRINT ────────────────────────────────────
    exp = decision.get("explanation", {})
    print("\n[EXPLANATION]")
    print(f"• Metrics: {exp.get('key_metrics')}")
    print(f"• Reason: {exp.get('decision_basis')}")
    print(f"• Expected Effect: {exp.get('expected_effect')}")

    # ── STATE UPDATE ─────────────────────────────────────────
    updates = {
        "decision_action": decision["action"],
        "decision_reason": decision["reason"],
        "_prev_dropoff_risk": dropoff_risk,
    }

    if decision["action"] == "replan":
        updates["selected_strategy"] = decision["new_strategy"]
        updates["adaptation_cycles"] = cycles + 1

    elif decision["action"] == "adjust":
        updates["adaptation_cycles"] = cycles + 1

    return updates


# =============================================================================
# 3. CONDITIONAL ROUTER
# =============================================================================

def route_after_decision(state: BridgeUpGraphState) -> str:
    """
    Routes from decision_node based on LLM output + loop guard.
    """
    action = state["decision_action"]
    cycles = state["adaptation_cycles"]

    if cycles >= 3:
        print(f"\n[router] Loop guard hit (cycles={cycles}) → END")
        return END

    if action == "replan":
        print(f"\n[router] action=replan (cycles={cycles}) → plan_node")
        return "plan_node"

    if action == "adjust":
        print(f"\n[router] action=adjust (cycles={cycles}) → action_node")
        return "action_node"

    print(f"\n[router] action=continue → END")
    return END


# =============================================================================
# 4. GRAPH CONSTRUCTION
# =============================================================================

def build_graph() -> StateGraph:
    graph = StateGraph(BridgeUpGraphState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("strategy_node",  strategy_node)
    graph.add_node("plan_node",      plan_node)
    graph.add_node("action_node",    action_node)
    graph.add_node("monitor_node",   monitor_node)
    graph.add_node("job_fetch_node", job_fetch_node)
    graph.add_node("risk_eval_node", risk_eval_node)
    graph.add_node("decision_node",  decision_node)
    

    # ── Fixed edges ───────────────────────────────────────────────────────────
    graph.set_entry_point("strategy_node")
    graph.add_edge("strategy_node",  "plan_node")
    graph.add_edge("plan_node",      "action_node")
    graph.add_edge("action_node", "monitor_node")
    graph.add_edge("monitor_node",   "job_fetch_node")
    graph.add_edge("job_fetch_node", "risk_eval_node")
    graph.add_edge("risk_eval_node", "decision_node")

    # ── Conditional edge from decision_node ───────────────────────────────────
    graph.add_conditional_edges(
        "decision_node",
        route_after_decision,
        {
            "plan_node":   "plan_node",
            "action_node": "action_node",
            END:            END,
        },
    )

    return graph.compile()


def call_llm_decision(state: BridgeUpGraphState) -> dict:
    import json

    strategy = state["selected_strategy"]
    metrics  = state.get("metric_snapshot")
    cycles   = state["adaptation_cycles"]

    completion = getattr(metrics, "completion_rate", 0.0) if metrics else 0.0
    delay      = getattr(metrics, "average_delay_seconds", 0.0) if metrics else 0.0
    dropoff    = getattr(metrics, "dropoff_risk_score", 0.0) if metrics else 0.0
    stability  = getattr(metrics, "stability_score", 0.0) if metrics else 0.0

    prompt = f"""
You are an adaptive learning system.

IMPORTANT RULES:
- If dropoff risk >= 0.3 → DO NOT choose "continue"
- If performance improves → prefer "continue"

Given:

- current strategy: {strategy}
- completion rate: {completion:.2f}
- delay index: {delay:.2f}
- dropoff risk: {dropoff:.2f}
- stability score: {stability:.2f}
- iteration count: {cycles}

Return ONLY valid JSON:

{{
"action": "continue | replan | adjust",
"new_strategy": "fast | balanced | deep | null",
"reason": "short explanation",
"explanation": {{
    "key_metrics": {{
        "completion_rate": {completion:.2f},
        "dropoff_risk": {dropoff:.2f},
        "delay_index": {delay:.2f}
    }},
    "decision_basis": "why this action was chosen",
    "expected_effect": "what improvement is expected"
}}
}}
"""

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    text = response.choices[0].message.content.strip()
    return json.loads(text)