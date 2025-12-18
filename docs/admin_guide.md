# Admin Guide: Reviewing Integrity Reports

1. Generate a report
   - Automatically on session end (`POST /exams/{exam_id}/sessions/{session_id}/end`) or manually via:
     - `POST /exams/{exam_id}/sessions/{session_id}/generate-report`

2. View the report
   - JSON: `GET /exams/{exam_id}/sessions/{session_id}/report`
   - HTML (dashboard-ready): `GET /reports/{report_id}/export?format=html`
   - PDF (print/archive): `GET /reports/{report_id}/export?format=pdf`

3. Review checklist
   - Confirm risk classification and score timeline
   - Review top contributing event types
   - Scan event timeline for clusters (e.g., repeated tab switching)
   - Open evidence snapshot links for verification

4. Actions
   - `PASS`: no intervention
   - `REVIEW`: manual audit recommended
   - `FLAG_FOR_REVIEW`: initiate investigation and apply institutional policy

5. Deletion / retention
   - `DELETE /reports/{report_id}` performs a **soft delete**.
   - Reports are hard-deleted after the configured retention window.
