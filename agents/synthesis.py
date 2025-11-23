"""
Synthesis and Plan Generation agents
Phase 2 Implementation
"""
import os
from utils.state import ResearchState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv('GEMINI_API_KEY')
)


def verification_node(state: ResearchState) -> ResearchState:
    """
    Verification agent - detects conflicts in research data
    """
    state['progress_messages'].append("🔍 Verifying information for conflicts...")
    
    conflicts = []
    
    try:
        # Extract research data
        web_results = state.get('web_results', [])
        financial_data = state.get('financial_data', {})
        wiki_data = state.get('wiki_data', {})
        
        # Build verification prompt
        verification_prompt = f"""You are a fact-checking agent. Review the following research data about a company and identify any CONFLICTS or CONTRADICTIONS between sources.

Target Company: {state.get('target_company_name', 'Unknown')}

Wikipedia Overview:
{wiki_data.get('summary', 'N/A') if wiki_data else 'N/A'}

Financial Data:
{financial_data if financial_data else 'N/A'}

Web Search Results (Top 3):
"""
        for i, result in enumerate(web_results[:3], 1):
            verification_prompt += f"\n{i}. {result.get('title', 'N/A')}\n   {result.get('snippet', 'N/A')[:200]}...\n"
        
        verification_prompt += """

TASK: Identify ONLY significant conflicts or contradictions. For example:
- Different founding years
- Conflicting revenue figures
- Contradictory information about headquarters location
- Different CEO names

Return your response in this EXACT format:
CONFLICTS: [YES or NO]

If YES, list each conflict like:
- [Brief description of conflict] | Sources: [source1] vs [source2] | Confidence: [HIGH/MEDIUM/LOW]

If NO, just say:
- No significant conflicts detected

Be strict - only report actual conflicts, not minor differences or updates."""

        response = llm.invoke(verification_prompt)
        content = response.content.strip()
        
        # Parse conflicts
        if "CONFLICTS: YES" in content or "conflicts detected" in content.lower():
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('-') and '|' in line:
                    parts = line.strip('- ').split('|')
                    if len(parts) >= 2:
                        conflicts.append({
                            "description": parts[0].strip(),
                            "sources": parts[1].strip() if len(parts) > 1 else "Unknown",
                            "confidence": parts[2].strip() if len(parts) > 2 else "MEDIUM"
                        })
        
        state['conflicts'] = conflicts
        
        if conflicts:
            state['progress_messages'].append(f"⚠️ Found {len(conflicts)} potential conflict(s)")
        else:
            state['progress_messages'].append("✅ No conflicts detected")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Verification failed: {str(e)}")
        state['conflicts'] = []
    
    return state


def synthesis_node(state: ResearchState) -> ResearchState:
    """
    Synthesis agent - combines all research data into a coherent summary
    """
    import os
    debug = os.getenv('DEBUG_WORKFLOW', 'false').lower() == 'true'
    if debug:
        print(f"   [SYNTHESIS] Node called - starting synthesis")

    state['progress_messages'].append("🧠 Synthesizing information...")

    try:
        # Extract all research data
        company = state.get('target_company_name', 'Unknown')
        web_results = state.get('web_results', [])
        financial_data = state.get('financial_data', {})
        wiki_data = state.get('wiki_data', {})
        news_data = state.get('news_data', [])

        if debug:
            print(f"   [SYNTHESIS] wiki_data type: {type(wiki_data)}, value: {wiki_data}")
            print(f"   [SYNTHESIS] news_data type: {type(news_data)}, length: {len(news_data) if news_data else 0}")
        
        # Build synthesis prompt
        synthesis_prompt = f"""You are a research synthesis agent. Combine all the following research data about {company} into a comprehensive, accurate summary.

Wikipedia Overview:
{wiki_data.get('summary', 'N/A') if wiki_data else 'N/A'}

Financial Information:
- Ticker: {financial_data.get('ticker', 'N/A') if financial_data else 'N/A'}
- Revenue: {financial_data.get('revenue', 'N/A') if financial_data else 'N/A'}
- Market Cap: {financial_data.get('market_cap', 'N/A') if financial_data else 'N/A'}
- Employees: {financial_data.get('employees', 'N/A') if financial_data else 'N/A'}
- Sector: {financial_data.get('sector', 'N/A') if financial_data else 'N/A'}
- Industry: {financial_data.get('industry', 'N/A') if financial_data else 'N/A'}
- Description: {financial_data.get('description', 'N/A') if financial_data else 'N/A'}

Web Research (Top 5):
"""
        for i, result in enumerate(web_results[:5], 1):
            synthesis_prompt += f"\n{i}. {result.get('title', 'N/A')}\n   {result.get('snippet', 'N/A')}\n"
        
        synthesis_prompt += f"\n\nRecent News ({len(news_data)} articles):\n"
        for i, news in enumerate(news_data[:3], 1):
            synthesis_prompt += f"{i}. {news.get('title', 'N/A')}\n"
        
        synthesis_prompt += """

Create a comprehensive synthesis with these sections:

## Company Overview
[2-3 sentences about what the company does, its position in the market]

## Business Model
[How they make money, key products/services]

## Market Position
[Market size, competitors, unique positioning]

## Recent Developments
[Recent news, initiatives, changes]

## Key Metrics
[Important numbers - revenue, employees, market cap, etc.]

## Target Customer Profile
[Who they sell to, typical customer characteristics]

Be factual, concise, and cite information confidence levels when uncertain."""

        response = llm.invoke(synthesis_prompt)
        synthesized_content = response.content.strip() if response.content else ""

        if debug:
            print(f"   [SYNTHESIS] LLM response length: {len(synthesized_content) if synthesized_content else 0}")
            print(f"   [SYNTHESIS] synthesized_content is truthy: {bool(synthesized_content)}")

        # Ensure we never set empty string (prevents infinite loop)
        if not synthesized_content:
            state['synthesized_data'] = "No synthesis generated - empty response from LLM"
            state['progress_messages'].append("⚠️ Synthesis returned empty response")
            if debug:
                print(f"   [SYNTHESIS] Set ERROR MESSAGE for synthesized_data")
        else:
            state['synthesized_data'] = synthesized_content
            state['progress_messages'].append("✅ Research synthesized successfully")
            if debug:
                print(f"   [SYNTHESIS] Set synthesized_data with {len(synthesized_content)} chars")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Synthesis failed: {str(e)}")
        # Set error message instead of None to prevent infinite loop
        state['synthesized_data'] = f"Error during synthesis: {str(e)}"
        if debug:
            print(f"   [SYNTHESIS] Exception occurred: {str(e)}")

    if debug:
        print(f"   [SYNTHESIS] Returning state with synthesized_data={'SET' if state.get('synthesized_data') else 'NONE'}")

    return state


def personalized_plan_generator_node(state: ResearchState) -> ResearchState:
    """
    Plan generator - creates comprehensive account plan ABOUT the target company
    This matches the assignment requirements: analyze a company, don't sell to them
    """
    state['progress_messages'].append("📝 Generating comprehensive account plan...")

    try:
        target = state.get('target_company_name', '')
        synthesized = state.get('synthesized_data', '')
        web_results = state.get('web_results', [])
        financial_data = state.get('financial_data', {})
        wiki_data = state.get('wiki_data', {})
        news_data = state.get('news_data', [])
        conflicts = state.get('conflicts', [])

        # Build comprehensive analysis prompt
        plan_prompt = f"""You are a business analyst creating a comprehensive account plan ABOUT {target}.

# RESEARCH DATA:

## Company Overview:
{wiki_data.get('summary', 'N/A') if wiki_data else 'N/A'}

## Financial Information:
- Ticker: {financial_data.get('ticker', 'N/A') if financial_data else 'N/A'}
- Revenue: {financial_data.get('revenue', 'N/A') if financial_data else 'N/A'}
- Market Cap: {financial_data.get('market_cap', 'N/A') if financial_data else 'N/A'}
- Sector: {financial_data.get('sector', 'N/A') if financial_data else 'N/A'}
- Industry: {financial_data.get('industry', 'N/A') if financial_data else 'N/A'}
- Description: {financial_data.get('description', 'N/A') if financial_data else 'N/A'}

## Recent News:
{chr(10).join([f"- {item.get('title', 'N/A')}" for item in news_data[:5]]) if news_data else 'N/A'}

## Web Research Insights:
{chr(10).join([f"- {item.get('snippet', 'N/A')[:200]}" for item in web_results[:5]]) if web_results else 'N/A'}

## Data Conflicts Detected:
{chr(10).join([f"- {conflict}" for conflict in conflicts]) if conflicts else 'None detected'}

---

Create a COMPREHENSIVE ACCOUNT PLAN analyzing {target}. Use this structure:

## 📋 Company Overview
[High-level summary of what the company does, their mission, and market position]

## 👔 Leadership Team
[Key executives, their backgrounds, and strategic direction]
- CEO/Founder: [Name and background]
- Key Executives: [Names, roles, notable achievements]

## 💰 Financial Snapshot
[Current financial health and performance]
- Revenue: [Amount and growth trend]
- Market Cap: [Current valuation]
- Profitability: [Profit margins, trends]
- Key Metrics: [Industry-specific KPIs]

## 📊 SWOT Analysis
**Strengths:**
- [Strength 1: Why it's a strength]
- [Strength 2: Why it's a strength]
- [Strength 3: Why it's a strength]

**Weaknesses:**
- [Weakness 1: What needs improvement]
- [Weakness 2: What needs improvement]

**Opportunities:**
- [Opportunity 1: Market trends they can leverage]
- [Opportunity 2: Expansion possibilities]

**Threats:**
- [Threat 1: Competitive/market risks]
- [Threat 2: External challenges]

## 🎯 Market Opportunities
[Where can this company grow or expand?]
1. [Opportunity 1 with reasoning]
2. [Opportunity 2 with reasoning]
3. [Opportunity 3 with reasoning]

## ⚠️ Risks & Challenges
[What challenges does this company face?]
1. [Risk 1 and potential impact]
2. [Risk 2 and potential impact]
3. [Risk 3 and potential impact]

## 📰 Recent News & Developments
[Latest significant events, launches, acquisitions]
- [Recent development 1]
- [Recent development 2]
- [Recent development 3]

## 💡 Strategic Recommendations
[What should investors/partners/analysts know?]
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## 🔍 Data Quality Notes
[Mention any conflicts or gaps in the research data]
{f"Note: Found {len(conflicts)} data conflicts that may need verification." if conflicts else "Data quality: High - no significant conflicts detected."}

Be factual, analytical, and cite specific data points from the research.
Make it SPECIFIC to {target}, not generic. Use actual details from the research."""

        response = llm.invoke(plan_prompt)
        plan_content = response.content.strip() if response.content else ""

        # Ensure we never set empty content (prevents infinite loop)
        if not plan_content:
            plan_content = "No plan generated - empty response from LLM"
            state['progress_messages'].append("⚠️ Plan generation returned empty response")
        else:
            state['progress_messages'].append("✅ Account plan generated!")

        # Store the plan
        state['account_plan'] = {
            "content": plan_content,
            "generated_at": state.get('updated_at', ''),
            "target_company": target,
            "sections": {
                "overview": True,
                "leadership": True,
                "financial": True,
                "swot": True,
                "opportunities": True,
                "risks": True,
                "news": True,
                "recommendations": True
            }
        }
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Plan generation failed: {str(e)}")
        # Set error dict instead of None to prevent infinite loop
        state['account_plan'] = {"error": f"Plan generation failed: {str(e)}", "content": ""}

    return state


def generic_plan_generator_node(state: ResearchState) -> ResearchState:
    """
    Generate a GENERIC (non-personalized) plan for comparison
    This shows the difference between personalized and generic
    """
    state['progress_messages'].append("📝 Generating generic comparison plan...")
    
    try:
        target = state.get('target_company_name', '')
        synthesized = state.get('synthesized_data', '')
        
        generic_prompt = f"""Create a GENERIC account plan for {target}.

# RESEARCH SYNTHESIS:
{synthesized}

Create a standard, generic account plan:

## Company Overview
[Basic info about the company]

## Business Analysis
[What they do, their market]

## Potential Opportunities
[Generic opportunities anyone could see]

## Approach Strategy
[Generic outreach steps]

Keep it professional but GENERIC - this is what a typical rep would create without personalization."""

        response = llm.invoke(generic_prompt)
        plan_content = response.content.strip() if response.content else ""

        # Ensure we never set empty content (prevents infinite loop)
        if not plan_content:
            plan_content = "No generic plan generated - empty response from LLM"
            state['progress_messages'].append("⚠️ Generic plan generation returned empty response")
        else:
            state['progress_messages'].append("✅ Generic plan generated for comparison")

        state['generic_plan'] = {
            "content": plan_content,
            "generated_at": state.get('updated_at', ''),
            "target_company": target,
            "personalized": False
        }
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Generic plan generation failed: {str(e)}")
        # Set error dict instead of None to prevent infinite loop
        state['generic_plan'] = {"error": f"Generic plan generation failed: {str(e)}", "content": ""}

    return state