from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
import sys

if os.path.exists("/app"):
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, ".")

from far117.environment import FAR117Env
from far117.models import FAR117Action

app = FastAPI(title="FAR 117 Compliance API")
_current_env: Optional[FAR117Env] = None


class ResetRequest(BaseModel):
    task_id: Optional[str] = "hard_30day"


class StepRequest(BaseModel):
    violations: List[Dict[str, Any]] = []
    overall_compliant: bool = False
    explanation: str = ""


@app.get("/")
async def root():
    return {
        "message": "FAR 117 Compliance API",
        "endpoints": ["/ping", "/info", "/reset", "/step", "/state"],
    }


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/info")
async def info():
    return {
        "name": "far117_compliance",
        "version": "1.0.0",
        "tasks": ["easy_single_day", "medium_3day", "hard_30day"],
    }


@app.get("/state")
async def get_state():
    global _current_env
    if _current_env is None:
        raise HTTPException(
            status_code=400, detail="Environment not initialized. Call /reset first."
        )
    current_state = _current_env.state()
    return {
        "task_id": current_state.task_id,
        "ground_truth_violations": current_state.ground_truth_violations,
        "agent_report": current_state.agent_report,
        "agent_score": current_state.agent_score,
    }


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()):
    global _current_env
    task_id = request.task_id or os.getenv("FAR117_TASK", "hard_30day")
    _current_env = FAR117Env(task_id=task_id)
    observation = _current_env.reset(task_id=task_id)
    return {
        "observation": observation.model_dump(),
        "state": _current_env.state().model_dump() if _current_env.state() else None,
    }


@app.post("/step")
async def step(request: StepRequest):
    global _current_env
    if _current_env is None:
        raise HTTPException(
            status_code=400, detail="Environment not initialized. Call /reset first."
        )

    action = FAR117Action(
        violations=request.violations,
        overall_compliant=request.overall_compliant,
        explanation=request.explanation,
    )

    observation, reward, done, info = _current_env.step(action)

    return {
        "observation": observation.model_dump(),
        "reward": reward,
        "done": done,
        "info": info,
        "state": _current_env.state().model_dump() if _current_env.state() else None,
    }


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
