import streamlit as st
import sys
import os
import pandas as pd
import pycountry
from dotenv import load_dotenv

# Add backend to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.scoring_engine import ScoringEngine
from exceptions import GeminiConfigurationError

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Market Opportunity Finder",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f9fafb;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .score-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .score-green { background-color: #dcfce7; color: #15803d; }
    .score-yellow { background-color: #fef9c3; color: #a16207; }
    .score-red { background-color: #fee2e2; color: #b91c1c; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🌍 Market Opportunity Finder")
st.markdown("Identify and score tire recycling opportunities.")

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")
    st.info("This tool analyzes market opportunities for tire recycling businesses.")

# Main Input Area
col1, col2 = st.columns([2, 1])

with col1:
    country_input = st.text_input("Enter country name...", placeholder="e.g., Turkey, Armenia, Iraq")

with col2:
    # Add some spacing to align button with input
    st.write("") 
    st.write("")
    analyze_btn = st.button("Analyze Market")

# Initialize session state for results
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# Analysis Logic
if analyze_btn and country_input:
    with st.spinner(f"Analyzing market opportunities in {country_input}..."):
        try:
            # 1. Resolve Country
            try:
                country = pycountry.countries.search_fuzzy(country_input)[0]
                country_code = country.alpha_2
                country_name = country.name
            except LookupError:
                st.error(f"Country '{country_input}' not found.")
                st.stop()
            except Exception as e:
                st.error(f"Error validating country: {str(e)}")
                st.stop()

            # 2. Run Scoring Engine
            scoring_engine = ScoringEngine()
            result = scoring_engine.score_country(country_code, country_name)
            
            st.session_state.analysis_result = result
            st.session_state.error_message = None
            
        except GeminiConfigurationError as e:
            st.session_state.error_message = f"Configuration Error: {str(e)}"
        except Exception as e:
            st.session_state.error_message = f"An unexpected error occurred: {str(e)}"

# Display Error if any
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# Display Results
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    # Language Toggle
    lang_col1, lang_col2 = st.columns([1, 5])
    with lang_col1:
        language = st.radio("Language", ["English", "Persian"], horizontal=True)
    
    is_persian = language == "Persian"
    current_analysis = result['analysis_persian'] if is_persian else result['analysis']
    
    # Top Section: Title and Score
    st.markdown("---")
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        st.subheader(f"Analysis for {result['country']}")
    
    with header_col2:
        score = current_analysis.get('score', 0)
        score_class = "score-green" if score >= 70 else "score-yellow" if score >= 40 else "score-red"
        st.markdown(f"""
            <div class="score-card {score_class}">
                {score}/100
            </div>
        """, unsafe_allow_html=True)

    # Executive Summary
    if current_analysis.get('executive_summary'):
        st.info(f"**{'خلاصه مدیریتی' if is_persian else 'Executive Summary'}**: {current_analysis['executive_summary']}")

    # Sanctions Impact (if any)
    if current_analysis.get('sanctions_impact'):
        sanctions = current_analysis['sanctions_impact']
        with st.expander(f"{'تاثیر تحریم‌ها' if is_persian else 'Sanctions Impact'}", expanded=True):
            st.error(f"**{'شدت' if is_persian else 'Severity'}:** {sanctions.get('severity', 'Unknown')}")
            for restriction in sanctions.get('specific_restrictions', []):
                st.markdown(f"- {restriction}")

    # Key Metrics (GDP, Pop) & Dimensional Scores
    col_metrics, col_scores = st.columns([1, 1])
    
    with col_metrics:
        st.markdown(f"### {'داده‌های کلیدی' if is_persian else 'Key Data'}")
        gdp_val = result['data'].get('gdp', 0)
        pop_val = result['data'].get('population', 0)
        
        m1, m2 = st.columns(2)
        m1.metric("GDP", f"${gdp_val/1e9:.2f}B")
        m2.metric("Population", f"{pop_val/1e6:.1f}M")
        
        # Map
        if result['data'].get('lat') and result['data'].get('lng'):
            map_data = pd.DataFrame({
                'lat': [result['data']['lat']],
                'lon': [result['data']['lng']]
            })
            st.map(map_data, zoom=4)

    with col_scores:
        st.markdown(f"### {'امتیازات ابعادی' if is_persian else 'Dimensional Scores'}")
        scores = current_analysis.get('dimensional_scores', {})
        for key, value in scores.items():
            st.text(f"{key.replace('_', ' ').title()}")
            st.progress(value / 100)

    # Detailed Sections
    st.markdown("---")
    
    # Financials & Entry Strategy
    row1_1, row1_2 = st.columns(2)
    
    with row1_1:
        st.markdown(f"### 💰 {'پیش‌بینی‌های مالی' if is_persian else 'Financial Projections'}")
        fin = current_analysis.get('financial_projections', {})
        st.success(f"**{'درآمد سال اول' if is_persian else 'Year 1 Revenue'}:** ${fin.get('estimated_revenue_year1', 0):,}")
        st.info(f"**{'بازگشت سرمایه' if is_persian else 'ROI Timeline'}:** {fin.get('roi_timeline', 'N/A')}")

    with row1_2:
        st.markdown(f"### 🚀 {'استراتژی ورود' if is_persian else 'Entry Strategy'}")
        entry = current_analysis.get('market_entry_strategy', {})
        st.markdown(f"**{'رویکرد' if is_persian else 'Approach'}:** {entry.get('recommended_approach', 'N/A')}")
        st.caption(entry.get('rationale', ''))

    # Reasoning, Opportunities, Risks
    st.markdown("### 📊 {'تحلیل دقیق' if is_persian else 'Detailed Analysis'}")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Reasoning" if not is_persian else "تحلیل",
        "Opportunities" if not is_persian else "فرصت‌ها",
        "Risks" if not is_persian else "ریسک‌ها",
        "News" if not is_persian else "اخبار"
    ])
    
    with tab1:
        st.write(current_analysis.get('reasoning', ''))
        
        # Competitive Landscape
        if current_analysis.get('competitive_landscape'):
            st.markdown("#### Competitive Landscape")
            comp = current_analysis['competitive_landscape']
            st.markdown(f"**Saturation:** {comp.get('market_saturation')}")
            st.markdown(f"**Advantage:** {comp.get('competitive_advantage')}")

    with tab2:
        for opp in current_analysis.get('opportunities', []):
            st.markdown(f"✅ {opp}")

    with tab3:
        for risk in current_analysis.get('risks', []):
            st.markdown(f"⚠️ {risk}")
        
        if current_analysis.get('risk_mitigation_strategies'):
            st.markdown("#### Mitigation Strategies")
            for strat in current_analysis['risk_mitigation_strategies']:
                st.markdown(f"**{strat.get('risk')}**: {strat.get('mitigation')}")

    with tab4:
        news_text = current_analysis.get('news_analysis', '')
        if news_text:
            st.markdown(news_text)
        
        refs = current_analysis.get('news_references', [])
        if refs:
            st.markdown("#### References")
            for ref in refs:
                st.markdown(f"- [{ref.get('title')}]({ref.get('url')})")

    # Roadmap
    if current_analysis.get('implementation_roadmap'):
        st.markdown(f"### 📅 {'نقشه راه' if is_persian else 'Implementation Roadmap'}")
        for phase in current_analysis['implementation_roadmap']:
            with st.expander(f"{phase.get('phase')} ({phase.get('timeline')})"):
                for activity in phase.get('key_activities', []):
                    st.markdown(f"- {activity}")

