import os
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, Field

from .models import FAR117Observation, FAR117Action, FAR117State
from . import tasks, rules, grader


class StepResult:
    def __init__(
        self,
        observation: FAR117Observation,
        reward: float,
        done: bool,
        info: Dict[str, Any],
    ):
        self.observation = observation
        self.reward = reward
        self.done = done
        self.info = info


class FAR117Env:
    def __init__(self, task_id: str = "easy_single_day"):
        self.task_id = task_id
        self._state: Optional[FAR117State] = None
        self._schedule: Dict[str, Any] = {}
        self._ground_truth: list = []
        self._step_count: int = 0
        self._done: bool = False
        self._expected_violations: int = 0
        self._agent_score: Optional[float] = None

    def reset(self, task_id: Optional[str] = None) -> FAR117Observation:
        if task_id:
            self.task_id = task_id
        self._step_count = 0
        self._done = False
        self._agent_score = None

        task_config = tasks.get_task(self.task_id)
        schedule = task_config["schedule"]
        self._schedule = (
            schedule.model_dump() if hasattr(schedule, "model_dump") else schedule
        )
        self._ground_truth = task_config.get("ground_truth", [])
        self._expected_violations = task_config.get("expected_violations", 0)

        self._state = FAR117State(
            task_id=self.task_id,
            ground_truth_violations=self._ground_truth,
            agent_report=None,
        )

        observation = FAR117Observation(
            schedule=self._schedule,
            step=0,
            done=False,
            feedback="Please audit the provided pilot schedule for FAR 117 compliance violations.",
        )
        return observation

    def step(
        self, action: FAR117Action
    ) -> Tuple[FAR117Observation, float, bool, Dict[str, Any]]:
        if self._done:
            return (
                FAR117Observation(
                    schedule=self._schedule,
                    step=self._step_count,
                    done=True,
                    feedback="Episode already finished",
                ),
                0.0,
                True,
                {"error": "Episode already done"},
            )

        self._step_count += 1

        agent_report = {
            "violations": [
                v.model_dump() if hasattr(v, "model_dump") else v
                for v in action.violations
            ],
            "overall_compliant": action.overall_compliant,
        }

        self._state.agent_report = agent_report

        score, reward, feedback = grader.grade_submission(
            agent_report=agent_report,
            ground_truth_violations=self._ground_truth,
            ground_truth_compliant=len(self._ground_truth) == 0,
        )

        self._agent_score = score
        self._done = True

        observation = FAR117Observation(
            schedule=self._schedule,
            step=self._step_count,
            done=True,
            reward=reward,
            feedback=feedback,
        )

        info = {
            "score": score,
            "feedback": feedback,
            "expected_violations": self._expected_violations,
        }

        return observation, reward, True, info

    def state(self) -> Optional[FAR117State]:
        if self._state:
            self._state.agent_score = self._agent_score
        return self._state
