from typing import Any, Dict, List

TASKS = {
    "easy_single_day": {
        "task_id": "easy_single_day",
        "description": "Single pilot, single day",
        "ground_truth": [],
    },
    "medium_3day": {
        "task_id": "medium_3day",
        "description": "3-day rotation with violations",
        "ground_truth": [
            {"type": "duty_period_exceeded", "date": "2024-03-15", "duty_id": "D1"},
        ],
    },
    "hard_30day": {
        "task_id": "hard_30day",
        "description": "30-day cumulative with violations",
        "ground_truth": [
            {
                "type": "duty_period_exceeded",
                "date": f"2024-03-{d:02d}",
                "duty_id": f"D{d}",
            }
            for d in range(1, 11)
        ],
    },
}

GRADERS = {
    "easy_single_day": "grader:grade_easy",
    "medium_3day": "grader:grade_medium",
    "hard_30day": "grader:grade_hard",
}


def list_tasks() -> List[str]:
    return list(TASKS.keys())


def get_task(task_id: str) -> Dict[str, Any]:
    return TASKS[task_id]


def get_grader(task_id: str) -> str:
    return GRADERS.get(task_id, "grader:grade")
