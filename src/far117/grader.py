from typing import Any, Dict, List, Tuple


def grade_submission(
    agent_report: Dict[str, Any],
    ground_truth_violations: List[Dict[str, Any]],
    ground_truth_compliant: bool,
) -> Tuple[float, float, str]:
    """Grade an agent's submission for FAR 117 compliance."""

    agent_violations = agent_report.get("violations", [])
    agent_compliant = agent_report.get("overall_compliant", True)

    gt_count = len(ground_truth_violations)
    agent_count = len(agent_violations)

    compliance_correct = agent_compliant == ground_truth_compliant

    if ground_truth_compliant:
        if agent_count == 0:
            final_score = 1.0
            step_reward = 1.0
            feedback = "Correct: Schedule is compliant and no violations reported."
        else:
            false_positive_penalty = min(0.5, agent_count * 0.1)
            final_score = max(0.0, 1.0 - false_positive_penalty)
            step_reward = -false_positive_penalty
            feedback = f"Incorrect: Schedule is compliant but {agent_count} false positive(s) reported."
    else:
        if agent_count == 0:
            final_score = 0.0
            step_reward = -0.5
            feedback = f"Missed: Schedule has {gt_count} violation(s) but none were correctly identified."
        else:
            true_matches = min(agent_count, gt_count)
            recall = true_matches / gt_count if gt_count > 0 else 0.0
            precision = true_matches / agent_count if agent_count > 0 else 0.0

            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0.0

            compliance_bonus = 0.3 if compliance_correct else 0.0
            final_score = (f1 * 0.7) + compliance_bonus
            final_score = max(0.0, min(1.0, final_score))

            if agent_count > gt_count:
                fp_penalty = min(0.2, (agent_count - gt_count) * 0.05)
                final_score -= fp_penalty
                final_score = max(0.0, final_score)

            step_reward = final_score

            if true_matches == gt_count and agent_count <= gt_count:
                feedback = f"Excellent: Correctly identified all {gt_count} violation(s) with no false positives."
            elif true_matches > 0:
                feedback = f"Partial: Found {true_matches} violation(s), missed {gt_count - true_matches}."
            else:
                feedback = f"Incorrect: No violations correctly identified."

    step_reward = max(-1.0, min(1.0, step_reward))
    final_score = max(0.0, min(1.0, final_score))

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
