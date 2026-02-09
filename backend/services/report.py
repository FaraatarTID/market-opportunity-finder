from typing import Any, Dict, List, Optional


def _escape(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_kv_table(title: str, data: Dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><th>{_escape(key)}</th><td>{_escape(value)}</td></tr>" for key, value in data.items()
    )
    return f"""
    <section>
      <h2>{_escape(title)}</h2>
      <table class="kv">
        {rows}
      </table>
    </section>
    """


def _render_scores(scores: Dict[str, Any]) -> str:
    dimensional = scores.get("dimensional_scores", {})
    confidence_breakdown = scores.get("confidence_breakdown", {})
    confidence_sources = scores.get("confidence_sources", {})
    rows = "".join(
        f"<tr><th>{_escape(key.replace('_', ' ').title())}</th><td>{_escape(value)}</td></tr>"
        for key, value in dimensional.items()
    )
    breakdown_rows = "".join(
        f"<tr><th>{_escape(key.replace('_', ' ').title())}</th><td>{_escape(value)}</td></tr>"
        for key, value in confidence_breakdown.items()
    )

    return f"""
    <section>
      <h2>Scores</h2>
      <p><strong>Overall:</strong> {_escape(scores.get("overall_score"))}</p>
      <p><strong>Confidence:</strong> {_escape(scores.get("confidence"))}</p>
      <p>{_escape(scores.get("rationale"))}</p>
      <table class="kv">
        {rows}
      </table>
      <h3>Confidence Breakdown</h3>
      <table class="kv">
        {breakdown_rows}
      </table>
      <h3>Confidence Sources</h3>
      <table class="kv">
        { "".join(f"<tr><th>{_escape(key.title())}</th><td>{_escape(value)}</td></tr>" for key, value in confidence_sources.items()) }
      </table>
    </section>
    """


def _render_evidence(evidence: List[Dict[str, Any]]) -> str:
    if not evidence:
        return "<section><h2>Evidence Pack</h2><p>No evidence collected.</p></section>"

    rows = []
    for item in evidence:
        title = _escape(item.get("title"))
        url = _escape(item.get("url"))
        summary = _escape(item.get("summary"))
        age = _escape(item.get("age"))
        source = _escape(item.get("source"))
        signal_type = _escape(item.get("signal_type"))
        domain = _escape(item.get("domain"))
        quality = _escape(item.get("quality"))
        severity = _escape(item.get("severity"))
        keyword_hits = _escape(item.get("keyword_hits"))
        relevance_score = _escape(item.get("relevance_score"))
        link = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>' if url else title
        rows.append(
            f"<tr><td>{link}</td><td>{summary}</td><td>{age}</td><td>{source}</td><td>{signal_type}</td><td>{domain}</td><td>{quality}</td><td>{severity}</td><td>{keyword_hits}</td><td>{relevance_score}</td></tr>"
        )

    body = "".join(rows)
    return f"""
    <section>
      <h2>Evidence Pack</h2>
      <table class="evidence">
        <thead>
          <tr>
            <th>Title</th>
            <th>Summary</th>
            <th>Age</th>
            <th>Source</th>
            <th>Signal</th>
            <th>Domain</th>
            <th>Quality</th>
            <th>Severity</th>
            <th>Keyword Hits</th>
            <th>Relevance</th>
          </tr>
        </thead>
        <tbody>
          {body}
        </tbody>
      </table>
    </section>
    """


def build_score_narrative(result: Dict[str, Any]) -> Dict[str, Any]:
    scores = result.get("scores", {})
    evidence = result.get("evidence", [])
    subject = result.get("subject", {})
    macro = result.get("macro", {})
    trade_signals = result.get("trade_signals", {})
    policy_signals = result.get("policy_signals", {})

    target = subject.get("target_name", "the target")
    overall = scores.get("overall_score", 0)
    confidence = scores.get("confidence", 0)
    evidence_count = len(evidence)

    tier = "Low"
    if overall >= 70:
        tier = "High"
    elif overall >= 40:
        tier = "Medium"

    confidence_sources = scores.get("confidence_sources", {})
    official_count = confidence_sources.get("official", 0)
    media_count = confidence_sources.get("media", 0)
    unknown_count = confidence_sources.get("unknown", 0)

    macro_flags = []
    if macro.get("gdp") is not None:
        macro_flags.append("GDP")
    if macro.get("population") is not None:
        macro_flags.append("Population")

    trade_available = sum(
        1
        for payload in trade_signals.values()
        if isinstance(payload, dict) and payload.get("value") is not None
    )
    policy_available = sum(
        1
        for payload in policy_signals.values()
        if isinstance(payload, dict) and payload.get("value") is not None
    )

    summary = (
        f"{target} scores {overall} ({tier}) with confidence {confidence}. "
        f"The assessment is based on {evidence_count} evidence items and the available macro, trade, and policy signals."
    )

    justification = [
        f"Overall score {overall} reflects weighted demand, trade ease, risk, financial viability, and strategic fit.",
        f"Confidence {confidence} is driven by {evidence_count} evidence items and source mix.",
        f"Macro coverage: {', '.join(macro_flags) if macro_flags else 'no macro indicators available'}.",
        f"Trade indicators with values: {trade_available}.",
        f"Policy indicators with values: {policy_available}.",
        f"Source mix: {official_count} official, {media_count} media, {unknown_count} unknown.",
    ]

    key_evidence = _summarize_key_evidence(evidence)

    gaps = []
    if official_count == 0:
        gaps.append("No official sources detected; validate with primary data.")
    if evidence_count < 5:
        gaps.append("Evidence volume is limited; consider widening sources or keywords.")
    if trade_available == 0:
        gaps.append("Trade indicators are missing or null; confidence in demand signals is lower.")
    if policy_available == 0:
        gaps.append("Policy indicators are missing or null; regulatory risk may be under-scoped.")

    return {
        "summary": summary,
        "justification": justification,
        "key_evidence": key_evidence,
        "gaps": gaps,
    }


def _summarize_key_evidence(evidence: List[Dict[str, Any]], limit: int = 3) -> List[str]:
    scored = []
    for item in evidence:
        relevance = item.get("relevance_score")
        relevance_value: Optional[float] = None
        if isinstance(relevance, (int, float)):
            relevance_value = float(relevance)
        scored.append((relevance_value, item))

    scored.sort(key=lambda pair: (pair[0] is None, -(pair[0] or 0)))
    highlights = []
    for _, item in scored[:limit]:
        title = item.get("title") or "Untitled evidence"
        source = item.get("source") or "unknown source"
        quality = item.get("quality") or "unknown quality"
        highlights.append(f"{title} ({source}, {quality})")
    return highlights


def _render_executive_summary(result: Dict[str, Any]) -> str:
    scores = result.get("scores", {})
    evidence = result.get("evidence", [])
    subject = result.get("subject", {})
    overall = scores.get("overall_score", 0)
    confidence = scores.get("confidence", 0)
    signal_strength = scores.get("dimensional_scores", {}).get("signal_strength", 0)
    target = subject.get("target_name", "the target")

    tier = "Low"
    if overall >= 70:
        tier = "High"
    elif overall >= 40:
        tier = "Medium"

    summary = (
        f"{target} receives a {tier} attractiveness rating with an overall score of {overall}. "
        f"Confidence is {confidence} based on {len(evidence)} evidence items and signal strength {signal_strength}."
    )
    return f"""
    <section>
      <h2>Executive Summary</h2>
      <p>{_escape(summary)}</p>
    </section>
    """


def _render_quality_legend() -> str:
    return """
    <section>
      <h2>Signal Quality Legend</h2>
      <ul>
        <li><strong>official</strong>: government, international organizations, or tender portals</li>
        <li><strong>media</strong>: news outlets or commercial publishers</li>
        <li><strong>unknown</strong>: unclear or missing source metadata</li>
      </ul>
    </section>
    """


def _render_key_takeaways(result: Dict[str, Any]) -> str:
    evidence = result.get("evidence", [])
    scores = result.get("scores", {})
    breakdown = scores.get("confidence_breakdown", {})
    sources = scores.get("confidence_sources", {})
    takeaways = []

    if scores.get("overall_score", 0) >= 70:
        takeaways.append("Overall attractiveness is high.")
    elif scores.get("overall_score", 0) >= 40:
        takeaways.append("Overall attractiveness is moderate.")
    else:
        takeaways.append("Overall attractiveness is low.")

    if scores.get("confidence", 0) >= 70:
        takeaways.append("Confidence is strong with solid data coverage.")
    elif scores.get("confidence", 0) >= 40:
        takeaways.append("Confidence is moderate; review evidence quality.")
    else:
        takeaways.append("Confidence is low; data gaps remain.")

    if breakdown.get("has_imports_goods_services"):
        takeaways.append("Import volume data is available.")
    else:
        takeaways.append("Import volume data is missing.")

    if sources.get("official", 0) >= 3:
        takeaways.append("Multiple official sources support the analysis.")
    elif sources.get("official", 0) == 0:
        takeaways.append("No official sources detected; validate with primary data.")

    takeaways.append(f"Evidence items collected: {len(evidence)}.")

    items = "".join(f"<li>{_escape(item)}</li>" for item in takeaways)
    return f"""
    <section>
      <h2>Key Takeaways</h2>
      <ul>
        {items}
      </ul>
    </section>
    """


def _render_run_delta(result: Dict[str, Any]) -> str:
    delta = result.get("report_delta")
    if not delta:
        return ""
    rows = "".join(
        f"<tr><th>{_escape(key.replace('_', ' ').title())}</th><td>{_escape(value)}</td></tr>"
        for key, value in delta.items()
    )
    return f"""
    <section>
      <h2>Change vs Previous Run</h2>
      <table class="kv">
        {rows}
      </table>
    </section>
    """


def build_html_report(result: Dict[str, Any]) -> str:
    subject = result.get("subject", {})
    resolved = result.get("resolved", {})
    macro = result.get("macro", {})
    trade_signals = result.get("trade_signals", {})
    policy_signals = result.get("policy_signals", {})
    scores = result.get("scores", {})
    scoring_config = result.get("scoring_config", {})
    evidence = result.get("evidence", [])
    query_plan = result.get("query_plan", [])
    tender_filters = result.get("tender_filters", [])
    warnings = result.get("warnings", [])
    sources = result.get("data_sources", [])

    warnings_html = ""
    if warnings:
        warnings_html = "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in warnings) + "</ul>"

    queries_html = "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in query_plan) + "</ul>"
    sources_html = "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in sources) + "</ul>"
    tender_filters_html = "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in tender_filters) + "</ul>"

    executive_summary = _render_executive_summary(result)
    narrative = build_score_narrative(result)
    quality_legend = _render_quality_legend()
    key_takeaways = _render_key_takeaways(result)
    run_delta = _render_run_delta(result)

    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>Market Opportunity OSINT Report</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 32px;
          color: #111827;
        }}
        h1 {{ margin-bottom: 8px; }}
        h2 {{ margin-top: 24px; }}
        .meta {{ color: #6b7280; font-size: 14px; }}
        table {{
          border-collapse: collapse;
          width: 100%;
          margin-top: 8px;
        }}
        th, td {{
          border: 1px solid #e5e7eb;
          padding: 8px;
          text-align: left;
          vertical-align: top;
        }}
        th {{ background: #f9fafb; }}
        .kv th {{ width: 240px; }}
        .evidence td {{ font-size: 13px; }}
      </style>
    </head>
    <body>
      <h1>Market Opportunity OSINT Report</h1>
      <p class="meta">Generated with open-source intelligence only.</p>

      {_render_kv_table("Subject", subject)}
      {_render_kv_table("Resolved Target", resolved)}
      {_render_kv_table("Macro Data", macro)}
      <section>
        <h2>Analyst Narrative</h2>
        <p>{_escape(narrative["summary"])}</p>
        <h3>Why this score</h3>
        <ul>
          { "".join(f"<li>{_escape(item)}</li>" for item in narrative["justification"]) }
        </ul>
        { "<h3>Key evidence highlights</h3><ul>" + "".join(f"<li>{_escape(item)}</li>" for item in narrative["key_evidence"]) + "</ul>" if narrative["key_evidence"] else "" }
        { "<h3>Gaps to validate</h3><ul>" + "".join(f"<li>{_escape(item)}</li>" for item in narrative["gaps"]) + "</ul>" if narrative["gaps"] else "" }
      </section>
      {quality_legend}
      {key_takeaways}
      {run_delta}
      {executive_summary}
      {_render_scores(scores)}
      {_render_kv_table("Scoring Weights", scoring_config.get("weights", {}))}
      {_render_kv_table("Trade Signals", {payload.get("label"): payload.get("value") for payload in trade_signals.values()})}
      {_render_kv_table("Policy Signals", {payload.get("label"): payload.get("value") for payload in policy_signals.values()})}

      <section>
        <h2>Warnings</h2>
        {warnings_html or "<p>None.</p>"}
      </section>

      <section>
        <h2>Query Plan</h2>
        {queries_html}
      </section>

      <section>
        <h2>Tender Filters</h2>
        {tender_filters_html}
      </section>

      {_render_evidence(evidence)}

      <section>
        <h2>Data Sources</h2>
        {sources_html}
      </section>
    </body>
    </html>
    """
    return html
