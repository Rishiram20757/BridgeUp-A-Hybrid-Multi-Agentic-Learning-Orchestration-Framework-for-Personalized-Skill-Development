# bridgeup/events/validator.py

import json
from datetime import timedelta
from typing import Dict, Any

from .schema import (
    Event,
    EventType,
    AgentName,
    EVENT_SCHEMA_VERSION,
)


# ============================================================
# Exception
# ============================================================

class EventValidationError(Exception):
    """Raised when an event violates schema or payload rules."""
    pass


# ============================================================
# Event Payload Schemas
# ============================================================

EVENT_PAYLOAD_SCHEMAS: Dict[EventType, Dict[str, Any]] = {
    EventType.SESSION_STARTED: {
        "required": ["user_id"],
        "optional": [],
    },
    EventType.PLAN_READY: {
        "required": ["plan_id", "total_tasks"],
        "optional": [],
    },
    EventType.EXECUTION_STARTED: {
        "required": ["plan_id"],
        "optional": [],
    },
    EventType.SESSION_ENDED: {
        "required": ["status"],
        "optional": ["reason"],
    },
    EventType.ERROR: {
        "required": ["error_message"],
        "optional": ["error_code"],
    },
    EventType.TASK_CREATED: {
        "required": ["task_id", "task_name"],
        "optional": ["deadline"],
    },
    EventType.TASK_STARTED: {
        "required": ["task_id"],
        "optional": [],
    },
    EventType.TASK_COMPLETED: {
        "required": ["task_id"],
        "optional": ["completion_time"],
    },
    EventType.TASK_MISSED: {
        "required": ["task_id"],
        "optional": ["reason"],
    },
    EventType.TASK_RESCHEDULED: {
        "required": ["task_id", "new_deadline"],
        "optional": [],
    },
    EventType.METRICS_COMPUTED: {
        "required": ["completion_rate"],
        "optional": ["focus_score", "efficiency_score"],
    },
}


# ============================================================
# Public Validator
# ============================================================

def validate_event(event: Event) -> None:
    """
    Validates an Event object.

    Raises:
        EventValidationError if validation fails.
    """

    _validate_structure(event)
    _validate_version(event)
    _validate_timestamp(event)
    _validate_agent(event)
    _validate_event_type(event)
    _validate_payload_schema(event)
    _validate_json_serializable(event)


# ============================================================
# Validation Layers
# ============================================================

def _validate_structure(event: Event) -> None:
    if not event.session_id or not isinstance(event.session_id, str):
        raise EventValidationError("session_id must be a non-empty string")

    if not isinstance(event.payload, dict):
        raise EventValidationError("payload must be a dictionary")

    if not isinstance(event.metadata, dict):
        raise EventValidationError("metadata must be a dictionary")


def _validate_version(event: Event) -> None:
    if event.version != EVENT_SCHEMA_VERSION:
        raise EventValidationError(
            f"Invalid event version: {event.version}. "
            f"Expected {EVENT_SCHEMA_VERSION}"
        )


def _validate_timestamp(event: Event) -> None:
    if event.timestamp.tzinfo is None:
        raise EventValidationError("timestamp must be timezone-aware (UTC)")

    if event.timestamp.utcoffset() != timedelta(0):
        raise EventValidationError("timestamp must be UTC")


def _validate_agent(event: Event) -> None:
    valid_agents = {a.value for a in AgentName}
    if event.agent not in valid_agents:
        raise EventValidationError(
            f"Invalid agent '{event.agent}'. Must be one of {valid_agents}"
        )


def _validate_event_type(event: Event) -> None:
    if not isinstance(event.event_type, EventType):
        raise EventValidationError(
            "event_type must be an instance of EventType enum"
        )


def _validate_payload_schema(event: Event) -> None:
    if event.event_type not in EVENT_PAYLOAD_SCHEMAS:
        raise EventValidationError(
            f"No payload schema defined for event type {event.event_type}"
        )

    schema = EVENT_PAYLOAD_SCHEMAS[event.event_type]
    required_fields = schema.get("required", [])

    for field in required_fields:
        if field not in event.payload:
            raise EventValidationError(
                f"Missing required payload field '{field}' "
                f"for event {event.event_type.value}"
            )

        if event.payload[field] is None:
            raise EventValidationError(
                f"Payload field '{field}' cannot be None "
                f"for event {event.event_type.value}"
            )


def _validate_json_serializable(event: Event) -> None:
    try:
        json.dumps(event.payload)
        json.dumps(event.metadata)
    except (TypeError, ValueError) as e:
        raise EventValidationError(
            f"Payload or metadata is not JSON serializable: {str(e)}"
        )