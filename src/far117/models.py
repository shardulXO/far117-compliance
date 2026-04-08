from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Violation(BaseModel):
    type: str
    severity: str
    date: str
    duty_id: str = ""
    details: str = ""
    regulation: str = ""


class ScheduleInput(BaseModel):
    version: str = "1.0"
    crew_member: Dict[str, Any] = Field(default_factory=dict)
    schedule_period: Dict[str, str] = Field(default_factory=dict)
    duties: List[Dict[str, Any]] = Field(default_factory=list)
    prior_duties_context: List[Dict[str, Any]] = Field(default_factory=list)


class FAR117Observation(BaseModel):
    schedule: Any
    step: int = 0
    done: bool = False
    reward: float = 0.0
    feedback: str = ""


class FAR117Action(BaseModel):
    violations: List[Any] = Field(default_factory=list)
    overall_compliant: bool = True
    explanation: str = ""


class FAR117State(BaseModel):
    task_id: str = ""
    ground_truth_violations: List[Any] = Field(default_factory=list)
    agent_report: Optional[Dict[str, Any]] = None
    agent_score: Optional[float] = None
