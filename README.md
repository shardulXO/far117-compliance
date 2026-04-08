---
title: Flightrestcompliancegeturhoursrightpilot
emoji: ✈️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: apache-2.0
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