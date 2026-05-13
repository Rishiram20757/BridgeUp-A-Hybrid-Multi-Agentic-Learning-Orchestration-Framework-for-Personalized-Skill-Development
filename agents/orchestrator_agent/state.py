
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import time


# =========================
# ENUMS
# =========================

class WorkflowStage(str, Enum):
    INIT = "INIT"
    VALIDATED = "VALIDATED"
    PLANNING = "PLANNING"
    PLAN_READY = "PLAN_READY"
    EXECUTING = "EXECUTING"
    EXECUTION_ACTIVE = "EXECUTION_ACTIVE"
    MONITORING = "MONITORING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class PlanningStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExecutionStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    STARTING = "STARTING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MonitoringStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# =========================
# ERROR MODEL
# =========================

@dataclass
class ErrorRecord:
    stage: str
    agent: str
    error_type: str
    message: str
    timestamp: float
    retry_count: int = 0


# =========================
# SUB-STATES
# =========================

@dataclass
class PlanningState:
    input_payload: Optional[Dict[str, Any]] = None
    roadmap_options: Optional[Dict[str, Any]] = None
    selected_strategy: Optional[str] = None
    weekly_schedule: Optional[List[Any]] = None
    explainability_notes: Optional[Dict[str, Any]] = None
    planning_status: PlanningStatus = PlanningStatus.NOT_STARTED


from typing import Optional, List, Dict

@dataclass
class ExecutionState:
    execution_status: ExecutionStatus = ExecutionStatus.NOT_STARTED
    active_plan_id: Optional[str] = None
    started_at: Optional[float] = None
    progress_metrics: Optional[Dict] = None
    last_action_response: Optional[Dict] = None

    # Action Agent fields
    tasks: Optional[List] = None
    schedule_blocks: Optional[List] = None
    progress_snapshot: Optional[Dict] = None


@dataclass
class MonitoringState:
    monitoring_status: MonitoringStatus = MonitoringStatus.NOT_STARTED
    last_evaluation_timestamp: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    adaptation_triggered: bool = False
    monitoring_report: Optional[Dict[str, Any]] = None


# =========================
# SESSION STATE
# =========================

@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    last_updated_at: float = field(default_factory=time.time)

    workflow_type: Optional[str] = None
    current_stage: WorkflowStage = WorkflowStage.INIT
    version: int = 1

    planning_state: PlanningState = field(default_factory=PlanningState)
    execution_state: ExecutionState = field(default_factory=ExecutionState)
    monitoring_state: MonitoringState = field(default_factory=MonitoringState)

    request_history: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[ErrorRecord] = field(default_factory=list)

    # =====================================================
    # NEW — LLM RESOURCE INTELLIGENCE OUTPUTS (ADVISORY)
    # =====================================================

    llm_ranked_resources: Optional[Any] = None
    llm_learning_plan: Optional[Any] = None

    # =====================================================

    def update_timestamp(self):
        self.last_updated_at = time.time()