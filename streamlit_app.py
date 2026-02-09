import json
import os
import sys
from datetime import datetime
from typing import Dict, List

import pandas as pd

import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from models.subject import Subject
from services.osint_pipeline import analyze_subject, SubjectResolutionError
from services.report import build_html_report
from services.pdf_report import build_pdf_report

load_dotenv()

st.set_page_config(
    page_title="Market Opportunity OSINT",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRESET_PATH = os.path.join(os.path.dirname(__file__), "backend", ".cache", "weight_presets.json")
RUN_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "backend", ".cache", "run_history.json")


def _load_presets() -> Dict[str, Dict[str, float]]:
    if not os.path.exists(PRESET_PATH):
        return {}
    try:
        with open(PRESET_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _save_presets(presets: Dict[str, Dict[str, float]]) -> None:
    os.makedirs(os.path.dirname(PRESET_PATH), exist_ok=True)
    with open(PRESET_PATH, "w", encoding="utf-8") as handle:
        json.dump(presets, handle, ensure_ascii=False, indent=2)


def _load_run_history() -> List[Dict[str, str]]:
    if not os.path.exists(RUN_HISTORY_PATH):
        return []
    try:
        with open(RUN_HISTORY_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return []


def _save_run_history(history: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(RUN_HISTORY_PATH), exist_ok=True)
    with open(RUN_HISTORY_PATH, "w", encoding="utf-8") as handle:
        json.dump(history, handle, ensure_ascii=False, indent=2)

def _parse_csv_list(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def suggest_hs_codes(product_text: str) -> List[str]:
    config_path = os.path.join(os.path.dirname(__file__), "backend", "config", "hs_codes.json")
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        categories = payload.get("categories", {})
        product_text = product_text.lower()
        suggestions = []
        for key, codes in categories.items():
            if key.replace("_", " ") in product_text or key in product_text:
                suggestions.extend(codes)
        return suggestions
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def run_analysis(subject_payload: dict, scoring_payload: dict):
    subject = Subject(**subject_payload)
    return analyze_subject(subject, scoring_config=scoring_payload)


st.title("Market Opportunity OSINT")
st.caption("Evidence-first research for export market screening using open sources.")
st.markdown(
    """
This tool helps analysts quickly screen export markets using public data and OSINT.  
Fill the **Subject Definition** on the left, run the analysis, and review the evidence-backed score.
"""
)

with st.expander("How to interpret the score", expanded=False):
    st.markdown(
        """
- **Overall score**: weighted composite of the dimensions you set in the sidebar.  
- **Confidence**: data availability + evidence mix (news, trade, policy, tenders).  
- **Evidence Pack**: raw sources used to justify the score. Always review before decisions.
"""
    )

if "comparisons" not in st.session_state:
    st.session_state["comparisons"] = []
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "run_history" not in st.session_state:
    st.session_state["run_history"] = _load_run_history()

with st.sidebar:
    st.subheader("Subject Definition")
    if st.button("Quick Start: Turkey (Rubber Exports)"):
        st.session_state["quick_start"] = {
            "target_type": "country",
            "target_name": "Turkey",
            "region": "Middle East",
            "products": "crumb rubber, rubber tiles",
            "signals": "import growth, construction projects, tenders",
            "risks": "sanctions, customs delays, currency controls",
            "hs_codes": "4004, 4016",
            "languages": "en,tr",
            "tender_feeds": "",
        }
        st.success("Quick Start applied. Review inputs and run analysis.")
    quick = st.session_state.get("quick_start", {})
    target_type_options = ["country", "sector", "product", "company", "supply_chain"]
    target_type_index = 0
    if quick.get("target_type") in target_type_options:
        target_type_index = target_type_options.index(quick.get("target_type"))
    target_type = st.selectbox(
        "Target type",
        target_type_options,
        index=target_type_index,
        help="Country targets are fully supported. Others return limited data for now.",
    )
    target_name = st.text_input(
        "Target name",
        placeholder="e.g., Turkey",
        help="Required.",
        value=quick.get("target_name", ""),
    )

    with st.expander("Core Inputs", expanded=True):
        region = st.text_input(
            "Region (optional)",
            placeholder="e.g., Middle East",
            value=quick.get("region", ""),
        )
        products = st.text_area(
            "Products (comma-separated)",
            placeholder="crumb rubber, rubber tiles",
            help="Used to build targeted search queries.",
            value=quick.get("products", ""),
        )
        signals = st.text_area(
            "Signals of interest (comma-separated)",
            placeholder="import growth, construction projects, tenders",
            help="Keywords prioritized in OSINT searches.",
            value=quick.get("signals", ""),
        )
        risks = st.text_area(
            "Risk focus (comma-separated)",
            placeholder="sanctions, customs delays, currency controls",
            help="Risk-related signals to emphasize.",
            value=quick.get("risks", ""),
        )
        time_horizon = st.slider(
            "Time horizon (months)",
            min_value=1,
            max_value=36,
            value=12,
            help="Used for OSINT freshness targets where supported.",
        )

    beginner_mode = st.toggle("Beginner mode", value=True, help="Hides advanced inputs unless disabled.")

    if not beginner_mode:
        with st.expander("Advanced Inputs", expanded=True):
            st.caption("Tip: You can auto-suggest HS codes from product keywords.")
            hs_codes = st.text_input(
                "HS codes (comma-separated)",
                placeholder="4004, 4016",
                help="Optional: used to generate HS-code specific queries.",
                value=quick.get("hs_codes", ""),
            )
            if st.button("Suggest HS codes"):
                suggested = suggest_hs_codes(products)
                if suggested:
                    hs_codes = ", ".join(sorted(set(suggested)))
                    st.session_state["suggested_hs_codes"] = hs_codes
                    st.success(f"Suggested HS codes: {hs_codes}")
                else:
                    st.info("No HS code suggestions found.")
            languages = st.text_input(
                "Languages (comma-separated)",
                help="Used for query generation (multilingual support is limited).",
                value=quick.get("languages", "en"),
            )
            tender_feeds = st.text_area(
                "Tender RSS/Atom feeds (comma-separated URLs)",
                placeholder="https://example.com/tenders/rss",
                help="Optional: add official tender feeds to include in evidence.",
                value=quick.get("tender_feeds", ""),
            )
    else:
        hs_codes = ""
        languages = "en"
        tender_feeds = ""
    st.subheader("Scoring Weights")
    presets = _load_presets()
    preset_names = ["Default"] + sorted(presets.keys())
    selected_preset = st.selectbox("Preset", preset_names, index=0)

    if "weights" not in st.session_state:
        st.session_state["weights"] = {
            "market_demand": 0.35,
            "trade_ease": 0.2,
            "political_risk": 0.2,
            "financial_viability": 0.15,
            "strategic_fit": 0.1,
        }

    if selected_preset != "Default" and selected_preset in presets:
        st.session_state["weights"] = presets[selected_preset]

    col_a, col_b = st.columns(2)
    with col_a:
        w_market = st.number_input(
            "Market demand",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["weights"]["market_demand"]),
            step=0.05,
        )
        w_trade = st.number_input(
            "Trade ease",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["weights"]["trade_ease"]),
            step=0.05,
        )
        w_risk = st.number_input(
            "Political risk",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["weights"]["political_risk"]),
            step=0.05,
        )
    with col_b:
        w_fin = st.number_input(
            "Financial viability",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["weights"]["financial_viability"]),
            step=0.05,
        )
        w_fit = st.number_input(
            "Strategic fit",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state["weights"]["strategic_fit"]),
            step=0.05,
        )

    st.session_state["weights"] = {
        "market_demand": w_market,
        "trade_ease": w_trade,
        "political_risk": w_risk,
        "financial_viability": w_fin,
        "strategic_fit": w_fit,
    }

    st.caption("Weights are normalized automatically during scoring.")
    preset_name = st.text_input("Save preset as", value="")
    if st.button("Save preset") and preset_name.strip():
        presets[preset_name.strip()] = st.session_state["weights"]
        _save_presets(presets)
        st.success("Preset saved.")

    submit = st.button("Run OSINT Analysis")

if submit:
    if not target_name.strip():
        st.error("Target name is required.")
        st.stop()

    subject_payload = {
        "target_type": target_type,
        "target_name": target_name.strip(),
        "region": region.strip() or None,
        "products": _parse_csv_list(products),
        "hs_codes": _parse_csv_list(hs_codes),
        "signals_of_interest": _parse_csv_list(signals),
        "risk_focus": _parse_csv_list(risks),
        "time_horizon_months": time_horizon,
        "languages": _parse_csv_list(languages) or ["en"],
        "tender_feeds": _parse_csv_list(tender_feeds),
    }

    scoring_payload = {
        "weights": {
            "market_demand": w_market,
            "trade_ease": w_trade,
            "political_risk": w_risk,
            "financial_viability": w_fin,
            "strategic_fit": w_fit,
        }
    }

    with st.spinner("Running OSINT pipeline..."):
        try:
            result = run_analysis(subject_payload, scoring_payload)
        except SubjectResolutionError as exc:
            st.error(str(exc))
            st.stop()
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
            st.stop()

    st.subheader("Overall Score")
    st.metric("OSINT Market Score", result["scores"]["overall_score"])
    st.caption(result["scores"]["rationale"])
    st.metric("Confidence", result["scores"]["confidence"])

    if result["scores"].get("confidence_sources", {}).get("official", 0) == 0:
        st.warning("No official sources detected. Validate with primary data before decisions.")

    if result.get("warnings"):
        st.warning(" | ".join(result["warnings"]))

    if st.button("Add to comparison list"):
        comparison_row = {
            "target": result["subject"].get("target_name"),
            "type": result["subject"].get("target_type"),
            "overall_score": result["scores"].get("overall_score"),
            "confidence": result["scores"].get("confidence"),
            "market_demand": result["scores"]["dimensional_scores"].get("market_demand"),
            "trade_ease": result["scores"]["dimensional_scores"].get("trade_ease"),
            "signal_strength": result["scores"]["dimensional_scores"].get("signal_strength"),
            "evidence_count": len(result.get("evidence", [])),
            "gdp": result.get("macro", {}).get("gdp"),
            "population": result.get("macro", {}).get("population"),
        }
        st.session_state["comparisons"].append(comparison_row)
        st.success("Added to comparison list.")

    report_delta = None
    if st.button("Compare with previous run"):
        previous = st.session_state.get("last_result")
        if previous:
            delta = {
                "overall_score": result["scores"].get("overall_score", 0) - previous["scores"].get("overall_score", 0),
                "confidence": result["scores"].get("confidence", 0) - previous["scores"].get("confidence", 0),
                "evidence_count": len(result.get("evidence", [])) - len(previous.get("evidence", [])),
                "official_sources": result["scores"]
                .get("confidence_sources", {})
                .get("official", 0)
                - previous["scores"].get("confidence_sources", {}).get("official", 0),
            }
            st.info("Comparison against last run")
            st.json(delta)
            report_delta = delta
        else:
            st.info("No previous run available yet.")

    report_payload = dict(result)
    if report_delta:
        report_payload["report_delta"] = report_delta

    report_html = build_html_report(report_payload)
    report_pdf = build_pdf_report(report_payload)
    st.download_button(
        label="Download HTML Report",
        data=report_html,
        file_name="osint_report.html",
        mime="text/html",
    )
    st.download_button(
        label="Download PDF Brief",
        data=report_pdf,
        file_name="osint_report.pdf",
        mime="application/pdf",
    )

    st.session_state["run_history"].append(
        {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "target": result["subject"].get("target_name"),
            "type": result["subject"].get("target_type"),
            "overall_score": result["scores"].get("overall_score"),
            "confidence": result["scores"].get("confidence"),
            "official_sources": result["scores"].get("confidence_sources", {}).get("official", 0),
            "evidence_count": len(result.get("evidence", [])),
        }
    )
    _save_run_history(st.session_state["run_history"])

    st.session_state["last_result"] = result

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Dimensional Scores")
        st.dataframe(
            [
                {"dimension": key.replace("_", " ").title(), "score": value}
                for key, value in result["scores"]["dimensional_scores"].items()
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Evidence Pack")
        st.caption("Quality labels: official (government/international), media, or unknown.")
        if result["evidence"]:
            relevance_values = [
                item.get("relevance_score", 0)
                for item in result["evidence"]
                if isinstance(item.get("relevance_score"), (int, float))
            ]
            if relevance_values:
                st.subheader("Relevance Histogram")
                st.caption("Higher values indicate stronger keyword match to your subject.")
                st.bar_chart(pd.Series(relevance_values))
            st.dataframe(result["evidence"], use_container_width=True, hide_index=True)
        else:
            st.info("No evidence collected. Check API keys or adjust queries.")

    with col2:
        st.subheader("Resolved Target")
        st.json(result.get("resolved", {}))

        st.subheader("Macro Data")
        st.json(result.get("macro", {}))

        st.subheader("Trade Signals")
        st.json(result.get("trade_signals", {}))

        st.subheader("Policy Signals")
        st.json(result.get("policy_signals", {}))

        st.subheader("Confidence Breakdown")
        st.json(result["scores"].get("confidence_breakdown", {}))

        st.subheader("Confidence Sources")
        st.json(result["scores"].get("confidence_sources", {}))

        st.subheader("Query Plan")
        st.write(result.get("query_plan", []))

        st.subheader("Tender Filters")
        st.write(result.get("tender_filters", []))

        st.subheader("Data Sources")
        st.write(result.get("data_sources", []))

st.markdown("---")
st.subheader("Comparison View")
st.caption("Compare multiple analyses side-by-side. Add items using the button above.")
if st.session_state["comparisons"]:
    df = pd.DataFrame(st.session_state["comparisons"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        label="Download Comparison CSV",
        data=df.to_csv(index=False),
        file_name="osint_comparison.csv",
        mime="text/csv",
    )
    if st.button("Clear comparison list"):
        st.session_state["comparisons"] = []
        st.info("Comparison list cleared.")
else:
    st.info("No comparisons yet. Run an analysis and click 'Add to comparison list'.")

st.markdown("---")
st.subheader("Run History")
st.caption("Note: Cloud deployments may reset local storage on redeploy.")
st.caption("Tip: Export run history for long-term storage and re-import when needed.")
uploaded_history = st.file_uploader("Import run history (JSON)", type=["json"])
if uploaded_history:
    try:
        imported = json.load(uploaded_history)
        if isinstance(imported, list):
            st.session_state["run_history"] = imported
            _save_run_history(imported)
            st.success("Run history imported.")
        else:
            st.error("Invalid history format. Expected a list of records.")
    except Exception:
        st.error("Failed to parse uploaded JSON.")
if st.session_state["run_history"]:
    history_df = pd.DataFrame(st.session_state["run_history"])
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    st.download_button(
        label="Download Run History JSON",
        data=json.dumps(st.session_state["run_history"], ensure_ascii=False, indent=2),
        file_name="osint_run_history.json",
        mime="application/json",
    )
    st.download_button(
        label="Download Run History CSV",
        data=history_df.to_csv(index=False),
        file_name="osint_run_history.csv",
        mime="text/csv",
    )
else:
    st.info("No runs yet.")
