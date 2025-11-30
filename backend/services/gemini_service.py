import google.generativeai as genai
import os
import json
import logging


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
        prompt = f"""
        You are a strategic business analyst specializing in international market entry for tire recycling companies.
        Conduct a comprehensive, critical analysis of the tire recycling market opportunity in {country_name} for an Iranian company.
        
        **CRITICAL CONTEXT:**
        - The client is an Iranian company seeking to export tire recycling products OR establish recycling projects in {country_name}
        - Iran faces international sanctions - this MUST be factored into all analysis
        - Analysis must be realistic, critical, and actionable - not generic or overly optimistic
        
        **DATA PROVIDED:**
        - GDP: ${data.get('gdp', 0):,.0f}
        - Population: {data.get('population', 0):,.0f}
        - Estimated Annual Tire Waste: {data.get('tire_waste', 0):,.0f} units
        
        **RECENT NEWS & MARKET INTELLIGENCE:**
        {json.dumps(data.get('news', []), indent=2, ensure_ascii=False)}
        
        **ANALYTICAL FRAMEWORK - Apply ALL of the following:**
        
        1. **SWOT ANALYSIS** (Iran-{country_name} tire recycling context):
           - Strengths: What advantages does this market offer?
           - Weaknesses: What limitations or challenges exist?
           - Opportunities: What specific opportunities can be exploited?
           - Threats: What risks could derail success?
        
        2. **PORTER'S FIVE FORCES** (Competitive Analysis):
           - Threat of new entrants
           - Bargaining power of suppliers
           - Bargaining power of buyers
           - Threat of substitutes
           - Competitive rivalry
        
        3. **PESTEL ANALYSIS**:
           - Political: Iran relations, sanctions impact, government stability
           - Economic: Market size, growth, purchasing power
           - Social: Environmental awareness, waste management culture
           - Technological: Infrastructure, recycling technology adoption
           - Environmental: Regulations, tire waste problem severity
           - Legal: Trade laws, compliance requirements
        
        4. **NEWS ANALYSIS - Critical Interpretation**:
           - Identify trends and patterns from the news
           - Assess geopolitical implications for Iran-{country_name} trade
           - Identify competitors or market players mentioned
           - Determine market timing (is now the right time?)
           - Extract actionable intelligence
        
        **REQUIRED OUTPUT (JSON format):**
        {{
            "score": <0-100 overall attractiveness>,
            
            "dimensional_scores": {{
                "market_attractiveness": <0-100: market size, growth, demand>,
                "entry_feasibility": <0-100: ease of entry, barriers, regulations>,
                "political_risk": <0-100: higher = lower risk, sanctions, stability>,
                "financial_viability": <0-100: ROI potential, profitability>,
                "strategic_fit": <0-100: alignment with Iranian capabilities>
            }},
            
            "reasoning": "<2-3 sentences explaining the overall score and key factors>",
            
            "competitive_landscape": {{
                "market_saturation": "<Low/Medium/High>",
                "key_players": ["<list existing competitors if identified from news>"],
                "competitive_advantage": "<What unique advantage can Iranian company bring?>",
                "market_gaps": "<Underserved segments or opportunities>"
            }},
            
            "market_entry_strategy": {{
                "recommended_approach": "<Direct Export / Joint Venture / Licensing / Greenfield Investment / etc.>",
                "rationale": "<Why this approach is best>",
                "key_partners": ["<Types of local partners to seek>"],
                "entry_barriers": ["<Specific barriers to overcome>"],
                "timeline": "<Estimated time to market entry>"
            }},
            
            "financial_projections": {{
                "estimated_market_size_usd": <annual market size estimate>,
                "potential_market_share": "<realistic % achievable in 3-5 years>",
                "estimated_revenue_year1": <USD>,
                "estimated_revenue_year3": <USD>,
                "initial_investment_required": <USD estimate>,
                "roi_timeline": "<months/years to break even>",
                "key_assumptions": ["<critical assumptions behind projections>"]
            }},
            
            "opportunities": [
                "<Specific, actionable opportunities - be concrete, not generic>"
            ],
            
            "risks": [
                "<Specific risks with realistic assessment>"
            ],
            
            "risk_mitigation_strategies": [
                {{
                    "risk": "<specific risk from above>",
                    "mitigation": "<concrete action to address it>",
                    "contingency": "<backup plan if mitigation fails>"
                }}
            ],
            
            "critical_success_factors": [
                "<What MUST go right for success?>"
            ],
            
            "implementation_roadmap": [
                {{
                    "phase": "<Phase name>",
                    "timeline": "<timeframe>",
                    "key_activities": ["<specific actions>"],
                    "milestones": ["<measurable outcomes>"]
                }}
            ],
            
            "news_analysis": "<Detailed analysis of news headlines with critical insights. Format as numbered points (1. 2. 3.) with bold headers using **Header:** followed by explanation. Focus on: trends, geopolitical implications, competitive intelligence, market timing, actionable insights.>",
            
            "news_references": [
                {{"title": "<news title>", "url": "<url>"}}
            ],
            
            "regulations": "<Summary of environmental/trade regulations>",
            
            "sanctions_impact": {{
                "severity": "<Low/Medium/High>",
                "specific_restrictions": ["<any known sanctions affecting Iran-{country_name} trade>"],
                "workarounds": ["<legal strategies to navigate restrictions>"]
            }},
            
            "executive_summary": "<3-4 sentence summary: Is this opportunity worth pursuing? What's the bottom line recommendation?>"
        }}
        
        **CRITICAL INSTRUCTIONS:**
        - Be REALISTIC and CRITICAL - avoid generic optimism
        - Use the news data to inform your analysis with specific, current insights
        - All financial estimates should be grounded in the GDP, population, and market data
        - Consider Iran's geopolitical position in ALL recommendations
        - Provide ACTIONABLE insights, not theoretical frameworks
        - If data is insufficient, state assumptions clearly
        
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
                
            return json.loads(text)
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
        {json.dumps(analysis, ensure_ascii=False, indent=2)}
        
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
