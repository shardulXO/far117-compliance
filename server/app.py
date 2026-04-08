from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys

sys.path.insert(0, "/app")
from src.far117 import FAR117Env, FAR117Action

app = FastAPI(title="FAR 117 Compliance")
_current_env = None


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    violations: list = []
    overall_compliant: bool = False
    explanation: str = ""


@app.get("/")
async def root():
    return {
        "message": "FAR 117 Compliance API",
        "endpoints": ["/ping", "/info", "/reset", "/step"],
    }


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/info")
async def info():
    return {
        "name": "far117_compliance",
        "tasks": ["easy_single_day", "medium_3day", "hard_30day"],
    }


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()):
    global _current_env
    task_id = request.task_id or os.getenv("FAR117_TASK", "easy_single_day")
    _current_env = FAR117Env(task_id=task_id)
    result = await _current_env.reset()
    return {
        "observation": {
            "schedule": result.observation.schedule.model_dump(),
            "step": result.observation.step,
            "done": result.observation.done,
            "feedback": result.observation.feedback,
        },
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.post("/step")
async def step(request: StepRequest):
    global _current_env
    from src.far117.models import Violation

    violations = [
        Violation(**v) if isinstance(v, dict) else v for v in request.violations
    ]
    action = FAR117Action(
        violations=violations,
        overall_compliant=request.overall_compliant,
        explanation=request.explanation,
    )
    result = await _current_env.step(action)
    return {
        "observation": {
            "schedule": result.observation.schedule.model_dump(),
            "step": result.observation.step,
            "done": result.observation.done,
            "feedback": result.observation.feedback,
        },
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }
