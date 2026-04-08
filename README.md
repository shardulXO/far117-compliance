---
title: FAR 117 Compliance
emoji: ✈️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: FAA FAR 117 flight crew rest compliance checker.
---

# FAR 117 Flight Crew Rest Compliance

## Overview

This OpenEnv environment simulates real-world aviation safety compliance auditing. Agents review pilot flight schedules against FAA FAR 117 regulations to detect fatigue-related safety violations.

**Real-world utility**: FAA has fined airlines $2M+ for rest violations. Fatigue is the #1 cause of pilot error (50% of accidents).

## Tasks

| Task | Difficulty | Description | Expected Violations |
|------|------------|-------------|---------------------|
| easy_single_day | Easy | Single pilot, single day, domestic US | 1-2 |
| medium_3day | Medium | Full crew, 3-day rotation, multiple timezones | 3 |
| hard_30day | Hard | Multi-crew, 30-day cumulative, international | 8+ |

## Action & Observation Spaces

### Action Space
```json
{
  "violations": [
    {
      "type": "insufficient_rest",
      "severity": "critical",
      "date": "2024-03-15",
      "duty_id": "D1",
      "details": "Rest period below minimum",
      "regulation": "FAR 117.7(a)"
    }
  ],
  "overall_compliant": false,
  "explanation": "..."
}
```

### Observation Space
```json
{
  "schedule": {
    "crew_member": {...},
    "duties": [...],
    "schedule_period": {...}
  },
  "step": 0,
  "done": false,
  "feedback": "Expected violations (2 total): ..."
}
```

### Reward
- +0.1 per correct violation found
- -0.1 per false positive
- Score: 0.0-1.0 (F1-based)

## Setup & Usage

### Local Development
```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Docker
```bash
docker build -t far117 .
docker run -p 7860:7860 far117
```

### API Endpoints
- `GET /` - Root info
- `GET /ping` - Health check
- `GET /info` - Environment info
- `POST /reset` - Reset with task_id
- `POST /step` - Submit compliance report

## Baseline Performance

| Task | Expected Score | Notes |
|------|----------------|-------|
| easy_single_day | 0.7-0.9 | Clear violations |
| medium_3day | 0.5-0.7 | Multiple violations, timezone handling |
| hard_30day | 0.3-0.5 | Cumulative limits, international complexity |

## OpenEnv Compliance

- ✅ Typed Pydantic models (Action, Observation, State)
- ✅ reset() → observation
- ✅ step(action) → (observation, reward, done, info)
- ✅ state() → current state
- ✅ openenv.yaml with metadata
- ✅ 3 tasks with difficulty progression
- ✅ Grader produces 0.0-1.0 score
- ✅ Dockerfile builds and runs
- ✅ Deterministic, reproducible grading

## Known Limitations

1. **Simplified Schedule Schema**: The schedule format uses a simplified duty-based model rather than raw leg-by-leg flight data. This trade-off prioritizes clarity over full FAA regulatory complexity.

2. **Single-Episode Completion**: The environment terminates after one step submission. Multi-turn dialogue for clarification is not supported—agents must produce complete compliance reports in a single response.

3. **No Prior Context History**: Agents receive only the current schedule without prior schedule context. In production, FAR 117 requires 7-day lookback for cumulative limits.

4. **Fixed Timezone Handling**: Timezone crossings are simplified to boolean flags rather than detailed UTC conversion for each leg. Complex international routing may not be fully represented.

5. **No Partial Credit for Near-Misses**: The grader does not award partial credit for violations detected with wrong severity or regulation citations—only exact type matches count.

6. **No Uncertainty Quantification**: The model must commit to a binary compliance decision. Probabilistic or "likely compliant" responses are not supported.

7. **Hardcoded Ground Truth**: Violations are pre-computed in task definitions. The environment does not dynamically compute violations from the schedule using the rules engine.

## Design Tradeoffs

| Tradeoff | Decision | Rationale |
|----------|----------|----------|
| Dict vs Pydantic for schedule | Dict-based schedules | Better JSON serialization for API responses; avoids nested model complexity |
| Single-step episode | One submission per schedule | Simplifies evaluation; aligns with benchmark scoring methodology |
| F1-based scoring | Precision + recall weighting | Balances false positives (reporting violations that don't exist) against false negatives (missing real violations) |
| Static ground truth | Pre-computed violations | Determinism is critical for reproducible benchmarking; dynamic computation would introduce non-determinism |
| Simplified FAR rules | Duty-hour focus | Full FAR 117 has 50+ pages of regulations; core fatigue-related limits are prioritized |
| Explicit regulation citations | Agent must cite FAR section | Enforces domain knowledge; plain English descriptions alone would be insufficient |
| No multi-agent support | Single agent per schedule | Aligned with single-pilot certification scope; multi-crew is modeled as separate pilots |