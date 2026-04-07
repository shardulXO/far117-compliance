from datetime import datetime
from typing import List
from .models import ScheduleInput, Violation, Duty, RestPeriod


def parse_time(t):
    return datetime.strptime(t, "%H:%M")


def calc_duration(start, end):
    s, e = parse_time(start), parse_time(end)
    d = (e - s).total_seconds() / 3600
    return d + 24 if d < 0 else d


def compute_ground_truth(schedule: ScheduleInput) -> List[Violation]:
    violations = []
    for duty in schedule.duties:
        duty_hours = calc_duration(duty.duty_start, duty.duty_end)
        if duty_hours > 13:
            violations.append(
                Violation(
                    type="exceeded_duty_limit",
                    severity="critical",
                    date=duty.date,
                    duty_id=duty.duty_id,
                    details=f"Duty {duty_hours:.1f}h > 13h",
                    regulation="FAR 117.7(b)",
                )
            )
        if duty.rest_period:
            rest_hours = calc_duration(duty.rest_period.start, duty.rest_period.end)
            if rest_hours < 8:
                violations.append(
                    Violation(
                        type="insufficient_rest",
                        severity="critical",
                        date=duty.date,
                        duty_id=duty.duty_id,
                        details=f"Rest {rest_hours:.1f}h < 8h",
                        regulation="FAR 117.7(a)",
                    )
                )
            elif rest_hours < 9:
                violations.append(
                    Violation(
                        type="reduced_rest_used",
                        severity="major",
                        date=duty.date,
                        duty_id=duty.duty_id,
                        details=f"Rest {rest_hours:.1f}h < 9h",
                        regulation="FAR 117.7(c)",
                    )
                )
    total_duty = sum(
        calc_duration(d.duty_start, d.duty_end)
        for d in schedule.duties
        if d.type == "flight_duty"
    )
    if total_duty > 100:
        violations.append(
            Violation(
                type="cumulative_duty_exceeded",
                severity="critical",
                date="2024-03-31",
                duty_id="cumulative",
                details=f"Monthly {total_duty:.1f}h > 100h",
                regulation="FAR 117.9(a)",
            )
        )
    return violations
