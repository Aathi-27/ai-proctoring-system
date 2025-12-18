# Risk Classification Criteria

This implementation uses a simple, deterministic mapping from the **final risk score** (0–100) to a classification:

| Score Range | Classification |
|---:|---|
| 0–24 | LOW |
| 25–49 | MEDIUM |
| 50–74 | HIGH |
| 75–100 | CRITICAL |

## Final risk score

`final_risk_score = clamp(sum(event.risk_contribution), 0, 100)`

## Recommendations

| Classification | Recommendation |
|---|---|
| LOW | PASS |
| MEDIUM | REVIEW |
| HIGH / CRITICAL | FLAG_FOR_REVIEW |
