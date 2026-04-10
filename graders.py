from typing import Any, Dict, List, Tuple


def _violation_key(v: Dict[str, Any]) -> str:
    return f"{v.get('type', '')}|{v.get('date', '')}|{v.get('duty_id', '')}"


def _clamp_score(s: float) -> float:
    if s <= 0.01:
        return 0.01
    if s >= 0.99:
        return 0.99
    return round(s, 2)


def grade_submission(
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
    ground_truth_compliant: bool,
) -> Tuple[float, float, str]:
    agent_violations = agent_report.get("violations", [])
    agent_compliant = agent_report.get("overall_compliant", True)

    gt_keys = {_violation_key(v) for v in ground_truth_violations}
    agent_keys = {_violation_key(v) for v in agent_violations}

    tp_count = len(gt_keys & agent_keys)
    fp_count = len(agent_keys - gt_keys)
    fn_count = len(gt_keys - agent_keys)
    gt_count = len(gt_keys)
    agent_count = len(agent_keys)

    compliance_correct = agent_compliant == ground_truth_compliant

    if ground_truth_compliant:
        if agent_count == 0:
            return 0.99, 0.99, "Correct: Schedule is compliant."
        else:
            penalty = min(0.5, fp_count * 0.15)
            return (
                max(0.01, round(1.0 - penalty, 2)),
                round(-penalty, 2),
                f"Incorrect: {fp_count} false positive(s).",
            )
    else:
        if tp_count == 0:
            return 0.01, -0.5, f"Missed: {gt_count} violation(s)."
        recall = tp_count / gt_count if gt_count > 0 else 0.0
        precision = tp_count / agent_count if agent_count > 0 else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        score = (f1 * 0.7) + (0.3 if compliance_correct else 0.0)
        score = max(0.01, min(0.99, round(score, 2)))
        if fp_count > 0:
            score = max(0.01, round(score - min(0.2, fp_count * 0.1), 2))
        return score, round(score, 2), f"Found {tp_count}/{gt_count} violation(s)."


def grade(
    task_id: str,
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
) -> Tuple[float, str]:
    score, _, feedback = grade_submission(
        agent_report, ground_truth_violations, len(ground_truth_violations) == 0
    )
    return score, feedback


def grade_easy(
    task_id: str,
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
) -> Tuple[float, str]:
    return grade(task_id, agent_report, ground_truth_violations)


def grade_medium(
    task_id: str,
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
) -> Tuple[float, str]:
    return grade(task_id, agent_report, ground_truth_violations)


def grade_hard(
    task_id: str,
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
) -> Tuple[float, str]:
    return grade(task_id, agent_report, ground_truth_violations)
