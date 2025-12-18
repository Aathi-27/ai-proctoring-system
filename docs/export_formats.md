# Export Formats

Endpoint: `GET /reports/{report_id}/export?format=...`

Supported `format` values:

## `format=json`

Returns the report document serialized as JSON.

## `format=csv`

Returns a CSV of the event timeline for spreadsheet analysis.

Header:

```
event_id,timestamp,type,confidence,risk_contribution
```

## `format=html`

Returns a standalone HTML document intended for admin dashboard embedding. The score timeline is rendered with **Recharts** via CDN.

## `format=pdf`

Returns a printable PDF generated via **ReportLab** (includes header, executive summary, a score timeline chart, event table, and evidence links).
