# Post-Exam Integrity Report Generation

FastAPI service implementing post-exam integrity report generation, storage (MongoDB), exports (PDF/JSON/CSV/HTML), and RBAC.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Auth model (dev/test)

This repository uses lightweight header-based auth for RBAC:

- `X-Role`: `ADMIN` | `CANDIDATE` | `INVIGILATOR`
- `X-User-Id`: UUID string

Candidate access is limited to their own reports. Invigilators are limited to exams they monitor (provided via `X-Monitored-Exam-Ids: <exam_id>,<exam_id>`).

See `docs/` for schema, risk classification, and export formats.
