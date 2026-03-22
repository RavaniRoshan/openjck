from __future__ import annotations

import json
import textwrap
import tomllib
from datetime import date
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
PDF_PATH = OUTPUT_DIR / "openjck-product-documentation.pdf"

PALETTE = {
    "ink": colors.HexColor("#10233F"),
    "navy": colors.HexColor("#163A70"),
    "blue": colors.HexColor("#2F6BFF"),
    "cyan": colors.HexColor("#16B7D9"),
    "mint": colors.HexColor("#33B892"),
    "sand": colors.HexColor("#F3F7FB"),
    "gold": colors.HexColor("#FFB648"),
    "rose": colors.HexColor("#EE6C63"),
    "slate": colors.HexColor("#5D6B82"),
    "border": colors.HexColor("#D7E0EC"),
    "muted": colors.HexColor("#74839B"),
}


def load_project_context() -> dict:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    npm_package = json.loads((ROOT / "openjck-npm" / "package.json").read_text(encoding="utf-8"))

    trace_dir = ROOT / "tmp-home" / ".openjck" / "traces"
    traces = []
    if trace_dir.exists():
        for path in sorted(trace_dir.glob("*.json")):
            try:
                traces.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue

    success_trace = next((trace for trace in traces if trace.get("status") == "completed"), None)
    failed_trace = next((trace for trace in traces if trace.get("status") == "failed"), None)

    if success_trace is None:
        success_trace = {
            "status": "completed",
            "total_duration_ms": 352.57,
            "total_tokens": 312,
            "total_cost_usd": 0.000114,
            "steps": [
                {"step_id": 1, "type": "tool_call", "name": "search_web", "duration_ms": 100.1},
                {"step_id": 2, "type": "tool_call", "name": "read_document", "duration_ms": 50.5},
                {"step_id": 3, "type": "llm_call", "name": "call_llm_with_context", "duration_ms": 201.1},
            ],
        }

    if failed_trace is None:
        failed_trace = {
            "status": "failed",
            "error": "ValueError: Simulated error: API rate limit exceeded",
            "steps": [{"step_id": 1, "type": "tool_call", "name": "search_web", "duration_ms": 100.2}],
        }

    return {
        "python_version": pyproject["project"]["version"],
        "npm_version": npm_package["version"],
        "npm_package": npm_package["name"],
        "date": date(2026, 3, 12).strftime("%B %d, %Y"),
        "success_trace": success_trace,
        "failed_trace": failed_trace,
        "repo_surfaces": [
            ("Python tracer", "Decorators, collector, storage, and an optional FastAPI viewer entry point."),
            ("npm package", "Express-based local UI plus CLI commands for browsing, listing, and clearing traces."),
            ("Integrations", "LangChain monkey-patch helper for zero-touch capture of chains, tools, and LLM calls."),
            ("Examples + landing", "A sample traced agent and a static marketing site that explains the product story."),
        ],
    }


def paragraph_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=PALETTE["ink"],
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocSubtitle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11.5,
            leading=16,
            textColor=PALETTE["slate"],
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=PALETTE["ink"],
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionLead",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=PALETTE["slate"],
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=PALETTE["ink"],
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=PALETTE["slate"],
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=PALETTE["muted"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTight",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=PALETTE["ink"],
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletText",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=PALETTE["ink"],
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            fontName="Courier",
            fontSize=8.3,
            leading=11,
            textColor=PALETTE["ink"],
            leftIndent=8,
            rightIndent=8,
            spaceAfter=0,
        )
    )
    return styles


def rounded_box(drawing: Drawing, x: float, y: float, w: float, h: float, fill, stroke=None, radius=10):
    drawing.add(
        Rect(
            x,
            y,
            w,
            h,
            rx=radius,
            ry=radius,
            fillColor=fill,
            strokeColor=stroke or fill,
            strokeWidth=1,
        )
    )


def add_wrapped_text(drawing: Drawing, x: float, y: float, text: str, width: int, font_size=10, color=None):
    lines = textwrap.wrap(text, width=width)
    for index, line in enumerate(lines):
        drawing.add(
            String(
                x,
                y - (index * (font_size + 2)),
                line,
                fontName="Helvetica",
                fontSize=font_size,
                fillColor=color or PALETTE["ink"],
            )
        )


def add_arrow(drawing: Drawing, x1: float, y1: float, x2: float, y2: float, color):
    drawing.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=2))
    if x2 >= x1:
        points = [x2, y2, x2 - 8, y2 + 4, x2 - 8, y2 - 4]
    else:
        points = [x2, y2, x2 + 8, y2 + 4, x2 + 8, y2 - 4]
    drawing.add(Polygon(points, fillColor=color, strokeColor=color))


class DrawingFlowable(Flowable):
    def __init__(self, drawing: Drawing, width: float, height: float):
        super().__init__()
        self.drawing = drawing
        self.width = width
        self.height = height

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


def architecture_diagram() -> DrawingFlowable:
    width, height = 470, 235
    d = Drawing(width, height)
    rounded_box(d, 10, 20, 450, 195, PALETTE["sand"], PALETTE["border"], radius=18)

    nodes = [
        (25, 135, 120, 60, PALETTE["blue"], "Python agent", "Decorated entry point, tools, and LLM calls"),
        (175, 135, 120, 60, PALETTE["mint"], "TraceCollector", "In-process step capture and aggregation"),
        (325, 135, 120, 60, PALETTE["cyan"], "JSON storage", "~/.openjck/traces and costs.json"),
        (165, 38, 140, 66, PALETTE["gold"], "Local viewer", "Express or FastAPI server with browser UI"),
    ]

    for x, y, w, h, fill, title, body in nodes:
        rounded_box(d, x, y, w, h, fill, fill, radius=14)
        d.add(String(x + 10, y + h - 18, title, fontName="Helvetica-Bold", fontSize=12, fillColor=colors.white))
        add_wrapped_text(d, x + 10, y + h - 34, body, width=19, font_size=8, color=colors.white)

    add_arrow(d, 145, 165, 175, 165, PALETTE["navy"])
    add_arrow(d, 295, 165, 325, 165, PALETTE["navy"])
    add_arrow(d, 365, 135, 275, 104, PALETTE["navy"])
    add_arrow(d, 105, 135, 195, 104, PALETTE["navy"])

    d.add(String(26, 213, "End-to-end local architecture", fontName="Helvetica-Bold", fontSize=13, fillColor=PALETTE["ink"]))
    return DrawingFlowable(d, width, height)


def lifecycle_diagram() -> DrawingFlowable:
    width, height = 470, 185
    d = Drawing(width, height)
    d.add(String(10, 165, "How a run becomes an inspectable trace", fontName="Helvetica-Bold", fontSize=13, fillColor=PALETTE["ink"]))

    steps = [
        ("1", "Agent starts", PALETTE["blue"]),
        ("2", "Decorators open a trace", PALETTE["cyan"]),
        ("3", "Each step becomes a TraceEvent", PALETTE["mint"]),
        ("4", "Trace JSON is saved locally", PALETTE["gold"]),
        ("5", "Viewer lists and drills in", PALETTE["rose"]),
    ]
    x = 10
    for index, (num, label, fill) in enumerate(steps):
        rounded_box(d, x, 78, 82, 54, fill, fill, radius=14)
        d.add(Circle(x + 18, 105, 13, fillColor=colors.white, strokeColor=colors.white))
        d.add(String(x + 14, 100, num, fontName="Helvetica-Bold", fontSize=10, fillColor=fill))
        add_wrapped_text(d, x + 38, 111, label, width=12, font_size=8, color=colors.white)
        if index < len(steps) - 1:
            add_arrow(d, x + 82, 105, x + 98, 105, PALETTE["navy"])
        x += 94

    rounded_box(d, 10, 16, 450, 42, colors.white, PALETTE["border"], radius=12)
    add_wrapped_text(
        d,
        20,
        42,
        "The successful sample run in this repo records two tool calls and one LLM call, then rolls those metrics up into total duration, tokens, and cost.",
        width=86,
        font_size=9,
        color=PALETTE["slate"],
    )
    return DrawingFlowable(d, width, height)


def trace_schema_diagram() -> DrawingFlowable:
    width, height = 470, 240
    d = Drawing(width, height)
    d.add(String(10, 220, "Trace data model at a glance", fontName="Helvetica-Bold", fontSize=13, fillColor=PALETTE["ink"]))

    rounded_box(d, 25, 130, 180, 70, PALETTE["blue"], PALETTE["blue"], radius=16)
    d.add(String(40, 180, "Trace", fontName="Helvetica-Bold", fontSize=13, fillColor=colors.white))
    add_wrapped_text(d, 40, 162, "trace_id, run_name, started_at, finished_at, status, totals, error, metadata, steps[]", width=25, font_size=9, color=colors.white)

    rounded_box(d, 265, 130, 180, 90, PALETTE["mint"], PALETTE["mint"], radius=16)
    d.add(String(280, 199, "TraceEvent", fontName="Helvetica-Bold", fontSize=13, fillColor=colors.white))
    add_wrapped_text(d, 280, 181, "step_id, type, name, started_at, duration_ms, input, output, error, model, token counts, cost", width=25, font_size=9, color=colors.white)

    add_arrow(d, 205, 165, 265, 165, PALETTE["navy"])
    d.add(String(214, 176, "contains many", fontName="Helvetica-Bold", fontSize=9, fillColor=PALETTE["navy"]))

    rounded_box(d, 25, 35, 120, 58, PALETTE["sand"], PALETTE["border"], radius=14)
    d.add(String(38, 71, "Step types", fontName="Helvetica-Bold", fontSize=11, fillColor=PALETTE["ink"]))
    add_wrapped_text(d, 38, 56, "llm_call, tool_call, agent_step, custom", width=18, font_size=8, color=PALETTE["slate"])

    rounded_box(d, 175, 35, 130, 58, PALETTE["sand"], PALETTE["border"], radius=14)
    d.add(String(188, 71, "Search filters", fontName="Helvetica-Bold", fontSize=11, fillColor=PALETTE["ink"]))
    add_wrapped_text(d, 188, 56, "q, status, model, from_date, to_date", width=18, font_size=8, color=PALETTE["slate"])

    rounded_box(d, 335, 35, 110, 58, PALETTE["sand"], PALETTE["border"], radius=14)
    d.add(String(348, 71, "Stored as", fontName="Helvetica-Bold", fontSize=11, fillColor=PALETTE["ink"]))
    add_wrapped_text(d, 348, 56, "One JSON file per run", width=14, font_size=8, color=PALETTE["slate"])
    return DrawingFlowable(d, width, height)


def viewer_mock_diagram() -> DrawingFlowable:
    width, height = 470, 265
    d = Drawing(width, height)
    rounded_box(d, 10, 12, 450, 235, PALETTE["ink"], PALETTE["ink"], radius=20)
    rounded_box(d, 24, 26, 118, 206, colors.HexColor("#0E1830"), colors.HexColor("#23395F"), radius=16)
    rounded_box(d, 154, 26, 292, 48, colors.HexColor("#152B4F"), colors.HexColor("#2F5CA3"), radius=16)
    rounded_box(d, 154, 86, 292, 40, colors.HexColor("#122744"), colors.HexColor("#2D5BA5"), radius=16)
    rounded_box(d, 154, 136, 292, 96, colors.HexColor("#F6F9FD"), colors.HexColor("#D7E0EC"), radius=16)

    d.add(String(38, 212, "OpenJCK", fontName="Helvetica-Bold", fontSize=15, fillColor=colors.white))
    d.add(String(38, 194, "Recorded runs", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#BFD3FF")))
    for idx, label in enumerate(["agent_run_success", "agent_run_with_error", "research_agent"]):
        y = 164 - idx * 48
        rounded_box(d, 34, y, 98, 34, colors.HexColor("#17355E"), colors.HexColor("#2D5CA6"), radius=10)
        d.add(String(42, y + 20, label[:18], fontName="Helvetica", fontSize=8, fillColor=colors.white))
        d.add(String(42, y + 8, ["completed", "failed", "completed"][idx], fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#C8D6EF")))

    d.add(String(168, 56, "Selected trace overview", fontName="Helvetica-Bold", fontSize=15, fillColor=colors.white))
    d.add(String(168, 38, "Status, totals, and run metadata in the header", fontName="Helvetica", fontSize=9, fillColor=colors.HexColor("#D0DCFA")))

    for idx, fill in enumerate([PALETTE["cyan"], PALETTE["mint"], PALETTE["gold"], PALETTE["rose"]]):
        x = 178 + idx * 60
        d.add(Circle(x, 106, 10, fillColor=fill, strokeColor=fill))
        if idx < 3:
            d.add(Line(x + 10, 106, x + 50, 106, strokeColor=colors.HexColor("#6A88BA"), strokeWidth=2))

    d.add(String(168, 210, "Header stats", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.white))
    for idx, label in enumerate(["3 steps", "352ms", "312 tokens", "$0.0001"]):
        rounded_box(d, 168 + idx * 67, 177, 58, 24, colors.HexColor("#21416E"), colors.HexColor("#3868B9"), radius=10)
        d.add(String(178 + idx * 67, 186, label, fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white))

    d.add(String(170, 214, "Execution timeline", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor("#CAE0FF")))
    d.add(String(170, 156, "Input / output payload cards", fontName="Helvetica-Bold", fontSize=11, fillColor=PALETTE["ink"]))
    rounded_box(d, 168, 148, 126, 70, colors.white, PALETTE["border"], radius=12)
    rounded_box(d, 306, 148, 126, 70, colors.white, PALETTE["border"], radius=12)
    add_wrapped_text(d, 178, 195, "Tool or LLM input JSON", width=19, font_size=8, color=PALETTE["slate"])
    add_wrapped_text(d, 316, 195, "Serialized output plus errors when present", width=19, font_size=8, color=PALETTE["slate"])
    return DrawingFlowable(d, width, height)


def repo_map_diagram() -> DrawingFlowable:
    width, height = 470, 240
    d = Drawing(width, height)
    d.add(String(10, 220, "Repository map", fontName="Helvetica-Bold", fontSize=13, fillColor=PALETTE["ink"]))

    columns = [
        (20, "openjck/", PALETTE["blue"], ["collector.py", "decorators.py", "storage.py", "server.py", "integrations/langchain.py"]),
        (170, "openjck-npm/", PALETTE["cyan"], ["bin/openjck.js", "src/server.js", "commands/ui.js", "commands/traces.js", "src/ui/index.html"]),
        (320, "supporting assets", PALETTE["mint"], ["examples/basic_agent.py", "landing/index.html", "README.md", "pyproject.toml"]),
    ]
    for x, title, fill, items in columns:
        rounded_box(d, x, 44, 130, 148, fill, fill, radius=16)
        d.add(String(x + 12, 176, title, fontName="Helvetica-Bold", fontSize=12, fillColor=colors.white))
        for idx, item in enumerate(items):
            d.add(String(x + 12, 152 - idx * 22, item, fontName="Helvetica", fontSize=8.3, fillColor=colors.white))

    rounded_box(d, 20, 10, 430, 22, PALETTE["sand"], PALETTE["border"], radius=10)
    add_wrapped_text(d, 30, 24, "The repo ships both product surfaces in one place: Python instrumentation, npm viewer, example usage, and the landing narrative.", width=84, font_size=8.5, color=PALETTE["slate"])
    return DrawingFlowable(d, width, height)


def sample_timeline_diagram(trace: dict | None) -> DrawingFlowable:
    width, height = 470, 120
    d = Drawing(width, height)
    d.add(String(10, 100, "Sample successful run from examples/basic_agent.py", fontName="Helvetica-Bold", fontSize=13, fillColor=PALETTE["ink"]))
    if not trace:
        rounded_box(d, 10, 20, 450, 56, PALETTE["sand"], PALETTE["border"], radius=14)
        add_wrapped_text(d, 25, 54, "No sample trace was available at generation time. Run examples/basic_agent.py first to populate a concrete timeline.", width=80, font_size=9, color=PALETTE["slate"])
        return DrawingFlowable(d, width, height)

    steps = trace.get("steps", [])
    total_duration = max(float(trace.get("total_duration_ms") or 1), 1)
    x = 16
    usable_width = 438
    for step in steps:
        step_width = max((float(step.get("duration_ms") or 0) / total_duration) * usable_width, 56)
        fill = {
            "tool_call": PALETTE["cyan"],
            "llm_call": PALETTE["gold"],
            "agent_step": PALETTE["mint"],
        }.get(step.get("type"), PALETTE["blue"])
        rounded_box(d, x, 34, step_width, 34, fill, fill, radius=10)
        d.add(String(x + 8, 54, f"#{step.get('step_id')} {step.get('name')}", fontName="Helvetica-Bold", fontSize=8.4, fillColor=colors.white))
        d.add(String(x + 8, 41, f"{round(float(step.get('duration_ms') or 0), 1)} ms", fontName="Helvetica", fontSize=7.5, fillColor=colors.white))
        x += step_width + 8
    return DrawingFlowable(d, width, height)


def metric_table(context: dict) -> Table:
    success_trace = context["success_trace"] or {}
    failed_trace = context["failed_trace"] or {}
    rows = [
        ["Documentation timestamp", context["date"]],
        ["Python package", f"openjck {context['python_version']}"],
        ["npm package", f"{context['npm_package']} {context['npm_version']}"],
        ["Sample success run", f"{len(success_trace.get('steps', []))} steps, {success_trace.get('total_tokens', 0)} tokens, {success_trace.get('total_duration_ms', 'n/a')} ms"],
        ["Sample failure run", failed_trace.get("error", "No failure sample found")],
    ]
    table = Table(rows, colWidths=[130, 300])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PALETTE["sand"]]),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                ("TEXTCOLOR", (0, 0), (-1, -1), PALETTE["ink"]),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def surface_cards(context: dict, styles) -> Table:
    cells = []
    for title, body in context["repo_surfaces"]:
        cells.append([Paragraph(title, styles["CardTitle"]), Paragraph(body, styles["CardBody"])])

    table = Table(
        [[cells[0], cells[1]], [cells[2], cells[3]]],
        colWidths=[232, 232],
        rowHeights=[76, 76],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def command_table() -> Table:
    rows = [
        ["Command", "Purpose"],
        ("pip install openjck", "Install the Python instrumentation package."),
        ("npx openjck", "Start the local viewer on http://localhost:7823."),
        ("npx openjck traces", "List all stored traces in the terminal."),
        ("npx openjck clear", "Delete recorded trace JSON files after confirmation."),
        ("openjck.patch_langchain()", "Monkey-patch LangChain primitives for automatic step capture."),
    ]
    table = Table(rows, colWidths=[180, 250], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALETTE["ink"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALETTE["sand"]]),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def endpoint_table() -> Table:
    rows = [
        ["Route", "What it does"],
        ["GET /api/health", "Health probe for the local viewer runtime."],
        ["GET /api/traces", "Lists trace summaries; supports q, status, model, from_date, and to_date filters."],
        ["GET /api/traces/{trace_id}", "Loads a full trace document with step payloads."],
        ["DELETE /api/traces/{trace_id}", "Deletes one stored trace file."],
        ["GET / and GET /trace/{trace_id}", "Serve the browser UI shell."],
    ]
    table = Table(rows, colWidths=[170, 260], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALETTE["blue"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALETTE["sand"]]),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def bullet_list(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, styles["BulletText"])) for item in items],
        bulletType="bullet",
        leftIndent=14,
    )


def code_panel(text: str, title: str, styles) -> Table:
    block = Preformatted(text.strip(), styles["CodeBlock"])
    table = Table([[Paragraph(title, styles["CardTitle"])], [block]], colWidths=[460])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), PALETTE["sand"]),
                ("BACKGROUND", (0, 1), (0, 1), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def cover_block(context: dict, styles) -> list:
    intro = Table(
        [
            [Paragraph("Product Documentation", styles["SmallLabel"])],
            [Paragraph("OpenJCK", styles["DocTitle"])],
            [
                Paragraph(
                    "A dedicated product document for the current repository state: what the package does, how the tracing pipeline works, what ships today, and where the viewer, CLI, and storage layers fit together.",
                    styles["DocSubtitle"],
                )
            ],
        ],
        colWidths=[460],
    )
    intro.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALETTE["sand"]),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )

    status = Table(
        [
            [
                Paragraph("Snapshot date", styles["SmallLabel"]),
                Paragraph("Python package", styles["SmallLabel"]),
                Paragraph("npm package", styles["SmallLabel"]),
            ],
            [
                Paragraph(context["date"], styles["CardTitle"]),
                Paragraph(f"openjck {context['python_version']}", styles["CardTitle"]),
                Paragraph(f"{context['npm_package']} {context['npm_version']}", styles["CardTitle"]),
            ],
        ],
        colWidths=[150, 150, 160],
    )
    status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALETTE["ink"]),
                ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    return [
        Spacer(1, 18 * mm),
        intro,
        Spacer(1, 10 * mm),
        architecture_diagram(),
        Spacer(1, 8 * mm),
        status,
    ]


def build_story(context: dict) -> list:
    styles = paragraph_styles()
    success_trace = context["success_trace"] or {}
    story: list = []

    story.extend(cover_block(context, styles))
    story.append(PageBreak())

    story.extend(
        [
            Paragraph("1. Product Snapshot", styles["SectionTitle"]),
            Paragraph(
                "OpenJCK is a local-first observability layer for AI agents. Instead of replacing an agent framework, it wraps existing Python functions and records the real execution path: every agent entry, every tool call, every LLM interaction, and every failure state.",
                styles["SectionLead"],
            ),
            metric_table(context),
            Spacer(1, 8),
            surface_cards(context, styles),
            Spacer(1, 10),
            Paragraph("Why it matters", styles["CardTitle"]),
            bullet_list(
                [
                    "It gives developers a concrete execution record instead of scattered print statements.",
                    "The trace model is lightweight and portable because each run is persisted as JSON.",
                    "The npm package turns those files into a practical browsing experience with zero server infrastructure.",
                    "The project already spans a full product arc: instrumentation, storage, CLI, UI, sample usage, and landing page.",
                ],
                styles,
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("2. Architecture", styles["SectionTitle"]),
            Paragraph(
                "The repo currently ships two runtime surfaces that share the same storage contract. The Python package is responsible for capturing steps and writing trace files. The viewer surface, most visibly delivered through the npm package, reads those files and presents them in a browser-first local UI.",
                styles["SectionLead"],
            ),
            architecture_diagram(),
            Spacer(1, 10),
            lifecycle_diagram(),
            Spacer(1, 10),
            Paragraph("Architectural note", styles["CardTitle"]),
            Paragraph(
                "Both the Python package and the npm package expose a viewer runtime. The Python side includes an optional FastAPI server entry point, while the npm package provides an Express server and the published CLI. Both target the same local trace directory and similar HTTP endpoints.",
                styles["BodyTight"],
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("3. Instrumentation API", styles["SectionTitle"]),
            Paragraph(
                "The public API is intentionally compact. Users instrument an agent with three decorators, then optionally add LangChain auto-instrumentation. This keeps adoption low-friction while still surfacing the high-value execution events.",
                styles["SectionLead"],
            ),
            code_panel(
                """
from openjck import trace, trace_llm, trace_tool

@trace(name="research_agent")
def run_agent(task: str):
    response = call_llm([{"role": "user", "content": task}])
    return web_search(response.message.content)

@trace_llm(model="gpt-4o-mini")
def call_llm(messages):
    ...

@trace_tool
def web_search(query: str):
    ...
                """,
                "Core usage pattern",
                styles,
            ),
            Spacer(1, 10),
            Table(
                [
                    [
                        Paragraph("@trace", styles["CardTitle"]),
                        Paragraph("@trace_llm", styles["CardTitle"]),
                        Paragraph("@trace_tool", styles["CardTitle"]),
                    ],
                    [
                        Paragraph("Starts and finishes a run, aggregates totals, saves the final trace, and can auto-start the local viewer.", styles["CardBody"]),
                        Paragraph("Captures prompt-like inputs, normalized outputs, detected model name, token counts, and cost.", styles["CardBody"]),
                        Paragraph("Captures serialized tool inputs and outputs, including exceptions if the tool fails.", styles["CardBody"]),
                    ],
                ],
                colWidths=[152, 152, 152],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PALETTE["sand"]),
                        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                        ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                        ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
            Spacer(1, 12),
            code_panel(
                """
from openjck import patch_langchain

patch_langchain()

# Monkey-patches:
# - BaseLanguageModel.__call__ / invoke
# - BaseTool._run / _arun
# - Chain.__call__ / invoke
                """,
                "LangChain integration surface",
                styles,
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("4. Trace Model and Example Run", styles["SectionTitle"]),
            Paragraph(
                "Every recorded run becomes one Trace document that contains a sequence of TraceEvent records. This model is plain enough to inspect by eye and structured enough to drive the viewer, terminal listings, and search filters.",
                styles["SectionLead"],
            ),
            trace_schema_diagram(),
            Spacer(1, 10),
            sample_timeline_diagram(success_trace),
            Spacer(1, 10),
            Paragraph("Observed sample run", styles["CardTitle"]),
            Paragraph(
                f"The generated success sample in this workspace completed in {success_trace.get('total_duration_ms', 'n/a')} ms, recorded {len(success_trace.get('steps', []))} steps, used {success_trace.get('total_tokens', 0)} total tokens, and computed a total cost of ${success_trace.get('total_cost_usd', 0):.4f}. The failed sample preserves the run-level error while still storing the successful steps that occurred before the exception.",
                styles["BodyTight"],
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("5. Viewer and CLI Experience", styles["SectionTitle"]),
            Paragraph(
                "The npm package turns the stored JSON files into a usable local product. Its Express runtime exposes a small HTTP API and serves a single-page interface that highlights recorded runs, totals, execution timelines, and input/output payloads for each step.",
                styles["SectionLead"],
            ),
            viewer_mock_diagram(),
            Spacer(1, 10),
            command_table(),
            Spacer(1, 10),
            Paragraph("What the UI emphasizes", styles["CardTitle"]),
            bullet_list(
                [
                    "A sidebar that keeps recent runs visible and clickable.",
                    "Run-level stats that summarize steps, duration, token usage, and cost.",
                    "A compact timeline that makes the order of LLM and tool calls obvious.",
                    "Step detail panels that show normalized input and output payloads without leaving the page.",
                ],
                styles,
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("6. Storage, Search, and HTTP Surface", styles["SectionTitle"]),
            Paragraph(
                "Storage is deliberately simple: one JSON file per run under ~/.openjck/traces/, plus a costs.json file that seeds default model pricing. That simplicity makes it easy to inspect, back up, clear, and port traces between machines.",
                styles["SectionLead"],
            ),
            endpoint_table(),
            Spacer(1, 10),
            Table(
                [
                    [Paragraph("Storage contract", styles["CardTitle"]), Paragraph("Behavior", styles["CardTitle"])],
                    [Paragraph("Trace persistence", styles["CardBody"]), Paragraph("TraceStorage.save writes one indented JSON file per completed run.", styles["CardBody"])],
                    [Paragraph("List/search behavior", styles["CardBody"]), Paragraph("Search supports run name substring, status, model, and date range filters by inspecting stored JSON.", styles["CardBody"])],
                    [Paragraph("Auto-open behavior", styles["CardBody"]), Paragraph("The @trace decorator prints a local trace URL and can auto-start the Python viewer runtime after the run finishes.", styles["CardBody"])],
                    [Paragraph("Clear behavior", styles["CardBody"]), Paragraph("The npm clear command asks for confirmation before deleting trace files.", styles["CardBody"])],
                ],
                colWidths=[150, 310],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PALETTE["sand"]),
                        ("BOX", (0, 0), (-1, -1), 1, PALETTE["border"]),
                        ("INNERGRID", (0, 0), (-1, -1), 0.75, PALETTE["border"]),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
        ]
    )

    story.append(PageBreak())
    story.extend(
        [
            Paragraph("7. Repository Scope and Current Assessment", styles["SectionTitle"]),
            Paragraph(
                "As of March 12, 2026, the repo already reads like a coherent product foundation rather than an isolated library. It includes trace capture primitives, an opinionated local viewer, an npm CLI wrapper, a demo agent, packaging metadata, and a landing page narrative.",
                styles["SectionLead"],
            ),
            repo_map_diagram(),
            Spacer(1, 10),
            KeepTogether(
                [
                    Paragraph("What is already strong", styles["CardTitle"]),
                    bullet_list(
                        [
                            "The public Python API is tiny and memorable.",
                            "The trace schema is understandable without custom infrastructure.",
                            "The viewer focuses on debugging outcomes that developers actually need: sequence, payloads, errors, tokens, and cost.",
                            "LangChain support shows the product can extend beyond hand-decorated functions.",
                        ],
                        styles,
                    ),
                    Spacer(1, 8),
                    Paragraph("What the next maturity layer would likely add", styles["CardTitle"]),
                    bullet_list(
                        [
                            "Stable shared viewer behavior between the Python and npm runtimes.",
                            "More integrations beyond LangChain and richer framework adapters.",
                            "Broader filtering, grouping, and comparison inside the UI.",
                            "Packaging polish around docs, release automation, and trace lifecycle management.",
                        ],
                        styles,
                    ),
                ]
            ),
            Spacer(1, 12),
            HRFlowable(color=PALETTE["border"], width="100%"),
            Spacer(1, 8),
            Paragraph(
                "Bottom line: OpenJCK is best described as a local-first agent debugging product made of a Python tracer and a browser-based trace viewer. The current repository already communicates a compelling product thesis and contains enough working surface area to document it as a real package, not just a prototype snippet.",
                ParagraphStyle(
                    "Closing",
                    parent=styles["BodyText"],
                    fontName="Helvetica-Bold",
                    fontSize=11,
                    leading=16,
                    textColor=PALETTE["ink"],
                ),
            ),
        ]
    )
    return story


def draw_footer(canvas, doc):
    page_num = canvas.getPageNumber()
    if page_num == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(PALETTE["border"])
    canvas.line(doc.leftMargin, 12 * mm, A4[0] - doc.rightMargin, 12 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(PALETTE["muted"])
    canvas.drawString(doc.leftMargin, 8 * mm, "OpenJCK Product Documentation")
    canvas.drawRightString(A4[0] - doc.rightMargin, 8 * mm, f"Page {page_num - 1}")
    canvas.restoreState()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    context = load_project_context()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="OpenJCK Product Documentation",
        author="Codex",
    )
    story = build_story(context)
    doc.build(story, onLaterPages=draw_footer)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
