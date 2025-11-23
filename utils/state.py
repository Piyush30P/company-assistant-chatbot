"""
State definitions for the two-phase research workflow
"""
from typing import TypedDict, Optional, List, Dict
from datetime import datetime


class UserContext(TypedDict, total=False):
    """Information about the salesperson/user - Phase 1"""
    name: str
    role: str
    email: Optional[str]
    company_name: str
    industry: Optional[str]
    product_service: str
    research_purpose: str  # "sales", "partnership", "investment", "competitive"


class UserCompanyResearch(TypedDict, total=False):
    """Research findings about user's own company - Phase 1"""
    overview: str
    products: List[str]
    key_metrics: Optional[Dict[str, str]]
    news: List[str]
    sources: List[Dict[str, str]]
    verified_by_user: bool
    user_corrections: Optional[str]


class FollowUpAnswers(TypedDict, total=False):
    """User's answers to context-gathering questions - Phase 1"""
    value_proposition: str
    ideal_customers: str
    customer_challenges: str
    differentiators: str


class ResearchState(TypedDict, total=False):
    """Main state for the entire two-phase workflow"""
    
    # ============ PHASE 1: USER ONBOARDING ============
    phase: str  # "onboarding", "verifying", "follow_up", "research", "complete"
    user_context: Optional[UserContext]
    user_company_research: Optional[UserCompanyResearch]
    follow_up_answers: Optional[FollowUpAnswers]
    onboarding_complete: bool
    
    # ============ PHASE 2: TARGET COMPANY RESEARCH ============
    target_company_name: str
    
    # Research Data from Multiple Sources
    web_results: Optional[List[Dict[str, any]]]
    financial_data: Optional[Dict[str, any]]
    wiki_data: Optional[Dict[str, any]]
    news_data: Optional[List[Dict[str, any]]]
    
    # Processing & Verification
    conflicts: List[Dict[str, any]]
    progress_messages: List[str]
    synthesized_data: Optional[str]
    
    # Output
    account_plan: Optional[Dict[str, any]]
    generic_plan: Optional[Dict[str, any]]  # Generic plan for comparison
    sources: List[Dict[str, any]]
    
    # Control Flow
    next_node: str
    needs_user_input: bool
    user_response: Optional[str]
    current_question: Optional[str]
    
    # Metadata
    created_at: Optional[str]
    updated_at: Optional[str]


# Helper function to create initial state
def create_initial_state(
    phase: str = "onboarding",
    user_context: Optional[UserContext] = None
) -> ResearchState:
    """Create an initial state for the workflow"""
    return ResearchState(
        phase=phase,
        user_context=user_context,
        user_company_research=None,
        follow_up_answers=None,
        onboarding_complete=False,
        target_company_name="",
        web_results=None,
        financial_data=None,
        wiki_data=None,
        news_data=None,
        conflicts=[],
        progress_messages=[],
        synthesized_data=None,
        account_plan=None,
        generic_plan=None,
        sources=[],
        next_node="",
        needs_user_input=False,
        user_response=None,
        current_question=None,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )