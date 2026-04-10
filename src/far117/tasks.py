from typing import Any, Dict, List


def create_easy_single_day() -> Dict[str, Any]:
    return {
        "version": "1.0",
        "crew_member": {"id": "P001", "role": "captain", "base": "ORD"},
        "schedule_period": {"start_date": "2024-03-15", "end_date": "2024-03-15"},
        "duties": [
            {
                "duty_id": "D1",
                "date": "2024-03-15",
                "type": "flight_duty",
                "duty_start": "05:00",
                "duty_end": "17:00",
                "departure_airport": "ORD",
                "arrival_airport": "LAX",
                "flights": [
                    {
                        "flight_number": "AA101",
                        "departure": "06:00",
                        "arrival": "08:15",
                    },
                    {
                        "flight_number": "AA102",
                        "departure": "09:30",
                        "arrival": "10:45",
                    },
                    {
                        "flight_number": "AA103",
                        "departure": "12:00",
                        "arrival": "13:15",
                    },
                    {
                        "flight_number": "AA104",
                        "departure": "14:30",
                        "arrival": "16:45",
                    },
                ],
                "rest_period": {
                    "start": "17:00",
                    "end": "23:00",
                    "is_hotel_rest": False,
                },
            }
        ],
    }


def create_medium_3day() -> Dict[str, Any]:
    return {
        "version": "1.0",
        "crew_member": {"id": "P002", "role": "first_officer", "base": "DFW"},
        "schedule_period": {"start_date": "2024-03-15", "end_date": "2024-03-17"},
        "duties": [
            {
                "duty_id": "D1",
                "date": "2024-03-15",
                "type": "flight_duty",
                "duty_start": "05:00",
                "duty_end": "16:00",
                "departure_airport": "DFW",
                "arrival_airport": "LAX",
                "flights": [
                    {
                        "flight_number": "AA301",
                        "departure": "06:00",
                        "arrival": "07:30",
                    },
                    {
                        "flight_number": "AA302",
                        "departure": "09:00",
                        "arrival": "10:15",
                    },
                    {
                        "flight_number": "AA303",
                        "departure": "12:00",
                        "arrival": "13:15",
                    },
                ],
                "rest_period": {
                    "start": "16:00",
                    "end": "01:00",
                    "is_hotel_rest": True,
                },
            },
            {
                "duty_id": "D2",
                "date": "2024-03-16",
                "type": "flight_duty",
                "duty_start": "10:00",
                "duty_end": "22:00",
                "departure_airport": "LAX",
                "arrival_airport": "JFK",
                "flights": [
                    {
                        "flight_number": "AA304",
                        "departure": "11:00",
                        "arrival": "19:00",
                    },
                    {
                        "flight_number": "AA305",
                        "departure": "20:00",
                        "arrival": "21:30",
                    },
                ],
                "rest_period": {
                    "start": "22:00",
                    "end": "06:00",
                    "is_hotel_rest": True,
                },
            },
            {
                "duty_id": "D3",
                "date": "2024-03-17",
                "type": "flight_duty",
                "duty_start": "14:00",
                "duty_end": "23:00",
                "departure_airport": "BOS",
                "arrival_airport": "DFW",
                "flights": [
                    {"flight_number": "AA306", "departure": "15:00", "arrival": "17:30"}
                ],
                "rest_period": {
                    "start": "23:00",
                    "end": "08:00",
                    "is_hotel_rest": False,
                },
            },
        ],
    }


def create_hard_30day() -> Dict[str, Any]:
    duties = []
    for day in range(1, 4):
        duties.append(
            {
                "duty_id": f"D{day}",
                "date": f"2024-03-{day:02d}",
                "type": "flight_duty",
                "duty_start": "04:00",
                "duty_end": "16:00",
                "departure_airport": "DFW",
                "arrival_airport": "LAX",
                "flights": [
                    {
                        "flight_number": f"AA{day}",
                        "departure": "05:00",
                        "arrival": "08:00",
                    }
                ],
                "rest_period": {
                    "start": "16:00",
                    "end": "23:00",
                    "is_hotel_rest": True,
                },
            }
        )
    for day in range(4, 16):
        duties.append(
            {
                "duty_id": f"D{day}",
                "date": f"2024-03-{day:02d}",
                "type": "flight_duty",
                "duty_start": "03:00",
                "duty_end": "15:00",
                "departure_airport": "LAX",
                "arrival_airport": "ORD",
                "flights": [
                    {
                        "flight_number": f"AA{day}",
                        "departure": "04:00",
                        "arrival": "10:00",
                    }
                ],
                "rest_period": {
                    "start": "15:00",
                    "end": "22:00",
                    "is_hotel_rest": True,
                },
            }
        )
    for day in range(16, 31):
        duties.append(
            {
                "duty_id": f"D{day}",
                "date": f"2024-03-{day:02d}",
                "type": "flight_duty",
                "duty_start": "20:00",
                "duty_end": "08:00",
                "departure_airport": "ORD",
                "arrival_airport": "NRT",
                "flights": [
                    {
                        "flight_number": f"AA{day}",
                        "departure": "21:00",
                        "arrival": "23:00",
                    }
                ],
                "rest_period": {
                    "start": "08:00",
                    "end": "18:00",
                    "is_hotel_rest": True,
                },
            }
        )
    return {
        "version": "1.0",
        "crew_member": {"id": "P003", "role": "captain", "base": "DFW"},
        "schedule_period": {"start_date": "2024-03-01", "end_date": "2024-03-31"},
        "duties": duties,
    }


TASKS = {
    "easy_single_day": {
        "schedule": create_easy_single_day(),
        "task_id": "easy_single_day",
        "description": "Single pilot, single day",
        "expected_violations": 1,
        "ground_truth": [
            {
                "type": "duty_period_exceeded",
                "severity": "critical",
                "date": "2024-03-15",
                "duty_id": "D1",
                "details": "FDP 12.0h exceeds max 11.0h",
                "regulation": "117.5(b)",
            }
        ],
        "grader": {"type": "python", "entry_point": "grader:grade_easy"},
    },
    "medium_3day": {
        "schedule": create_medium_3day(),
        "task_id": "medium_3day",
        "description": "3-day rotation with violations",
        "expected_violations": 2,
        "ground_truth": [
            {
                "type": "duty_period_exceeded",
                "severity": "critical",
                "date": "2024-03-15",
                "duty_id": "D1",
                "details": "FDP 11.0h exceeds max 10.0h",
                "regulation": "117.5(b)",
            },
            {
                "type": "duty_period_exceeded",
                "severity": "critical",
                "date": "2024-03-16",
                "duty_id": "D2",
                "details": "FDP 12.0h exceeds max 10.0h",
                "regulation": "117.5(b)",
            },
        ],
        "grader": {"type": "python", "entry_point": "grader:grade_medium"},
    },
    "hard_30day": {
        "schedule": create_hard_30day(),
        "task_id": "hard_30day",
        "description": "30-day cumulative with violations",
        "expected_violations": 8,
        "ground_truth": [
            {
                "type": "duty_period_exceeded",
                "severity": "critical",
                "date": f"2024-03-{d:02d}",
                "duty_id": f"D{d}",
                "details": "FDP 12.0h exceeds max 10.0h",
                "regulation": "117.5(b)",
            }
            for d in range(1, 11)
        ],
        "grader": {"type": "python", "entry_point": "grader:grade_hard"},
    },
}


def get_task(task_name: str) -> Dict[str, Any]:
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}")
    return TASKS[task_name]


def list_tasks() -> List[str]:
    """Return list of all task IDs."""
    return list(TASKS.keys())


def get_tasks_with_graders() -> Dict[str, Dict[str, Any]]:
    """Return all tasks that have graders configured."""
    return {k: v for k, v in TASKS.items() if "grader" in v}


GRADERS = {
    "easy_single_day": "grader:grade_easy",
    "medium_3day": "grader:grade_medium",
    "hard_30day": "grader:grade_hard",
}


def get_grader(task_id: str) -> str:
    """Get grader entry point for a task."""
    return GRADERS.get(task_id, "grader:grade")
