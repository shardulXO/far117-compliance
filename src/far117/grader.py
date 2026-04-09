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
    """Grade an agent's submission for FAR 117 compliance."""

    agent_violations = agent_report.get("violations", [])
    agent_compliant = agent_report.get("overall_compliant", True)

    gt_keys = {_violation_key(v) for v in ground_truth_violations}
    agent_keys = {_violation_key(v) for v in agent_violations}

    true_positives = gt_keys & agent_keys
    false_positives = agent_keys - gt_keys
    false_negatives = gt_keys - agent_keys

    tp_count = len(true_positives)
    fp_count = len(false_positives)
    fn_count = len(false_negatives)
    gt_count = len(gt_keys)
    agent_count = len(agent_keys)

    compliance_correct = agent_compliant == ground_truth_compliant

    if ground_truth_compliant:
        if agent_count == 0:
            final_score = 0.99
            step_reward = 0.99
            feedback = "Correct: Schedule is compliant and no violations reported."
        else:
            false_positive_penalty = min(0.5, fp_count * 0.15)
            final_score = max(0.01, round(1.0 - false_positive_penalty, 2))
            step_reward = round(-false_positive_penalty, 2)
            feedback = f"Incorrect: Schedule is compliant but {fp_count} false positive(s) reported."
    else:
        if tp_count == 0:
            final_score = 0.01
            step_reward = -0.5
            feedback = f"Missed: Schedule has {gt_count} violation(s) but none were correctly identified."
        else:
            recall = tp_count / gt_count if gt_count > 0 else 0.0
            precision = tp_count / agent_count if agent_count > 0 else 0.0

            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0.0

            compliance_bonus = 0.3 if compliance_correct else 0.0
            final_score = (f1 * 0.7) + compliance_bonus
            final_score = max(0.01, min(0.99, round(final_score, 2)))

            if fp_count > 0:
                fp_penalty = min(0.2, fp_count * 0.1)
                final_score = max(0.01, round(final_score - fp_penalty, 2))

            step_reward = round(final_score, 2)

            if tp_count == gt_count and fp_count == 0:
                feedback = f"Perfect: Correctly identified all {gt_count} violation(s) with no false positives."
            elif tp_count == gt_count and fp_count > 0:
                feedback = f"Correct types but {fp_count} extra false positive(s)."
            elif fn_count == 0:
                feedback = f"Found all {tp_count} violation(s), no misses."
            elif tp_count > 0:
                feedback = f"Found {tp_count}/{gt_count} violation(s), missed {fn_count}, {fp_count} false positive(s)."
            else:
                feedback = f"Found {fp_count} false positive(s), missed all {fn_count} true violations."

    step_reward = round(max(-1.0, min(1.0, step_reward)), 2)
    final_score = _clamp_score(round(final_score, 2))

    return final_score, step_reward, feedback


def compute_reward(
    agent_report: Dict[str, Any], ground_truth: List[Dict[str, Any]], step: int = 1
) -> float:
    """Compute reward for a submission."""
    score, reward, _ = grade_submission(
        agent_report, ground_truth, len(ground_truth) == 0
    )
    return reward


def grade_report(
    agent_report: Dict[str, Any], ground_truth: List[Dict[str, Any]]
) -> Tuple[float, str]:
    """Grade a report and return score with details."""
    score, _, feedback = grade_submission(
        agent_report, ground_truth, len(ground_truth) == 0
    )
    return score, feedback


def grade(
    task_id: str,
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
) -> Tuple[float, str]:
    """OpenEnv grader interface - grades a single task submission."""
    ground_truth_compliant = len(ground_truth_violations) == 0
    score, _, feedback = grade_submission(
        agent_report, ground_truth_violations, ground_truth_compliant
    )
    return score, feedback
