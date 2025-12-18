# Integrity Report Schema (MongoDB)

Collection: `reports` (recommended)

## Document shape

Matches the ticketed structure (additional soft-delete metadata fields are included to support retention):

```json
{
  "report_id": "uuid",
  "exam_id": "uuid",
  "session_id": "uuid",
  "candidate_id": "uuid",
  "generated_at": "2025-01-15T14:45:00Z",
  "exam_duration_minutes": 60,
  "final_risk_score": 65,
  "risk_classification": "HIGH",
  "score_timeline": [
    {"timestamp": "...", "score": 10},
    {"timestamp": "...", "score": 25}
  ],
  "events": [
    {
      "event_id": "uuid",
      "timestamp": "...",
      "type": "MOBILE_DETECTED",
      "confidence": 0.95,
      "risk_contribution": 25
    }
  ],
  "event_summary": {
    "MOBILE_DETECTED": {"count": 3, "total_contribution": 75},
    "TAB_SWITCHED": {"count": 5, "total_contribution": 50}
  },
  "evidence_snapshots": [
    {
      "snapshot_id": "uuid",
      "timestamp": "...",
      "event_type": "MOBILE_DETECTED",
      "s3_url": "s3://...",
      "encrypted": true
    }
  ],
  "recommendations": "FLAG_FOR_REVIEW",
  "notes": "",

  "deleted_at": null,
  "expires_at": "2025-02-14T14:45:00Z"
}
```

## Indexes (recommended)

- `reports`: `(exam_id, session_id)` unique
- `reports`: `expires_at` for retention sweeps
- `events`: `(exam_id, session_id, timestamp)`
- `snapshots`: `(exam_id, session_id, timestamp)`
