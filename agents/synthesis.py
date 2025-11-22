"""
Synthesis and Plan Generation agents
These will be implemented in Phase 2
"""
from utils.state import ResearchState
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.7
)


def verification_node(state: ResearchState) -> ResearchState:
    """
    Verification agent - detects conflicts in research data
    Phase 2 implementation
    """
    state['progress_messages'].append("🔍 Verifying information...")
    
    # Conflict detection logic will go here
    state['conflicts'] = []
    
    state['progress_messages'].append("✅ Verification complete")
    return state


def synthesis_node(state: ResearchState) -> ResearchState:
    """
    Synthesis agent - combines all research data
    Phase 2 implementation
    """
    state['progress_messages'].append("🧠 Synthesizing information...")
    
    # Synthesis logic will go here using Gemini
    
    state['progress_messages'].append("✅ Synthesis complete")
    return state


def personalized_plan_generator_node(state: ResearchState) -> ResearchState:
    """
    Plan generator - creates personalized account plan
    This is the KEY feature that uses user context from Phase 1
    Phase 2 implementation
    """
    state['progress_messages'].append("📝 Generating personalized account plan...")
    
    # Extract user context
    user_ctx = state.get('user_context', {})
    follow_up = state.get('follow_up_answers', {})
    target = state.get('target_company_name', '')
    
    # Personalized prompt will use:
    # - user_ctx['company_name']
    # - user_ctx['product_service']
    # - follow_up['value_proposition']
    # - follow_up['differentiators']
    # + all research data about target company
    
    # Full implementation coming in Phase 2
    
    state['progress_messages'].append("✅ Plan generated!")
    return state