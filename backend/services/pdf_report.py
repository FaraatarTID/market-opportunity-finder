from typing import Any, Dict, List

from fpdf import FPDF
from fpdf.errors import FPDFUnicodeEncodingException


def build_pdf_report(result: Dict[str, Any]) -> bytes:
    try:
        return _build_pdf_report(result)
    except FPDFUnicodeEncodingException:
        return _build_pdf_report(result, force_ascii=True)


def _build_pdf_report(result: Dict[str, Any], force_ascii: bool = False) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Market Opportunity OSINT Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Generated from open-source intelligence.", ln=True)
    width = _epw(pdf)

    _section(pdf, "Executive Summary")
    summary = _build_summary(result)
    _safe_multi_cell(pdf, width, 6, summary, force_ascii=force_ascii)

    _section(pdf, "Scores")
    scores = result.get("scores", {})
    pdf.cell(0, 6, f"Overall score: {scores.get('overall_score')}", ln=True)
    pdf.cell(0, 6, f"Confidence: {scores.get('confidence')}", ln=True)
    _safe_multi_cell(pdf, width, 6, scores.get("rationale", ""), force_ascii=force_ascii)

    _section(pdf, "Key Takeaways")
    for item in _takeaways(result):
        text = f"- {item}".strip()
        if text:
            _safe_multi_cell(pdf, width, 6, text, force_ascii=force_ascii)

    delta = result.get("report_delta")
    if delta:
        _section(pdf, "Change vs Previous Run")
        for key, value in delta.items():
            _safe_multi_cell(pdf, width, 6, f"{key.replace('_', ' ').title()}: {value}", force_ascii=force_ascii)

    _section(pdf, "Evidence Pack (Top 10)")
    evidence = result.get("evidence", [])[:10]
    if not evidence:
        _safe_multi_cell(pdf, width, 6, "No evidence collected.", force_ascii=force_ascii)
    for item in evidence:
        title = item.get("title", "")
        url = item.get("url", "")
        quality = item.get("quality", "")
        relevance = item.get("relevance_score", "")
        pdf.set_font("Helvetica", "B", 11)
        _safe_multi_cell(pdf, width, 6, title, force_ascii=force_ascii)
        pdf.set_font("Helvetica", "", 10)
        if url:
            _safe_multi_cell(pdf, width, 6, url, force_ascii=force_ascii)
        _safe_multi_cell(pdf, width, 6, f"Quality: {quality} | Relevance: {relevance}", force_ascii=force_ascii)

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


def _epw(pdf: FPDF) -> float:
    try:
        return pdf.epw
    except Exception:
        return pdf.w - pdf.l_margin - pdf.r_margin


def _safe_text(text: str, force_ascii: bool = False) -> str:
    if text is None:
        return ""
    # Allow line breaks but insert breakpoints into long tokens (URLs/IDs).
    safe = str(text)
    # Normalize common punctuation
    safe = safe.replace("’", "'").replace("“", "\"").replace("”", "\"")
    # Strip non-latin-1 characters to avoid FPDFUnicodeEncodingException.
    if force_ascii:
        safe = safe.encode("ascii", "ignore").decode("ascii")
    else:
        safe = safe.encode("latin-1", "ignore").decode("latin-1")
    safe = safe.replace("/", "/ ")
    safe = safe.replace("_", "_ ")
    safe = safe.replace("-", "- ")
    return safe


def _safe_multi_cell(pdf: FPDF, width: float, height: float, text: str, force_ascii: bool = False) -> None:
    try:
        pdf.multi_cell(width, height, _safe_text(text, force_ascii=force_ascii))
    except FPDFUnicodeEncodingException:
        fallback = str(text).encode("ascii", "ignore").decode("ascii")
        pdf.multi_cell(width, height, fallback)
