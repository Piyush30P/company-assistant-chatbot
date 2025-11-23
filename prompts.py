"""
LLM Prompt Templates for Account Plan Generation
"""

def get_full_plan_prompt(company_name, raw_data, focus_areas=""):
    """Generate prompt for creating complete account plan"""

    focus_section = f"\n**User's Focus Areas:** {focus_areas}\n" if focus_areas else ""

    return f"""You are a professional business analyst creating a comprehensive account plan for {company_name}.

{focus_section}
## RAW RESEARCH DATA:

{raw_data}

---

Create a detailed, well-structured account plan using this EXACT format:

# 📋 EXECUTIVE SUMMARY
[2-3 paragraph summary of key findings and opportunities]

# 🏢 COMPANY OVERVIEW
[Detailed description of what the company does, their mission, market position]

# 💰 FINANCIAL SNAPSHOT
[Revenue, market cap, growth trends, profitability - include specific numbers]

# 👔 LEADERSHIP
[Key executives with names, titles, and backgrounds]

# 🛠️ PRODUCTS & SERVICES / TECH STACK
[Main products, services, and technologies they use]

# 📰 RECENT NEWS & EVENTS
[Latest developments, launches, acquisitions, partnerships]

# 📊 SWOT ANALYSIS
**Strengths:**
- [List 3-4 key strengths]

**Weaknesses:**
- [List 2-3 weaknesses]

**Opportunities:**
- [List 3-4 opportunities]

**Threats:**
- [List 2-3 threats]

# 🎯 OPPORTUNITIES FOR ENGAGEMENT
[How companies/investors/partners could work with them]

# ⚠️ RISKS / OBJECTIONS
[Potential concerns or challenges when engaging with this company]

# 🚀 NEXT STEPS
[Concrete action items for following up]

# 📚 SOURCES & EVIDENCE
[List key data sources and links]

Be specific, factual, and cite numbers wherever possible. If data is missing, clearly state "Data not available"."""


def get_section_edit_prompt(company_name, section_name, section_content, new_instructions, raw_data):
    """Generate prompt for editing a specific section"""

    return f"""You are editing the "{section_name}" section of an account plan for {company_name}.

## CURRENT SECTION CONTENT:
{section_content}

## USER'S EDITING INSTRUCTIONS:
{new_instructions}

## AVAILABLE RESEARCH DATA:
{raw_data}

---

Rewrite ONLY the "{section_name}" section following the user's instructions.
Maintain the same format and structure.
Use the research data to ensure accuracy.
Return ONLY the updated section content, no additional commentary."""


def get_conflict_detection_prompt(data_points):
    """Generate prompt for detecting conflicts in research data"""

    return f"""You are analyzing research data for conflicts and inconsistencies.

## DATA TO ANALYZE:
{data_points}

---

Identify any conflicting information (e.g., different revenue numbers from different sources).

For each conflict, return in this format:
- **Conflict:** [Brief description]
- **Source 1:** [Data from source 1]
- **Source 2:** [Data from source 2]
- **Recommendation:** [Which to trust and why]

If no conflicts found, return: "No significant conflicts detected."
"""


def get_synthesis_prompt(company_name, web_data, financial_data, news_data):
    """Generate prompt for synthesizing research into structured data"""

    return f"""Synthesize the following research about {company_name} into a structured summary.

## WEB RESEARCH:
{web_data}

## FINANCIAL DATA:
{financial_data}

## NEWS & RECENT DEVELOPMENTS:
{news_data}

---

Create a well-organized synthesis covering:
1. Company basics (founded, headquarters, industry)
2. Key financials (revenue, market cap, employees)
3. Leadership team
4. Main products/services
5. Recent news highlights
6. Strategic focus areas

Format as clear bullet points. Be factual and cite specific numbers."""
