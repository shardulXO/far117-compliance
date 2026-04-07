from typing import List, Optional
from pydantic import BaseModel, Field


class CrewMember(BaseModel):
    id: str
    role: str
    base: str
    home_timezone: str


class Flight(BaseModel):
    flight_number: str
    departure: str
    arrival: str
    origin: str
    destination: str


class RestPeriod(BaseModel):
    start: str
    end: str
    location: str
    is_hotel_rest: bool = False


class Duty(BaseModel):
    duty_id: str
    date: str
    type: str
    duty_start: str
    duty_end: str
    departure_airport: str
    arrival_airport: str
    flights: List[Flight] = Field(default_factory=list)
    rest_period: Optional[RestPeriod] = None


class ScheduleInput(BaseModel):
    version: str = "1.0"
    crew_member: CrewMember
    schedule_period: dict
    duties: List[Duty]
    prior_duties_context: List[dict] = Field(default_factory=list)


class Violation(BaseModel):
    type: str
    severity: str
    date: str
    duty_id: str
    details: str
    regulation: str


class FAR117Observation(BaseModel):
    schedule: ScheduleInput
    step: int
    done: bool
    feedback: str = ""


class FAR117Action(BaseModel):
    violations: List[Violation] = Field(default_factory=list)
    overall_compliant: bool
    explanation: str = ""


class FAR117State(BaseModel):
    task_id: str
    ground_truth_violations: List[Violation]
    agent_report: Optional[FAR117Action] = None
