import google.generativeai as genai
import os
import json
import logging

from models.analysis import AnalysisModel

logger = logging.getLogger(__name__)

class GeminiConfigurationError(Exception):
    pass

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables.")
            raise GeminiConfigurationError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_search_query(self, country_name: str) -> str:
        prompt = f"""
        Generate a search query to find news about "tire recycling projects" and "trade with Iran" in {country_name}.
        The query should include terms in the primary local language of {country_name} AND in English.
        Return ONLY the query string, nothing else. Do not use quotes around the output.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return f"tire recycling news {country_name} Iran export"

    def analyze_market(self, country_name: str, data: dict) -> dict:
        """
        Analyzes market potential using Gemini with advanced analytical frameworks.
        """
        # Serialize news data safely
        news_json = json.dumps(data.get('news', []), indent=2, ensure_ascii=False)
        
        prompt = f"""
        You are a strategic business analyst specializing in international trade and export strategy for recycled rubber products.
        Conduct a comprehensive, critical analysis of the opportunity to EXPORT finished recycled tire products (crumb rubber, rubber flooring, fuel, etc.) from Iran to {country_name}.
        
        **CRITICAL CONTEXT:**
        - The client is an Iranian company producing recycled tire products (crumb rubber, tiles, reclaimed rubber).
        - The goal is to EXPORT these finished goods to {country_name}, NOT to build a recycling plant there.
        - Iran faces international sanctions - this MUST be factored into logistics, payments, and trade barriers.
        - Analysis must be realistic, critical, and actionable.
        
        **DATA PROVIDED:**
        - GDP: ${data.get('gdp', 0):,.0f}
        - Population: {data.get('population', 0):,.0f}
        
        **RECENT NEWS & MARKET INTELLIGENCE:**
        {news_json}
        
        **ANALYTICAL FRAMEWORK - Apply ALL of the following:**
        
        1. **SWOT ANALYSIS** (Iranian Export Context):
           - Strengths: Price competitiveness of Iranian products? Quality?
           - Weaknesses: Logistics costs, payment difficulties, branding?
           - Opportunities: Growing construction sector in {country_name}? Automotive demand?
           - Threats: Tariffs, border closures, competitors (China/Turkey).
        
        2. **PORTER'S FIVE FORCES** (Export Market):
           - Threat of new entrants (other exporters)
           - Bargaining power of suppliers (shipping/logistics providers)
           - Bargaining power of buyers (importers/distributors in {country_name})
           - Threat of substitutes (virgin rubber, other materials)
           - Competitive rivalry (price wars with other exporting nations)
        
        3. **PESTEL ANALYSIS**:
           - Political: Trade agreements with Iran, sanctions enforcement.
           - Economic: Currency exchange rates, purchasing power, construction boom.
           - Social: Acceptance of Iranian products.
           - Technological: Logistics infrastructure.
           - Environmental: Standards for imported recycled materials.
           - Legal: Import tariffs, customs regulations, compliance.
        
        4. **NEWS ANALYSIS - Critical Interpretation**:
           - Identify specific demand signals (infrastructure projects, automotive growth).
           - Assess trade sentiment towards Iran.
           - Identify potential partners or competitors mentioned.
        
        **REQUIRED OUTPUT (JSON format):**
        {{
            "score": <0-100 overall export attractiveness>,
            
            "dimensional_scores": {{
                "market_demand": <0-100: demand for finished rubber products>,
                "trade_ease": <0-100: tariffs, customs, logistics>,
                "political_risk": <0-100: higher = lower risk, sanctions, stability>,
                "financial_viability": <0-100: profit margin potential>,
                "strategic_fit": <0-100: alignment with Iranian export capabilities>
            }},
            
            "reasoning": "<2-3 sentences explaining the overall score and key factors>",
            
            "competitive_landscape": {{
                "market_saturation": "<Low/Medium/High>",
                "key_players": ["<list major competitors/exporters to this market>"],
                "competitive_advantage": "<How can Iranian products compete? (Price/Quality/Proximity)>",
                "market_gaps": "<Underserved segments (e.g., low-cost flooring)>"
            }},
            
            "market_entry_strategy": {{
                "recommended_approach": "<Direct Export / Local Distributor / Agent / Joint Venture>",
                "rationale": "<Why this approach is best for this specific market>",
                "key_partners": ["<Types of partners: e.g., Construction firms, Wholesalers>"],
                "entry_barriers": ["<Tariffs, Certifications, Sanctions>"],
                "timeline": "<Time to first shipment>"
            }},
            
            "financial_projections": {{
                "estimated_market_size_usd": <annual import market size estimate>,
                "potential_market_share": "<realistic % achievable>",
                "estimated_revenue_year1": <USD>,
                "estimated_revenue_year3": <USD>,
                "initial_investment_required": <USD (marketing, certifications, logistics setup)>,
                "roi_timeline": "<months to break even on initial setup>",
                "key_assumptions": ["<critical assumptions>"]
            }},
            
            "opportunities": [
                "<Specific export opportunities - e.g., 'Supply rubber tiles for new stadium project'>"
            ],
            
            "risks": [
                "<Specific export risks - e.g., 'Border closure due to security'>"
            ],
            
            "risk_mitigation_strategies": [
                {{
                    "risk": "<specific risk>",
                    "mitigation": "<action>",
                    "contingency": "<backup>"
                }}
            ],
            
            "critical_success_factors": [
                "<What MUST go right? e.g., 'Securing reliable payment channel'>"
            ],
            
            "implementation_roadmap": [
                {{
                    "phase": "<Phase name>",
                    "timeline": "<timeframe>",
                    "key_activities": ["<specific actions>"],
                    "milestones": ["<measurable outcomes>"]
                }}
            ],
            
            "news_analysis": "<Detailed analysis of news. Format as numbered points (1. 2. 3.) with bold headers using **Header:** followed by explanation.>",
            
            "news_references": [
                {{"title": "<news title>", "url": "<url>"}}
            ],
            
            "regulations": "<Summary of import duties and standards>",
            
            "sanctions_impact": {{
                "severity": "<Low/Medium/High>",
                "specific_restrictions": ["<banking/shipping restrictions>"],
                "workarounds": ["<legal payment methods, third-party logistics>"]
            }},
            
            "executive_summary": "<3-4 sentence summary: Should we export to this country?>"
        }}
        
        **CRITICAL INSTRUCTIONS:**
        - Focus ONLY on EXPORT of finished goods.
        - Do NOT suggest building a factory.
        - Be realistic about Sanctions and Banking issues.
        
        Return ONLY valid JSON, no additional text.
        """
        
        try:
            if not self.model:
                raise Exception("Gemini API key not configured")
                
            response = self.model.generate_content(prompt)
            # Extract JSON from response (handle potential markdown formatting)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            parsed = json.loads(text)
            validated = AnalysisModel.model_validate(parsed)
            return validated.model_dump()
        except Exception as e:
            logger.error(f"Error analyzing market for {country_name}: {e}")
            return {
                "score": 0,
                "dimensional_scores": {
                    "market_attractiveness": 0,
                    "entry_feasibility": 0,
                    "political_risk": 0,
                    "financial_viability": 0,
                    "strategic_fit": 0
                },
                "reasoning": "Analysis failed.",
                "competitive_landscape": {
                    "market_saturation": "Unknown",
                    "key_players": [],
                    "competitive_advantage": "Unknown",
                    "market_gaps": "Unknown"
                },
                "market_entry_strategy": {
                    "recommended_approach": "Unknown",
                    "rationale": "Analysis failed",
                    "key_partners": [],
                    "entry_barriers": [],
                    "timeline": "Unknown"
                },
                "financial_projections": {
                    "estimated_market_size_usd": 0,
                    "potential_market_share": "0%",
                    "estimated_revenue_year1": 0,
                    "estimated_revenue_year3": 0,
                    "initial_investment_required": 0,
                    "roi_timeline": "Unknown",
                    "key_assumptions": []
                },
                "risks": [],
                "opportunities": [],
                "risk_mitigation_strategies": [],
                "critical_success_factors": [],
                "implementation_roadmap": [],
                "regulations": "Unknown",
                "news_analysis": "Analysis failed.",
                "news_references": [],
                "sanctions_impact": {
                    "severity": "Unknown",
                    "specific_restrictions": [],
                    "workarounds": []
                },
                "executive_summary": "Analysis failed."
            }

    def translate_to_persian(self, analysis: dict, country_name: str) -> dict:
        """
        Translates the analysis results to Persian for Iranian users.
        """
        # Serialize analysis to JSON string first
        analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Translate the following market analysis JSON to Persian (Farsi).
        
        CRITICAL RULES:
        1. Keep all JSON keys in English (e.g., "reasoning", "risks", "market_entry_strategy", "recommended_approach").
        2. Translate ALL string values to Persian.
        3. Do NOT translate numbers or boolean values.
        4. For objects like 'market_entry_strategy', translate the values of its fields (e.g., translate the value of 'recommended_approach' to Persian).
        5. For lists of strings (like 'risks'), translate each string item to Persian.
        6. For lists of objects (like 'risk_mitigation_strategies'), translate the string values within each object to Persian.
        
        Original Analysis:
        {analysis_json}
        
        Target Audience: Iranian business executives. Use professional business terminology.
        
        Ensure the response is valid JSON with proper Persian text encoding.
        """

        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error translating to Persian: {e}")
            return analysis  # Return original if translation fails
