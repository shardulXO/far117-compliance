from typing import List, Tuple
from .models import Violation, FAR117Action


def grade_report(
    agent_report: FAR117Action, ground_truth: List[Violation]
) -> Tuple[float, str]:
    if not ground_truth:
        if agent_report.overall_compliant and not agent_report.violations:
            return 1.0, "PASS"
        return 0.0, "FAIL"
    true_pos = sum(
        1
        for gt in ground_truth
        for ag in agent_report.violations
        if gt.type == ag.type and gt.date == ag.date
    )
    false_pos = sum(
        1
        for ag in agent_report.violations
        if not any(gt.type == ag.type and gt.date == ag.date for gt in ground_truth)
    )
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
    recall = true_pos / len(ground_truth) if ground_truth else 0
    f1 = (
        2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    )
    return round(
        f1, 3
    ), f"TP={true_pos} FP={false_pos} FN={len(ground_truth) - true_pos}"


def compute_reward(agent_report, ground_truth, step=1) -> float:
    true_pos = sum(
        1
        for gt in ground_truth
        for ag in agent_report.violations
        if gt.type == ag.type and gt.date == ag.date
    )
    false_pos = sum(
        1
        for ag in agent_report.violations
        if not any(gt.type == ag.type and gt.date == ag.date for gt in ground_truth)
    )
    return round(true_pos * 0.1 - false_pos * 0.1, 2)
