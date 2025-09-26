"""
report_generator.py
Create a clean, side-by-side comparison report (HTML by default; optional PDF).

Expected high-level input (example):
comparison = {
    "left": {"name": "Plan A", "meta": {"insurer": "Alpha", "date": "2024-10-02"}},
    "right": {"name": "Plan B", "meta": {"insurer": "Beta", "date": "2024-07-19"}},
    "sections": [
        {
            "title": "Coverage",
            "rows": [
                {"field": "Life Cover", "left": "$250,000", "right": "$200,000"},
                {"field": "Accidental Death", "left": "Included", "right": "Excluded"},
            ],
        },
        {
            "title": "Exclusions",
            "rows": [
                {"field": "Pre-existing (12m)", "left": "Yes", "right": "Yes"},
                {"field": "Hazardous Sports", "left": "No", "right": "Yes"},
            ],
        },
    ],
    "summary": {
        "highlights": [
            "Plan A has higher base life cover.",
            "Plan B excludes hazardous sports."
        ],
        "score_left": 78,   # optional numeric score (0–100)
        "score_right": 65
    }
}

Usage:
    from report_generator import generate_report
    paths = generate_report(comparison, output_dir="reports", base_filename="comparison_2025-09-25", as_pdf=False)

Notes:
- PDF generation tries WeasyPrint first, then pdfkit (wkhtmltopdf). If neither is available, you still get HTML.
- Keep dependencies optional; don’t make CI choke if PDF tools aren’t installed.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import shutil
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------
# Public API
# -----------------------------

def generate_report(
    comparison: Dict[str, Any],
    *,
    output_dir: str = "reports",
    base_filename: str = "comparison_report",
    logo_path: Optional[str] = None,
    as_pdf: bool = False,
    write_json_snapshot: bool = True,
) -> Dict[str, str]:
    """
    Render an HTML report and optionally a PDF.
    Returns dict with generated file paths: {"html": "...", "pdf": "..."} (pdf only if created).
    """
    _validate_payload(comparison)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    logo_b64 = _maybe_embed_logo(logo_path)

    html = _render_html(comparison, stamp, logo_b64)
    html_path = str(Path(output_dir) / f"{base_filename}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    out = {"html": html_path}

    if write_json_snapshot:
        snap_path = str(Path(output_dir) / f"{base_filename}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        out["json"] = snap_path

    if as_pdf:
        pdf_path = str(Path(output_dir) / f"{base_filename}.pdf")
        ok, reason = _html_to_pdf(html, pdf_path)
        if ok:
            out["pdf"] = pdf_path
        else:
            # Don’t explode if PDF deps are missing.
            out["pdf_error"] = reason

    return out


# -----------------------------
# HTML rendering
# -----------------------------

def _render_html(comparison: Dict[str, Any], generated_at: str, logo_b64: Optional[str]) -> str:
    left_name = comparison["left"].get("name", "Left")
    right_name = comparison["right"].get("name", "Right")
    left_meta = comparison["left"].get("meta", {})
    right_meta = comparison["right"].get("meta", {})
    sections: List[Dict[str, Any]] = comparison.get("sections", [])
    summary: Dict[str, Any] = comparison.get("summary", {})

    # Scores (optional)
    score_left = summary.get("score_left")
    score_right = summary.get("score_right")
    highlights = summary.get("highlights", [])

    style = _css()

    # Build sections
    sections_html: List[str] = []
    for sec in sections:
        rows_html: List[str] = []
        for row in sec.get("rows", []):
            field = _escape(row.get("field", ""))
            lval = _escape(row.get("left", "—"))
            rval = _escape(row.get("right", "—"))
            # diff highlight
            diff_class = "diff" if (str(lval).strip() != str(rval).strip()) else ""
            rows_html.append(
                f"""
                <tr class="{diff_class}">
                    <td class="field">{field}</td>
                    <td class="left">{lval}</td>
                    <td class="right">{rval}</td>
                </tr>
                """
            )
        section_block = f"""
        <section>
            <h2>{_escape(sec.get('title', 'Section'))}</h2>
            <table class="compare">
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>{_escape(left_name)}</th>
                        <th>{_escape(right_name)}</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </section>
        """
        sections_html.append(section_block)

    # Meta key/values
    meta_html = f"""
    <div class="meta">
        <div>
            <h4>{_escape(left_name)}</h4>
            {_kv_table(left_meta)}
        </div>
        <div>
            <h4>{_escape(right_name)}</h4>
            {_kv_table(right_meta)}
        </div>
    </div>
    """

    # Score cards (optional)
    score_html = ""
    if isinstance(score_left, (int, float)) or isinstance(score_right, (int, float)):
        score_html = f"""
        <div class="scores">
            <div class="score-card">
                <div class="label">{_escape(left_name)}</div>
                <div class="score">{_fmt_score(score_left)}</div>
            </div>
            <div class="score-card">
                <div class="label">{_escape(right_name)}</div>
                <div class="score">{_fmt_score(score_right)}</div>
            </div>
        </div>
        """

    # Highlights
    highlights_html = ""
    if highlights:
        li = "".join(f"<li>{_escape(h)}</li>" for h in highlights)
        highlights_html = f"""
        <section>
            <h2>Highlights</h2>
            <ul class="highlights">{li}</ul>
        </section>
        """

    # Logo (optional)
    logo_html = f'<img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo" />' if logo_b64 else ""

    # Final HTML
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Insurance Product Comparator — Report</title>
<style>{style}</style>
</head>
<body>
<header>
  {logo_html}
  <div class="titles">
    <h1>Insurance Product Comparator — Report</h1>
    <p class="subtitle">Generated {generated_at}</p>
  </div>
</header>

{meta_html}
{score_html}
{''.join(sections_html)}
{highlights_html}

<footer>
  <p>Auto-generated by Insurance Product Comparator. For internal review use.</p>
</footer>
</body>
</html>
"""
    return textwrap.dedent(html)


def _css() -> str:
    # Simple, print-friendly styles. No external fonts.
    return textwrap.dedent(
        """
        :root {
          --bg: #ffffff;
          --fg: #111111;
          --muted: #6b7280;
          --border: #e5e7eb;
          --accent: #0ea5e9;
          --diff: #fff7ed;
          --diff-border: #fdba74;
        }
        * { box-sizing: border-box; }
        body {
          margin: 24px;
          background: var(--bg);
          color: var(--fg);
          font: 14px/1.45 system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
        }
        header {
          display: flex; align-items: center; gap: 16px; margin-bottom: 12px;
          padding-bottom: 12px; border-bottom: 1px solid var(--border);
        }
        .logo { height: 40px; width: auto; }
        .titles h1 { margin: 0; font-size: 22px; }
        .subtitle { margin: 2px 0 0; color: var(--muted); }

        .meta {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin: 16px 0 24px;
        }
        .meta h4 { margin: 0 0 6px; }
        .meta table { width: 100%; border: 1px solid var(--border); border-collapse: collapse; }
        .meta td { padding: 6px 8px; border-top: 1px solid var(--border); }
        .meta td.key { width: 40%; color: var(--muted); background: #fafafa; }

        h2 { margin: 24px 0 8px; font-size: 18px; }
        table.compare { width: 100%; border-collapse: collapse; border: 1px solid var(--border); }
        table.compare th, table.compare td { padding: 8px 10px; border-top: 1px solid var(--border); vertical-align: top; }
        table.compare th { text-align: left; background: #fafafa; }
        table.compare td.field { width: 28%; font-weight: 600; }
        table.compare tr.diff td { background: var(--diff); }
        table.compare tr.diff td.field { border-left: 3px solid var(--diff-border); }

        .scores {
          display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 6px 0 18px;
        }
        .score-card {
          border: 1px solid var(--border); border-radius: 10px; padding: 12px;
        }
        .score-card .label { color: var(--muted); margin-bottom: 6px; }
        .score-card .score { font-size: 28px; font-weight: 700; color: var(--accent); }

        .highlights { margin: 0; padding-left: 18px; }
        .highlights li { margin: 4px 0; }

        footer { margin-top: 36px; padding-top: 12px; border-top: 1px solid var(--border); color: var(--muted); font-size: 12px; }
        @media print {
          body { margin: 0.5in; }
          header { margin-bottom: 8px; }
        }
        """
    )


def _kv_table(meta: Dict[str, Any]) -> str:
    if not meta:
        return '<table><tbody><tr><td class="key">Info</td><td>—</td></tr></tbody></table>'
    rows = []
    for k, v in meta.items():
        rows.append(f'<tr><td class="key">{_escape(str(k))}</td><td>{_escape(str(v))}</td></tr>')
    return f"<table><tbody>{''.join(rows)}</tbody></table>"


def _fmt_score(x: Any) -> str:
    if x is None:
        return "—"
    try:
        val = float(x)
        if val < 0: val = 0.0
        if val > 100: val = 100.0
        return f"{val:.0f}/100"
    except Exception:
        return "—"


def _escape(s: Any) -> str:
    # Minimal HTML escaping
    text = "" if s is None else str(s)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _maybe_embed_logo(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        return base64.b64encode(p.read_bytes()).decode("ascii")
    except Exception:
        return None


# -----------------------------
# PDF generation (optional)
# -----------------------------

def _html_to_pdf(html: str, out_path: str) -> Tuple[bool, str]:
    """
    Try WeasyPrint, then pdfkit (wkhtmltopdf). Return (ok, reason_if_failed).
    """
    # Try WeasyPrint (pure Python, but needs Cairo/Pango system libs)
    try:
        from weasyprint import HTML  # type: ignore
        HTML(string=html).write_pdf(out_path)
        return True, ""
    except Exception as e:
        weasy_err = str(e)

    # Try pdfkit → wkhtmltopdf binary must be installed
    try:
        import pdfkit  # type: ignore
        config = None
        # Attempt to locate wkhtmltopdf if not on P
