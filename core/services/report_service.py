from pathlib import Path

from flask import current_app, render_template

from core.services.llm_report_service import build_demo_report_context


def render_report_fragment(report=None):
    return render_template("stock_report_content.html", report=report or build_demo_report_context())


def render_report_html(report=None):
    """Render the preview report as a styled HTML body for email sending."""
    css_path = Path(current_app.static_folder) / "css" / "stock_report.css"
    css_content = css_path.read_text(encoding="utf-8")
    content_html = render_report_fragment(report)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票分析报告预览</title>
    <style>
{css_content}
    </style>
</head>
<body>
{content_html}
</body>
</html>"""
