import os
import sys
import json
from typing import List, Optional

if os.path.exists("/app"):
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, ".")

from openai import OpenAI

from far117.environment import FAR117Env
from far117.models import FAR117Action

API_KEY = os.getenv("HF_TOKEN", os.getenv("OPENAI_API_KEY", ""))
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("FAR117_TASK", "hard_30day")
BENCHMARK = "far117_compliance"
MAX_STEPS = 3

SYSTEM_PROMPT = """You are an aviation safety compliance auditor. Your task is to review pilot flight schedules against FAA FAR 117 flight crew rest requirements.

FAR 117 Key Rules:
- Maximum Flight Duty Period (FDP): Up to 13 hours depending on prior rest
- Minimum Rest Period: 10 hours (can be reduced to 9 hours with limits)
- Hotel Rest: 12 hours minimum when away from base
- Cumulative Limits: 100 hours/month, 60 hours/7 days

Output your audit as a JSON object with this exact structure:
{
  "overall_compliant": true/false,
  "violations": [
    {
      "type": "duty_period_exceeded",
      "severity": "critical",
      "date": "YYYY-MM-DD",
      "duty_id": "D1",
      "details": "description",
      "regulation": "FAR 117.5(b)"
    }
  ]
}

If no violations, set "overall_compliant": true and "violations": [].
Respond with ONLY JSON, no markdown formatting."""


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: Optional[str]
) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_escaped = action.replace('"', '\\"').replace("\n", "\\n")[:200]
    print(
        f'[STEP] step={step} action="{action_escaped}" reward={reward:.2f} done={done_val} error={error_val}',
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower()
    print(
        f"[END] success={success_val} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def parse_model_response(text: str) -> Optional[FAR117Action]:
    try:
        text = text.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end]
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            if end > start:
                text = text[start:end]
        text = text.strip()
        data = json.loads(text)
        violations = data.get("violations", [])
        if not isinstance(violations, list):
            violations = []
        return FAR117Action(
            violations=violations,
            overall_compliant=data.get("overall_compliant", False),
        )
    except Exception:
        return None


def get_model_action(client: OpenAI, schedule_json: str) -> FAR117Action:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Review this schedule for FAR 117 violations:\n\n{schedule_json}\n\nRespond with ONLY JSON.",
                },
            ],
            temperature=0.0,
            max_tokens=2048,
        )
        text = (completion.choices[0].message.content or "").strip()
        action = parse_model_response(text)
        if action:
            return action
        return FAR117Action(violations=[], overall_compliant=False)
    except Exception:
        return FAR117Action(violations=[], overall_compliant=False)


def main() -> None:
    if not API_KEY:
        raise ValueError("HF_TOKEN environment variable is required")

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = FAR117Env(task_id=TASK_NAME)
    rewards: List[float] = []
    steps_taken = 0
    success = False
    final_score = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        observation = env.reset()
        schedule_dict = observation.schedule
        schedule_json = json.dumps(schedule_dict, indent=2, default=str)

        for step in range(1, MAX_STEPS + 1):
            action = get_model_action(client, schedule_json)
            obs, reward, done, info = env.step(action)

            rewards.append(reward)
            steps_taken = step
            final_score = info.get("score", 0.0)

            action_str = json.dumps(
                {
                    "overall_compliant": action.overall_compliant,
                    "violations_count": len(action.violations),
                }
            )

            log_step(
                step=step,
                action=action_str,
                reward=reward,
                done=done,
                error=info.get("error"),
            )

            if done:
                break

        success = final_score >= 0.7

    except Exception as e:
        print(f"[DEBUG] Main error: {e}", flush=True)
        success = False
    finally:
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)


if __name__ == "__main__":
    main()
