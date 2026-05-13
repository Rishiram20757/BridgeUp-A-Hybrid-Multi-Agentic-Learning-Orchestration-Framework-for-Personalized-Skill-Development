# BridgeUp/events/emitter.py

from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .schema import (
    Event,
    EventType,
    AgentName,
    EVENT_SCHEMA_VERSION,
)
from .validator import validate_event, EventValidationError
from .logger import append_event


# ============================================================
# Public Wrapper APIs (Agent-Safe)
# ============================================================

def emit_orchestrator_event(
    event_type: EventType,
    session_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    _emit_event_internal(
        agent=AgentName.ORCHESTRATOR,
        event_type=event_type,
        session_id=session_id,
        payload=payload,
        metadata=metadata,
    )


def emit_action_event(
    event_type: EventType,
    session_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    _emit_event_internal(
        agent=AgentName.ACTION_AGENT,
        event_type=event_type,
        session_id=session_id,
        payload=payload,
        metadata=metadata,
    )


def emit_monitoring_event(
    event_type: EventType,
    session_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    _emit_event_internal(
        agent=AgentName.MONITORING_AGENT,
        event_type=event_type,
        session_id=session_id,
        payload=payload,
        metadata=metadata,
    )


# ============================================================
# Core Internal Emitter
# ============================================================

def _emit_event_internal(
    agent: AgentName,
    event_type: EventType,
    session_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, Any]],
) -> None:
    """
    Core event emission pipeline.

    Responsibilities:
    - Construct Event object
    - Validate event
    - Append to log
    - Never crash caller
    """

    try:
        event = Event(
            event_id=uuid4(),
            version=EVENT_SCHEMA_VERSION,
            timestamp=datetime.now(timezone.utc),
            session_id=session_id,
            agent=agent.value,
            event_type=event_type,
            payload=payload,
            metadata=metadata or {},
        )

        validate_event(event)
        append_event(event)

    except EventValidationError as ve:
        # Validation failure — do not crash agent
        print(f"[EVENT VALIDATION ERROR] {ve}")

    except Exception as e:
        # Absolute safety net — must never break agents
        print(f"[EVENT SYSTEM ERROR] {e}")