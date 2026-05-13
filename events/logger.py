# BridgeUp/events/logger.py

import json
import os
import threading
from pathlib import Path
from datetime import timezone

from .schema import Event


# ============================================================
# Internal Lock (Thread Safety)
# ============================================================

_file_lock = threading.Lock()


# ============================================================
# Public API
# ============================================================

def append_event(event: Event) -> None:
    """
    Appends a validated Event to the session JSONL file.

    This function must never raise fatal exceptions.
    """

    try:
        event_dict = _serialize_event(event)
        file_path = _get_session_file_path(event.session_id)

        with _file_lock:
            _ensure_directory(file_path.parent)
            _write_line(file_path, event_dict)

    except Exception as e:
        _write_fallback_error(e, event)


# ============================================================
# Internal Helpers
# ============================================================

def _get_session_file_path(session_id: str) -> Path:
    base_dir = Path("data") / "events"
    return base_dir / f"session_{session_id}.jsonl"


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _serialize_event(event: Event) -> dict:
    """
    Convert Event object into JSON-serializable dictionary.
    """

    return {
        "event_id": str(event.event_id),
        "version": event.version,
        "timestamp": event.timestamp.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "session_id": event.session_id,
        "agent": event.agent,
        "event_type": event.event_type.value,
        "payload": event.payload,
        "metadata": event.metadata,
    }


def _write_line(file_path: Path, event_dict: dict) -> None:
    """
    Append single JSON line safely and durably.
    """

    line = json.dumps(event_dict, separators=(",", ":"))

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def _write_fallback_error(error: Exception, event: Event) -> None:
    """
    Fallback logging if primary write fails.
    """

    try:
        fallback_path = Path("data") / "events" / "fallback_errors.log"
        fallback_path.parent.mkdir(parents=True, exist_ok=True)

        with open(fallback_path, "a", encoding="utf-8") as f:
            f.write(
                f"[LOGGER ERROR] {str(error)} | Event: {str(event)}\n"
            )
    except Exception:
        # Last-resort silent fail — must never crash system
        pass