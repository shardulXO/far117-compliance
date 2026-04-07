from typing import Dict, Any, List
from .models import ScheduleInput, CrewMember, Duty, Flight, RestPeriod


def create_easy_single_day() -> ScheduleInput:
    return ScheduleInput(
        version="1.0",
        crew_member=CrewMember(
            id="P001", role="captain", base="ORD", home_timezone="America/Chicago"
        ),
        schedule_period={"start_date": "2024-03-15", "end_date": "2024-03-15"},
        duties=[
            Duty(
                duty_id="D1",
                date="2024-03-15",
                type="flight_duty",
                duty_start="05:00",
                duty_end="17:00",
                departure_airport="ORD",
                arrival_airport="LAX",
                flights=[
                    Flight(
                        flight_number="AA101",
                        departure="06:00",
                        arrival="08:15",
                        origin="ORD",
                        destination="LAX",
                    ),
                    Flight(
                        flight_number="AA102",
                        departure="09:30",
                        arrival="10:45",
                        origin="LAX",
                        destination="SFO",
                    ),
                    Flight(
                        flight_number="AA103",
                        departure="12:00",
                        arrival="13:15",
                        origin="SFO",
                        destination="LAX",
                    ),
                    Flight(
                        flight_number="AA104",
                        departure="14:30",
                        arrival="16:45",
                        origin="LAX",
                        destination="ORD",
                    ),
                ],
                rest_period=RestPeriod(
                    start="17:00", end="23:00", location="ORD", is_hotel_rest=False
                ),
            )
        ],
        prior_duties_context=[
            {
                "duty_id": "D0",
                "date": "2024-03-14",
                "duty_end": "22:00",
                "rest_location": "ORD",
            }
        ],
    )


def create_easy_single_day_pass() -> ScheduleInput:
    return ScheduleInput(
        version="1.0",
        crew_member=CrewMember(
            id="P001", role="captain", base="ORD", home_timezone="America/Chicago"
        ),
        schedule_period={"start_date": "2024-03-15", "end_date": "2024-03-15"},
        duties=[
            Duty(
                duty_id="D1",
                date="2024-03-15",
                type="flight_duty",
                duty_start="06:00",
                duty_end="14:00",
                departure_airport="ORD",
                arrival_airport="DEN",
                flights=[
                    Flight(
                        flight_number="AA201",
                        departure="07:00",
                        arrival="08:30",
                        origin="ORD",
                        destination="DEN",
                    ),
                    Flight(
                        flight_number="AA202",
                        departure="10:00",
                        arrival="11:30",
                        origin="DEN",
                        destination="ORD",
                    ),
                ],
                rest_period=RestPeriod(
                    start="14:00", end="23:00", location="ORD", is_hotel_rest=False
                ),
            )
        ],
        prior_duties_context=[
            {
                "duty_id": "D0",
                "date": "2024-03-14",
                "duty_end": "21:00",
                "rest_location": "ORD",
            }
        ],
    )


def create_medium_3day() -> ScheduleInput:
    return ScheduleInput(
        version="1.0",
        crew_member=CrewMember(
            id="P002", role="first_officer", base="DFW", home_timezone="America/Chicago"
        ),
        schedule_period={"start_date": "2024-03-15", "end_date": "2024-03-17"},
        duties=[
            Duty(
                duty_id="D1",
                date="2024-03-15",
                type="flight_duty",
                duty_start="05:00",
                duty_end="16:00",
                departure_airport="DFW",
                arrival_airport="LAX",
                flights=[
                    Flight(
                        flight_number="AA301",
                        departure="06:00",
                        arrival="07:30",
                        origin="DFW",
                        destination="LAX",
                    ),
                    Flight(
                        flight_number="AA302",
                        departure="09:00",
                        arrival="10:15",
                        origin="LAX",
                        destination="SFO",
                    ),
                    Flight(
                        flight_number="AA303",
                        departure="12:00",
                        arrival="13:15",
                        origin="SFO",
                        destination="LAX",
                    ),
                ],
                rest_period=RestPeriod(
                    start="16:00", end="01:00", location="LAX", is_hotel_rest=True
                ),
            ),
            Duty(
                duty_id="D2",
                date="2024-03-16",
                type="flight_duty",
                duty_start="10:00",
                duty_end="22:00",
                departure_airport="LAX",
                arrival_airport="JFK",
                flights=[
                    Flight(
                        flight_number="AA304",
                        departure="11:00",
                        arrival="19:00",
                        origin="LAX",
                        destination="JFK",
                    ),
                    Flight(
                        flight_number="AA305",
                        departure="20:00",
                        arrival="21:30",
                        origin="JFK",
                        destination="BOS",
                    ),
                ],
                rest_period=RestPeriod(
                    start="22:00", end="06:00", location="BOS", is_hotel_rest=True
                ),
            ),
            Duty(
                duty_id="D3",
                date="2024-03-17",
                type="flight_duty",
                duty_start="14:00",
                duty_end="23:00",
                departure_airport="BOS",
                arrival_airport="DFW",
                flights=[
                    Flight(
                        flight_number="AA306",
                        departure="15:00",
                        arrival="17:30",
                        origin="BOS",
                        destination="DFW",
                    )
                ],
                rest_period=RestPeriod(
                    start="23:00", end="08:00", location="DFW", is_hotel_rest=False
                ),
            ),
        ],
        prior_duties_context=[
            {
                "duty_id": "D0",
                "date": "2024-03-14",
                "duty_end": "20:00",
                "rest_location": "DFW",
            }
        ],
    )


def create_hard_30day() -> ScheduleInput:
    duties = []
    for day in range(1, 31):
        if day <= 3:
            duties.append(
                Duty(
                    duty_id=f"D{day:02d}",
                    date=f"2024-03-{day:02d}",
                    type="flight_duty",
                    duty_start="06:00",
                    duty_end="14:00",
                    departure_airport="DFW",
                    arrival_airport="LAX",
                    flights=[
                        Flight(
                            flight_number=f"AA{day}",
                            departure="07:00",
                            arrival="08:15",
                            origin="DFW",
                            destination="LAX",
                        )
                    ],
                    rest_period=RestPeriod(
                        start="14:00", end="23:00", location="LAX", is_hotel_rest=True
                    ),
                )
            )
        elif day <= 15:
            duties.append(
                Duty(
                    duty_id=f"D{day:02d}",
                    date=f"2024-03-{day:02d}",
                    type="flight_duty",
                    duty_start="04:00",
                    duty_end="15:00",
                    departure_airport="LAX",
                    arrival_airport="ORD",
                    flights=[
                        Flight(
                            flight_number=f"AA{day}",
                            departure="05:00",
                            arrival="11:00",
                            origin="LAX",
                            destination="ORD",
                        )
                    ],
                    rest_period=RestPeriod(
                        start="15:00", end="23:00", location="ORD", is_hotel_rest=True
                    ),
                )
            )
        else:
            duties.append(
                Duty(
                    duty_id=f"D{day:02d}",
                    date=f"2024-03-{day:02d}",
                    type="flight_duty",
                    duty_start="18:00",
                    duty_end="04:00",
                    departure_airport="ORD",
                    arrival_airport="NRT",
                    flights=[
                        Flight(
                            flight_number=f"AA{day}",
                            departure="19:00",
                            arrival="22:00",
                            origin="ORD",
                            destination="NRT",
                        )
                    ],
                    rest_period=RestPeriod(
                        start="04:00", end="14:00", location="NRT", is_hotel_rest=True
                    ),
                )
            )
    return ScheduleInput(
        version="1.0",
        crew_member=CrewMember(
            id="P003", role="captain", base="DFW", home_timezone="America/Chicago"
        ),
        schedule_period={"start_date": "2024-03-01", "end_date": "2024-03-31"},
        duties=duties,
        prior_duties_context=[],
    )


def get_task(task_name: str) -> Dict[str, Any]:
    tasks = {
        "easy_single_day": {
            "schedule": create_easy_single_day(),
            "task_id": "easy_single_day",
            "description": "Single pilot, single day",
            "expected_violations": 2,
        },
        "easy_single_day_pass": {
            "schedule": create_easy_single_day_pass(),
            "task_id": "easy_single_day_pass",
            "description": "Should pass",
            "expected_violations": 0,
        },
        "medium_3day": {
            "schedule": create_medium_3day(),
            "task_id": "medium_3day",
            "description": "3-day rotation",
            "expected_violations": 3,
        },
        "hard_30day": {
            "schedule": create_hard_30day(),
            "task_id": "hard_30day",
            "description": "30-day cumulative",
            "expected_violations": 8,
        },
    }
    if task_name not in tasks:
        raise ValueError(f"Unknown task: {task_name}")
    return tasks[task_name]
