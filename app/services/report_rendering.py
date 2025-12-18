from __future__ import annotations

import io
import json
from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.domain import Candidate, Exam, ExamSession
from app.models.report import IntegrityReport


_env = Environment(
    loader=PackageLoader("app", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_report_html(
    *,
    report: IntegrityReport,
    exam: Exam,
    candidate: Candidate,
    session: ExamSession,
) -> str:
    template = _env.get_template("report.html")

    breakdown = sorted(
        (
            {"type": k, "count": v.count, "total_contribution": v.total_contribution}
            for k, v in report.event_summary.items()
        ),
        key=lambda x: x["total_contribution"],
        reverse=True,
    )[:5]

    return template.render(
        report=report.model_dump(mode="json"),
        exam=exam.model_dump(mode="json"),
        candidate=candidate.model_dump(mode="json"),
        session=session.model_dump(mode="json"),
        breakdown=breakdown,
        timeline_json=json.dumps(
            [
                {"timestamp": p.timestamp.isoformat(), "score": p.score}
                for p in report.score_timeline
            ]
        ),
    )


def render_report_pdf(
    *,
    report: IntegrityReport,
    exam: Exam,
    candidate: Candidate,
    session: ExamSession,
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Integrity Report - {exam.name} - {candidate.name}",
    )

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    mono = ParagraphStyle(name="Mono", parent=body, fontName="Courier", fontSize=9)

    story = []
    story.append(Paragraph("Post-Exam Integrity Report", title_style))
    story.append(Spacer(1, 12))

    meta = [
        ["Exam", exam.name],
        ["Candidate", candidate.name],
        ["Session ID", session.session_id],
        [
            "Generated At",
            report.generated_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        ],
        [
            "Exam Duration",
            f"{report.exam_duration_minutes} minutes",
        ],
    ]
    story.append(_styled_table(meta, col_widths=[4 * cm, 12 * cm]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", h2))
    story.append(
        Paragraph(
            f"Risk Classification: <b>{report.risk_classification.value}</b><br/>"
            f"Final Risk Score: <b>{report.final_risk_score}</b><br/>"
            f"Recommendation: <b>{report.recommendations.value}</b>",
            body,
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("Score Timeline", h2))
    story.append(_timeline_chart(report))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Top Contributing Event Types", h2))
    breakdown = sorted(
        ((k, v.count, v.total_contribution) for k, v in report.event_summary.items()),
        key=lambda x: x[2],
        reverse=True,
    )[:5]
    if breakdown:
        story.append(
            _styled_table(
                [["Event Type", "Count", "Total Contribution"], *breakdown],
                header_rows=1,
                col_widths=[8 * cm, 3 * cm, 5 * cm],
            )
        )
    else:
        story.append(Paragraph("No events detected.", body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Event Timeline", h2))
    event_rows = [["Timestamp", "Type", "Confidence", "Contribution"]]
    for e in report.events:
        event_rows.append(
            [
                e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                e.type,
                f"{e.confidence:.2f}",
                str(e.risk_contribution),
            ]
        )
    story.append(
        _styled_table(
            event_rows,
            header_rows=1,
            col_widths=[5 * cm, 5 * cm, 3 * cm, 3 * cm],
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("Evidence Gallery", h2))
    if report.evidence_snapshots:
        for s in report.evidence_snapshots[:30]:
            story.append(
                Paragraph(
                    f"{s.timestamp.strftime('%Y-%m-%d %H:%M:%S')} — {s.event_type}<br/>"
                    f"<font size='9'>{s.s3_url}</font>",
                    mono,
                )
            )
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No evidence snapshots.", body))

    doc.build(story)
    return buf.getvalue()


def _styled_table(
    rows: list[list[str | int | float]],
    *,
    header_rows: int = 0,
    col_widths: list[float] | None = None,
) -> Table:
    t = Table(rows, colWidths=col_widths)
    style = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]
    )
    if header_rows:
        style.add("BACKGROUND", (0, 0), (-1, header_rows - 1), colors.HexColor("#0B2F6B"))
        style.add("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.white)
        style.add("FONTSIZE", (0, 0), (-1, header_rows - 1), 10)
        style.add("LINEBELOW", (0, header_rows - 1), (-1, header_rows - 1), 1, colors.black)
    t.setStyle(style)
    return t


def _timeline_chart(report: IntegrityReport) -> Drawing:
    drawing = Drawing(16 * cm, 6 * cm)
    lp = LinePlot()
    lp.x = 1 * cm
    lp.y = 0.8 * cm
    lp.width = 14 * cm
    lp.height = 4.5 * cm

    points = []
    for idx, p in enumerate(report.score_timeline):
        points.append((idx, p.score))

    lp.data = [points or [(0, report.final_risk_score)]]
    lp.lines[0].strokeColor = colors.HexColor("#D7263D")
    lp.lines[0].strokeWidth = 2

    lp.valueAxis.valueMin = 0
    lp.valueAxis.valueMax = 100
    lp.valueAxis.valueStep = 25
    lp.valueAxis.visibleGrid = 1
    lp.valueAxis.gridStrokeColor = colors.lightgrey

    lp.categoryAxis.categoryNames = [
        _short_time(p.timestamp) for p in report.score_timeline
    ] or [datetime.now().strftime("%H:%M")]
    lp.categoryAxis.labels.angle = 45
    lp.categoryAxis.labels.dy = -10
    lp.categoryAxis.labels.fontSize = 6

    drawing.add(lp)
    return drawing


def _short_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")
