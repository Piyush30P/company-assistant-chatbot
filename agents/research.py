"""
Research agents for gathering company information
Includes: Web search, Financial data, Wikipedia, News, and User company research
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import wikipedia
import yfinance as yf
import feedparser
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.state import ResearchState, UserCompanyResearch

# Load environment variables
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv('GEMINI_API_KEY')
)


# ============================================================
# PHASE 1: USER COMPANY RESEARCH
# ============================================================

def research_user_company(company_name: str) -> UserCompanyResearch:
    """
    Research the user's own company - Phase 1
    This builds trust by showing the agent's capabilities on familiar ground
    """
    print(f"\n🔍 Researching user's company: {company_name}")
    
    research_result = UserCompanyResearch(
        overview="",
        products=[],
        key_metrics={},
        news=[],
        sources=[],
        verified_by_user=False,
        user_corrections=None
    )
    
    # 1. Get Wikipedia overview
    try:
        wiki_summary = get_wikipedia_summary(company_name)
        if wiki_summary:
            research_result['overview'] = wiki_summary
            research_result['sources'].append({
                "source": "Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}",
                "confidence": 0.85
            })
    except Exception as e:
        print(f"⚠️ Wikipedia lookup failed: {e}")
    
    # 2. Get web search results for products
    try:
        web_results = search_web_duckduckgo(f"{company_name} products services", max_results=5)
        products = extract_products_from_web(web_results, company_name)
        research_result['products'] = products
    except Exception as e:
        print(f"⚠️ Web search failed: {e}")
    
    # 3. Get financial metrics (if public company)
    try:
        financial_data = get_financial_data_basic(company_name)
        if financial_data:
            research_result['key_metrics'] = financial_data
    except Exception as e:
        print(f"⚠️ Financial data unavailable: {e}")
    
    # 4. Get recent news
    try:
        news_items = get_recent_news(company_name, max_items=3)
        research_result['news'] = [item['title'] for item in news_items]
    except Exception as e:
        print(f"⚠️ News fetch failed: {e}")
    
    return research_result


# ============================================================
# PHASE 2: TARGET COMPANY RESEARCH AGENTS
# ============================================================

def web_search_node(state: ResearchState) -> ResearchState:
    """Web search agent using DuckDuckGo"""
    company = state.get('target_company_name', '')
    
    state['progress_messages'].append(f"🔍 Searching web for {company}...")
    
    try:
        results = search_web_duckduckgo(
            f"{company} company information overview",
            max_results=10
        )
        
        web_results = []
        for r in results:
            web_results.append({
                "title": r.get('title', ''),
                "snippet": r.get('body', ''),
                "url": r.get('href', ''),
                "source": "DuckDuckGo",
                "confidence": 0.7
            })
        
        state['web_results'] = web_results
        state['progress_messages'].append(f"✅ Found {len(web_results)} web sources")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Web search failed: {str(e)}")
        state['web_results'] = []
    
    return state


def financial_node(state: ResearchState) -> ResearchState:
    """Financial data agent using yfinance"""
    company = state.get('target_company_name', '')
    
    state['progress_messages'].append(f"💰 Fetching financial data...")
    
    try:
        # First, try to get ticker symbol using Gemini
        ticker_prompt = f"What is the stock ticker symbol for {company}? Reply with ONLY the ticker symbol (e.g., MSFT, TSLA, AAPL), nothing else."
        ticker_response = llm.invoke(ticker_prompt)
        ticker_symbol = ticker_response.content.strip().upper()
        
        # Get financial data
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        financial_data = {
            "ticker": ticker_symbol,
            "revenue": info.get("totalRevenue"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "employees": info.get("fullTimeEmployees"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "description": info.get("longBusinessSummary"),
            "source": "Yahoo Finance",
            "confidence": 0.95
        }
        
        state['financial_data'] = financial_data
        state['progress_messages'].append("✅ Financial data retrieved")
        
        # Add to sources
        if 'sources' not in state:
            state['sources'] = []
        state['sources'].append({
            "title": f"{company} - Yahoo Finance",
            "url": f"https://finance.yahoo.com/quote/{ticker_symbol}",
            "confidence": 0.95
        })
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Financial data unavailable: {str(e)}")
        state['financial_data'] = None
    
    return state


def wikipedia_node(state: ResearchState) -> ResearchState:
    """Wikipedia agent for company overview"""
    company = state.get('target_company_name', '')
    
    state['progress_messages'].append(f"📚 Getting company overview from Wikipedia...")
    
    try:
        summary = get_wikipedia_summary(company)
        
        if summary:
            # Get page URL
            search_results = wikipedia.search(company)
            page = wikipedia.page(search_results[0])
            
            wiki_data = {
                "summary": summary,
                "url": page.url,
                "title": page.title,
                "source": "Wikipedia",
                "confidence": 0.85
            }
            
            state['wiki_data'] = wiki_data
            state['progress_messages'].append("✅ Company overview retrieved")
            
            # Add to sources
            if 'sources' not in state:
                state['sources'] = []
            state['sources'].append({
                "title": f"{page.title} - Wikipedia",
                "url": page.url,
                "confidence": 0.85
            })
        else:
            state['wiki_data'] = None
            state['progress_messages'].append("⚠️ Wikipedia entry not found")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ Wikipedia lookup failed: {str(e)}")
        state['wiki_data'] = None
    
    return state


def news_node(state: ResearchState) -> ResearchState:
    """News agent using Google News RSS"""
    company = state.get('target_company_name', '')
    
    state['progress_messages'].append(f"📰 Fetching recent news...")
    
    try:
        news_items = get_recent_news(company, max_items=5)
        
        news_data = []
        for item in news_items:
            news_data.append({
                "title": item['title'],
                "link": item['link'],
                "published": item['published'],
                "source": item['source'],
                "confidence": 0.75
            })
        
        state['news_data'] = news_data
        state['progress_messages'].append(f"✅ Found {len(news_data)} recent articles")
        
    except Exception as e:
        state['progress_messages'].append(f"⚠️ News fetch failed: {str(e)}")
        state['news_data'] = []
    
    return state


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def search_web_duckduckgo(query: str, max_results: int = 10) -> List[Dict]:
    """Search using DuckDuckGo (free, no API key needed)"""
    try:
        results = DDGS().text(query, max_results=max_results)
        return list(results)
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []


def get_wikipedia_summary(company_name: str, sentences: int = 5) -> Optional[str]:
    """Get Wikipedia summary for a company"""
    try:
        search_results = wikipedia.search(company_name)
        if not search_results:
            return None
        
        summary = wikipedia.summary(search_results[0], sentences=sentences)
        return summary
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return None


def get_financial_data_basic(company_name: str) -> Optional[Dict[str, str]]:
    """Get basic financial data (simplified for demo)"""
    try:
        # Try common ticker patterns
        possible_tickers = [
            company_name.upper()[:4],  # First 4 letters
            company_name.split()[0].upper()[:4]  # First word, 4 letters
        ]
        
        for ticker_symbol in possible_tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info
                
                if info.get('regularMarketPrice'):  # Valid ticker
                    return {
                        "revenue": f"${info.get('totalRevenue', 0):,.0f}" if info.get('totalRevenue') else "N/A",
                        "employees": f"{info.get('fullTimeEmployees', 0):,}" if info.get('fullTimeEmployees') else "N/A",
                        "founded": str(info.get('founded', 'N/A'))
                    }
            except:
                continue
        
        return None
    except Exception as e:
        return None


def get_recent_news(company_name: str, max_items: int = 5) -> List[Dict]:
    """Get recent news using Google News RSS"""
    try:
        feed_url = f"https://news.google.com/rss/search?q={company_name}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(feed_url)
        
        news_items = []
        for entry in feed.entries[:max_items]:
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get('published', 'N/A'),
                "source": entry.get('source', {}).get('title', 'Unknown')
            })
        
        return news_items
    except Exception as e:
        print(f"News fetch error: {e}")
        return []


def extract_products_from_web(web_results: List[Dict], company_name: str) -> List[str]:
    """Extract products/services from web search results using Gemini"""
    try:
        # Combine snippets
        snippets = "\n".join([r.get('body', '') for r in web_results[:3]])
        
        prompt = f"""Based on these search results about {company_name}, list their main products or services.

Search results:
{snippets}

List 3-5 main products/services, one per line, starting with a dash (-).
Be concise and specific."""

        response = llm.invoke(prompt)
        products = [line.strip('- ').strip() for line in response.content.split('\n') if line.strip().startswith('-')]
        
        return products[:5]  # Max 5 products
    except Exception as e:
        print(f"Product extraction error: {e}")
        return []


# ============================================================
# TEST FUNCTION
# ============================================================

if __name__ == "__main__":
    # Test user company research
    print("Testing User Company Research...")
    result = research_user_company("Microsoft")
    
    print("\n" + "="*50)
    print("RESEARCH RESULTS:")
    print("="*50)
    print(f"\nOverview:\n{result.get('overview', 'N/A')}")
    print(f"\nProducts:\n" + "\n".join([f"- {p}" for p in result.get('products', [])]))
    print(f"\nKey Metrics:\n{result.get('key_metrics', {})}")
    print(f"\nRecent News:\n" + "\n".join([f"- {n}" for n in result.get('news', [])]))  