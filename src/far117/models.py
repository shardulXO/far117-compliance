from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Violation(BaseModel):
    type: str
    severity: str
    date: str
    duty_id: str = ""
    details: str = ""
    regulation: str = ""


class FAR117Observation(BaseModel):
    schedule: Dict[str, Any] = Field(default_factory=dict)
    step: int = 0
    done: bool = False
    reward: float = 0.0
    feedback: str = ""


class FAR117Action(BaseModel):
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    overall_compliant: bool = True
    explanation: str = ""


class FAR117State(BaseModel):
    task_id: str = ""
    ground_truth_violations: List[Dict[str, Any]] = Field(default_factory=list)
    agent_report: Optional[Dict[str, Any]] = None
    agent_score: Optional[float] = None
