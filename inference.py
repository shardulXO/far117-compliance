import asyncio
import os
import sys
import json
import textwrap
from typing import List, Optional

sys.path.insert(0, "/app")

from openai import OpenAI
from src.far117 import FAR117Env, FAR117Action
from src.far117.models import Violation

API_KEY = os.getenv("HF_TOKEN")
if not API_KEY:
    raise ValueError("HF_TOKEN environment variable is required")

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("FAR117_TASK", "easy_single_day")
BENCHMARK = os.getenv("FAR117_BENCHMARK", "far117_compliance")
MAX_STEPS = 3
TEMPERATURE = 0.3
MAX_TOKENS = 2048

SYSTEM_PROMPT = textwrap.dedent("""
You are an aviation safety compliance auditor. Your task is to review pilot flight schedules 
against FAA FAR 117 flight crew rest requirements and identify any violations.

FAR 117 Key Rules:
- Maximum Flight Duty Period (FDP): Up to 13 hours depending on prior rest
- Minimum Rest Period: 10 hours (can be reduced to 9 hours with limits)
- Quick Trip Rest: 12 hours when crossing 6+ timezones
- Cumulative Limits: 100 hours/month, 60 hours/7 days

Output your audit as a JSON object with this structure:
{
  "overall_compliant": true/false,
  "violations": [
    {
      "type": "insufficient_rest",
      "severity": "critical",
      "date": "YYYY-MM-DD",
      "duty_id": "D1",
      "details": "description",
      "regulation": "FAR 117.X"
    }
  ],
  "explanation": "summary of findings"
}

If no violations, set "overall_compliant": true and "violations": [].
""").strip()


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


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success_val = str(success).lower()
    print(
        f"[END] success={success_val} steps={steps} rewards={rewards_str}", flush=True
    )


def parse_model_response(text: str) -> Optional[FAR117Action]:
    try:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        data = json.loads(text)
        violations = []
        for v in data.get("violations", []):
            violations.append(Violation(**v))
        return FAR117Action(
            violations=violations,
            overall_compliant=data.get("overall_compliant", False),
            explanation=data.get("explanation", ""),
        )
    except Exception as e:
        print(f"[DEBUG] Parse error: {e}", flush=True)
        return None


def get_model_action(client: OpenAI, schedule_json: str) -> FAR117Action:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Review this schedule for FAR 117 violations:\n\n{schedule_json}\n\nOutput JSON only.",
                },
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        action = parse_model_response(text)
        if action:
            return action
        return FAR117Action(
            violations=[],
            overall_compliant=False,
            explanation="Failed to parse model response",
        )
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return FAR117Action(
            violations=[], overall_compliant=False, explanation=f"API error: {str(exc)}"
        )


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = FAR117Env(task_id=TASK_NAME)
    rewards: List[float] = []
    steps_taken = 0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset()
        schedule_json = result.observation.schedule.model_dump_json(indent=2)

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            action = get_model_action(client, schedule_json)
            result = await env.step(action)

            reward = result.reward or 0.0
            done = result.done

            rewards.append(reward)
            steps_taken = step

            action_str = json.dumps(
                {
                    "overall_compliant": action.overall_compliant,
                    "violations_count": len(action.violations),
                }
            )

            log_step(step=step, action=action_str, reward=reward, done=done, error=None)

            if done:
                break

        success = len(rewards) > 0 and any(r > 0 for r in rewards)

    except Exception as e:
        print(f"[DEBUG] Main error: {e}", flush=True)
        success = False
    finally:
        try:
            await env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
