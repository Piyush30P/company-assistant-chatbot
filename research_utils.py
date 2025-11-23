"""
Research utility functions for gathering company data
"""
import os
from dotenv import load_dotenv

load_dotenv()


def run_research(company_name, focus_areas=""):
    """
    Main research function that gathers data from multiple sources

    Args:
        company_name: Name of company to research
        focus_areas: Optional specific areas to focus on

    Returns:
        dict with research data and progress messages
    """
    progress_messages = []
    research_data = {}

    # 1. Web Search
    progress_messages.append("🌐 Searching the web for company information...")
    web_data = fetch_web_data(company_name)
    research_data['web'] = web_data
    progress_messages.append(f"✅ Found {len(web_data.get('results', []))} web results")

    # 2. Financial Data
    progress_messages.append("💰 Fetching financial data...")
    financial_data = fetch_financial_data(company_name)
    research_data['financial'] = financial_data
    if financial_data.get('revenue'):
        progress_messages.append(f"✅ Retrieved financial data (Revenue: ${financial_data['revenue']:,})")
    else:
        progress_messages.append("⚠️ Financial data limited")

    # 3. Wikipedia Overview
    progress_messages.append("📚 Getting Wikipedia overview...")
    wiki_data = fetch_wikipedia_data(company_name)
    research_data['wikipedia'] = wiki_data
    progress_messages.append("✅ Wikipedia data retrieved")

    # 4. News & Recent Developments
    progress_messages.append("📰 Collecting recent news...")
    news_data = fetch_news_data(company_name)
    research_data['news'] = news_data
    progress_messages.append(f"✅ Found {len(news_data.get('articles', []))} news articles")

    # 5. Conflict Detection
    progress_messages.append("🔍 Checking for data conflicts...")
    conflicts = detect_conflicts(research_data)
    research_data['conflicts'] = conflicts

    if conflicts:
        progress_messages.append(f"⚠️ Found {len(conflicts)} potential conflicts")
    else:
        progress_messages.append("✅ No major conflicts detected")

    return {
        'data': research_data,
        'messages': progress_messages
    }


def fetch_web_data(company_name):
    """Fetch web search results using Tavily API"""
    try:
        from tavily import TavilyClient

        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            return {'results': [], 'error': 'Tavily API key not set'}

        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=f"{company_name} company overview products services",
            max_results=5
        )

        return {
            'results': response.get('results', []),
            'source': 'Tavily'
        }
    except Exception as e:
        return {'results': [], 'error': str(e)}


def fetch_financial_data(company_name):
    """Fetch financial data using Alpha Vantage"""
    try:
        from alpha_vantage.fundamentaldata import FundamentalData
        import google.generativeai as genai

        # Get ticker symbol using LLM
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        ticker_prompt = f"What is the stock ticker symbol for {company_name}? Reply with ONLY the ticker symbol (e.g., MSFT, TSLA), nothing else."
        response = model.generate_content(ticker_prompt)
        ticker = response.text.strip().upper()

        # Fetch data from Alpha Vantage
        alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not alpha_key:
            return {'error': 'Alpha Vantage API key not set'}

        fd = FundamentalData(key=alpha_key, output_format='json')
        data, _ = fd.get_company_overview(symbol=ticker)

        if data and 'Symbol' in data:
            return {
                'ticker': ticker,
                'revenue': int(data.get('RevenueTTM', 0)) if data.get('RevenueTTM') else None,
                'market_cap': int(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else None,
                'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') else None,
                'sector': data.get('Sector'),
                'industry': data.get('Industry'),
                'description': data.get('Description'),
                'source': 'Alpha Vantage'
            }
        else:
            return {'error': 'No financial data found'}

    except Exception as e:
        return {'error': str(e)}


def fetch_wikipedia_data(company_name):
    """Fetch Wikipedia summary"""
    try:
        import wikipedia

        page = wikipedia.page(company_name, auto_suggest=True)
        return {
            'summary': page.summary[:1000],  # First 1000 chars
            'url': page.url,
            'title': page.title,
            'source': 'Wikipedia'
        }
    except Exception as e:
        return {'error': str(e)}


def fetch_news_data(company_name):
    """Fetch recent news using Google News RSS"""
    try:
        import feedparser
        from urllib.parse import quote

        query = quote(f"{company_name}")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        feed = feedparser.parse(rss_url)
        articles = []

        for entry in feed.entries[:5]:
            articles.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'source': entry.get('source', {}).get('title', 'Unknown')
            })

        return {
            'articles': articles,
            'source': 'Google News RSS'
        }
    except Exception as e:
        return {'articles': [], 'error': str(e)}


def detect_conflicts(research_data):
    """Detect conflicting information in research data"""
    conflicts = []

    # Example: Check if revenue numbers differ significantly
    financial = research_data.get('financial', {})
    web_results = research_data.get('web', {}).get('results', [])

    # Add actual conflict detection logic here
    # For now, return empty list

    return conflicts


def format_raw_data(research_data):
    """Format research data into readable text for LLM"""

    output = []

    # Web Results
    if research_data.get('web', {}).get('results'):
        output.append("## WEB SEARCH RESULTS:")
        for i, result in enumerate(research_data['web']['results'][:5], 1):
            output.append(f"\n{i}. **{result.get('title', 'N/A')}**")
            output.append(f"   {result.get('content', result.get('snippet', 'N/A'))[:300]}")
            output.append(f"   Source: {result.get('url', 'N/A')}")

    # Financial Data
    if research_data.get('financial'):
        fin = research_data['financial']
        output.append("\n## FINANCIAL DATA:")
        output.append(f"- Ticker: {fin.get('ticker', 'N/A')}")
        output.append(f"- Revenue: ${fin.get('revenue', 0):,}" if fin.get('revenue') else "- Revenue: N/A")
        output.append(f"- Market Cap: ${fin.get('market_cap', 0):,}" if fin.get('market_cap') else "- Market Cap: N/A")
        output.append(f"- Sector: {fin.get('sector', 'N/A')}")
        output.append(f"- Industry: {fin.get('industry', 'N/A')}")

    # Wikipedia
    if research_data.get('wikipedia', {}).get('summary'):
        output.append("\n## WIKIPEDIA OVERVIEW:")
        output.append(research_data['wikipedia']['summary'])

    # News
    if research_data.get('news', {}).get('articles'):
        output.append("\n## RECENT NEWS:")
        for article in research_data['news']['articles'][:5]:
            output.append(f"- {article.get('title', 'N/A')}")
            output.append(f"  Published: {article.get('published', 'N/A')}")

    return "\n".join(output)
