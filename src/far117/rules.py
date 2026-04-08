from datetime import datetime
from typing import Any, Dict, List


def parse_time(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


def calc_duration(start: str, end: str) -> float:
    s = parse_time(start)
    e = parse_time(end)
    d = (e - s).total_seconds() / 3600
    return d + 24 if d < 0 else d


def compute_ground_truth(schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
    violations = []
    duties = schedule.get("duties", [])

    for duty in duties:
        duty_hours = calc_duration(
            duty.get("duty_start", "00:00"), duty.get("duty_end", "00:00")
        )
        if duty_hours > 13:
            violations.append(
                {
                    "type": "exceeded_duty_limit",
                    "severity": "critical",
                    "date": duty.get("date", ""),
                    "duty_id": duty.get("duty_id", ""),
                    "details": f"Duty {duty_hours:.1f}h > 13h",
                    "regulation": "FAR 117.7(b)",
                }
            )

        rest_period = duty.get("rest_period")
        if rest_period:
            rest_hours = calc_duration(
                rest_period.get("start", "00:00"), rest_period.get("end", "00:00")
            )
            if rest_hours < 8:
                violations.append(
                    {
                        "type": "insufficient_rest",
                        "severity": "critical",
                        "date": duty.get("date", ""),
                        "duty_id": duty.get("duty_id", ""),
                        "details": f"Rest {rest_hours:.1f}h < 8h",
                        "regulation": "FAR 117.7(a)",
                    }
                )
            elif rest_hours < 9:
                violations.append(
                    {
                        "type": "reduced_rest_used",
                        "severity": "major",
                        "date": duty.get("date", ""),
                        "duty_id": duty.get("duty_id", ""),
                        "details": f"Rest {rest_hours:.1f}h < 9h",
                        "regulation": "FAR 117.7(c)",
                    }
                )

    total_duty = sum(
        calc_duration(d.get("duty_start", "00:00"), d.get("duty_end", "00:00"))
        for d in duties
        if d.get("type") == "flight_duty"
    )
    if total_duty > 100:
        violations.append(
            {
                "type": "cumulative_duty_exceeded",
                "severity": "critical",
                "date": "2024-03-31",
                "duty_id": "cumulative",
                "details": f"Monthly {total_duty:.1f}h > 100h",
                "regulation": "FAR 117.9(a)",
            }
        )

    return violations
