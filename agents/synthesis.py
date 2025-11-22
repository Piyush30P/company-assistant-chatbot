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
    state['progress_messages'].append("🧠 Synthesizing information...")
    
    try:
        # Extract all research data
        company = state.get('target_company_name', 'Unknown')
        web_results = state.get('web_results', [])
        financial_data = state.get('financial_data', {})
        wiki_data = state.get('wiki_data', {})
        news_data = state.get('news_data', [])
        
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
        state['synthesized_data'] = response.content
        
        state['progress_messages'].append("✅ Research synthesized successfully")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Synthesis failed: {str(e)}")
        state['synthesized_data'] = None
    
    return state


def personalized_plan_generator_node(state: ResearchState) -> ResearchState:
    """
    Plan generator - creates personalized account plan
    This is the KEY feature that uses user context from Phase 1
    """
    state['progress_messages'].append("📝 Generating personalized account plan...")
    
    try:
        # Extract user context
        user_ctx = state.get('user_context', {})
        follow_up = state.get('follow_up_answers', {})
        target = state.get('target_company_name', '')
        synthesized = state.get('synthesized_data', '')
        
        # Build personalized prompt
        plan_prompt = f"""You are a strategic sales consultant creating a PERSONALIZED account plan.

# YOUR COMPANY CONTEXT (The Salesperson):
Company: {user_ctx.get('company_name', 'N/A')}
Role: {user_ctx.get('role', 'N/A')}
Product/Service: {user_ctx.get('product_service', 'N/A')}
Research Purpose: {user_ctx.get('research_purpose', 'N/A')}

Value Proposition: {follow_up.get('value_proposition', 'N/A')}
Ideal Customers: {follow_up.get('ideal_customers', 'N/A')}
Customer Challenges: {follow_up.get('customer_challenges', 'N/A')}
Differentiators: {follow_up.get('differentiators', 'N/A')}

# TARGET COMPANY:
{target}

# RESEARCH SYNTHESIS:
{synthesized}

---

Create a PERSONALIZED account plan that shows HOW your product/service specifically addresses this target company's needs.

Use this structure:

## 🎯 Executive Summary
[2-3 sentences on why {user_ctx.get('company_name', 'your company')} is a fit for {target}]

## 🔍 Target Company Profile
- Company: {target}
- Industry & Size: [from research]
- Key Business Focus: [from research]
- Recent Developments: [from research]

## 💡 Opportunity Analysis
[WHY is this a good fit? Connect YOUR value prop to THEIR needs]
- Business Need #1: [specific to {target}] → Your Solution: [how you solve it]
- Business Need #2: [specific to {target}] → Your Solution: [how you solve it]
- Business Need #3: [specific to {target}] → Your Solution: [how you solve it]

## 🎁 Value Proposition
[Customized pitch using YOUR differentiators for THIS specific company]

## 👥 Key Stakeholders
[Who to contact at {target} based on your research]
- Title 1: [Why they care]
- Title 2: [Why they care]
- Title 3: [Why they care]

## 📞 Recommended Approach
[Specific outreach strategy]
1. [First step]
2. [Second step]
3. [Third step]

## ⚠️ Potential Objections & Responses
[Anticipate objections specific to {target}]
- Objection 1: [Response]
- Objection 2: [Response]

## 📊 Success Metrics
[How to measure this opportunity]

## 🚀 Next Steps
[Concrete action items with timeline]

Make it SPECIFIC to {target}, not generic. Use actual details from the research."""

        response = llm.invoke(plan_prompt)
        
        # Store the plan
        state['account_plan'] = {
            "content": response.content,
            "generated_at": state.get('updated_at', ''),
            "target_company": target,
            "user_company": user_ctx.get('company_name', 'N/A'),
            "personalized": True
        }
        
        state['progress_messages'].append("✅ Personalized plan generated!")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Plan generation failed: {str(e)}")
        state['account_plan'] = None
    
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
        
        state['generic_plan'] = {
            "content": response.content,
            "generated_at": state.get('updated_at', ''),
            "target_company": target,
            "personalized": False
        }
        
        state['progress_messages'].append("✅ Generic plan generated for comparison")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Generic plan generation failed: {str(e)}")
        state['generic_plan'] = None
    
    return state