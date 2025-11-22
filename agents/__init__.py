"""
Agent modules for the research assistant
"""
from .research import (
    research_user_company,
    web_search_node,
    financial_node,
    wikipedia_node,
    news_node
)

__all__ = [
    'research_user_company',
    'web_search_node',
    'financial_node',
    'wikipedia_node',
    'news_node'
]