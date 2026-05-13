# bridgeup/events/schema.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID


# ============================================================
# Schema Version
# ============================================================

EVENT_SCHEMA_VERSION: str = "1.0"


# ============================================================
# Event Types
# ============================================================

class EventType(str, Enum):
    """
    Canonical list of all valid system events.

    RULES:
    - Never remove existing types.
    - Only append new types.
    - Names must remain stable.
    """

    # --- Orchestrator Events ---
    SESSION_STARTED = "SESSION_STARTED"
    PLAN_READY = "PLAN_READY"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    SESSION_ENDED = "SESSION_ENDED"
    ERROR = "ERROR"

    # --- Action Agent Events ---
    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_MISSED = "TASK_MISSED"
    TASK_RESCHEDULED = "TASK_RESCHEDULED"

    # --- Monitoring Events ---
    METRICS_COMPUTED = "METRICS_COMPUTED"


# ============================================================
# Canonical Agent Names
# ============================================================

class AgentName(str, Enum):
    """
    Canonical agent identifiers.

    Agents must never hardcode strings.
    Always use this enum via emitter wrappers.
    """

    ORCHESTRATOR = "orchestrator"
    ACTION_AGENT = "action_agent"
    MONITORING_AGENT = "monitoring_agent"


# ============================================================
# Event Model
# ============================================================

@dataclass(frozen=True)
class Event:
    """
    Immutable event model.

    Properties:
    - Deterministic
    - Append-only
    - Session-scoped
    - Machine-readable
    """

    event_id: UUID
    version: str
    timestamp: datetime
    session_id: str
    agent: str
    event_type: EventType
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)