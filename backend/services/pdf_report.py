from typing import Any, Dict, List

from fpdf import FPDF


def build_pdf_report(result: Dict[str, Any]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Market Opportunity OSINT Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Generated from open-source intelligence.", ln=True)

    _section(pdf, "Executive Summary")
    summary = _build_summary(result)
    pdf.multi_cell(0, 6, summary)

    _section(pdf, "Scores")
    scores = result.get("scores", {})
    pdf.cell(0, 6, f"Overall score: {scores.get('overall_score')}", ln=True)
    pdf.cell(0, 6, f"Confidence: {scores.get('confidence')}", ln=True)
    pdf.multi_cell(0, 6, scores.get("rationale", ""))

    _section(pdf, "Key Takeaways")
    for item in _takeaways(result):
        pdf.multi_cell(0, 6, f"- {item}")

    delta = result.get("report_delta")
    if delta:
        _section(pdf, "Change vs Previous Run")
        for key, value in delta.items():
            pdf.multi_cell(0, 6, f"{key.replace('_', ' ').title()}: {value}")

    _section(pdf, "Evidence Pack (Top 10)")
    evidence = result.get("evidence", [])[:10]
    if not evidence:
        pdf.multi_cell(0, 6, "No evidence collected.")
    for item in evidence:
        title = item.get("title", "")
        url = item.get("url", "")
        quality = item.get("quality", "")
        relevance = item.get("relevance_score", "")
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, title)
        pdf.set_font("Helvetica", "", 10)
        if url:
            pdf.multi_cell(0, 6, url)
        pdf.multi_cell(0, 6, f"Quality: {quality} | Relevance: {relevance}")

    return pdf.output(dest="S").encode("latin-1")


def _section(pdf: FPDF, title: str) -> None:
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font("Helvetica", "", 11)


def _build_summary(result: Dict[str, Any]) -> str:
    subject = result.get("subject", {})
    scores = result.get("scores", {})
    overall = scores.get("overall_score", 0)
    confidence = scores.get("confidence", 0)
    target = subject.get("target_name", "the target")
    tier = "Low"
    if overall >= 70:
        tier = "High"
    elif overall >= 40:
        tier = "Medium"
    return (
        f"{target} receives a {tier} attractiveness rating with overall score {overall}. "
        f"Confidence is {confidence} based on the current evidence base."
    )


def _takeaways(result: Dict[str, Any]) -> List[str]:
    evidence = result.get("evidence", [])
    scores = result.get("scores", {})
    sources = scores.get("confidence_sources", {})
    takeaways = []
    if scores.get("overall_score", 0) >= 70:
        takeaways.append("Overall attractiveness is high.")
    elif scores.get("overall_score", 0) >= 40:
        takeaways.append("Overall attractiveness is moderate.")
    else:
        takeaways.append("Overall attractiveness is low.")
    if sources.get("official", 0) >= 3:
        takeaways.append("Multiple official sources support the analysis.")
    if len(evidence) == 0:
        takeaways.append("No evidence collected; verify API keys and sources.")
    return takeaways
