import os
from typing import Optional
from dataclasses import dataclass
from .models import FAR117Observation, FAR117Action, FAR117State
from . import tasks, rules, grader


@dataclass
class StepResult:
    observation: FAR117Observation
    reward: float
    done: bool
    info: dict


class FAR117Env:
    def __init__(self, task_id: str = "easy_single_day"):
        self.task_id = task_id
        self._state = None
        self._step_count = 0
        self._done = False
        task_config = tasks.get_task(task_id)
        self._schedule = task_config["schedule"]
        self._ground_truth = rules.compute_ground_truth(self._schedule)
        self._expected_violations = task_config["expected_violations"]
        self._state = FAR117State(
            task_id=task_id,
            ground_truth_violations=self._ground_truth,
            agent_report=None,
        )

    @classmethod
    async def from_docker_image(cls, image_name: Optional[str] = None) -> "FAR117Env":
        task_id = os.getenv("FAR117_TASK", "easy_single_day")
        return cls(task_id=task_id)

    async def reset(self) -> StepResult:
        self._step_count = 0
        self._done = False
        task_config = tasks.get_task(self.task_id)
        self._schedule = task_config["schedule"]
        self._ground_truth = rules.compute_ground_truth(self._schedule)
        self._state = FAR117State(
            task_id=self.task_id,
            ground_truth_violations=self._ground_truth,
            agent_report=None,
        )
        observation = FAR117Observation(
            schedule=self._schedule, step=0, done=False, feedback=self._build_feedback()
        )
        return StepResult(
            observation=observation,
            reward=0.0,
            done=False,
            info={
                "task_id": self.task_id,
                "expected_violations": self._expected_violations,
            },
        )

    async def step(self, action: FAR117Action) -> StepResult:
        if self._done:
            raise RuntimeError("Episode already done")
        self._step_count += 1
        self._state.agent_report = action
        reward = grader.compute_reward(action, self._ground_truth, self._step_count)
        self._done = True
        score, grading_details = grader.grade_report(action, self._ground_truth)
        observation = FAR117Observation(
            schedule=self._schedule,
            step=self._step_count,
            done=True,
            feedback=grading_details,
        )
        return StepResult(
            observation=observation,
            reward=reward,
            done=True,
            info={"score": score, "grading_details": grading_details},
        )

    async def state(self) -> FAR117State:
        return self._state

    async def close(self):
        pass

    def _build_feedback(self) -> str:
        if not self._ground_truth:
            return "No violations expected."
        return f"Expected violations ({len(self._ground_truth)} total): " + ", ".join(
            [f"{v.date}: {v.type}" for v in self._ground_truth]
        )
