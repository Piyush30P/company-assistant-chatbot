"""
LangGraph workflow for Phase 2 (Target Company Research)
Full implementation with all agents
"""
from langgraph.graph import StateGraph, END
from utils.state import ResearchState
from agents.research import web_search_node, financial_node, wikipedia_node, news_node
from agents.synthesis import (
    verification_node, 
    synthesis_node, 
    personalized_plan_generator_node,
    generic_plan_generator_node
)


def supervisor_node(state: ResearchState) -> ResearchState:
    """
    Supervisor agent that routes to appropriate research agents
    Sequential flow: Research → Verify → Synthesize → Generate Plans
    """
    # Check what stage we're at
    # Use 'key not in state' to check if a node has RUN (not if it succeeded)
    # This prevents infinite loops when nodes fail and set fields to None

    # Debug: Print what keys exist
    import os
    debug = os.getenv('DEBUG_WORKFLOW', 'false').lower() == 'true'
    if debug:
        print(f"   [Supervisor] Checking state keys: {list(state.keys())}")
        print(f"   [Supervisor] web_results={'SET' if state.get('web_results') else 'NONE'}, financial_data={'SET' if state.get('financial_data') else 'NONE'}")
        print(f"   [Supervisor] wiki_data={'SET' if state.get('wiki_data') else 'NONE'}, news_data={'SET' if state.get('news_data') else 'NONE'}")
        print(f"   [Supervisor] conflicts={'SET' if state.get('conflicts') is not None else 'NONE'}, synthesized_data={'SET' if state.get('synthesized_data') else 'NONE'}")
        print(f"   [Supervisor] account_plan={'SET' if state.get('account_plan') else 'NONE'}, generic_plan={'SET' if state.get('generic_plan') else 'NONE'}")

    # Check if data exists AND is not None (LangGraph auto-creates keys from TypedDict schema)
    if not state.get('web_results'):
        state["next_node"] = "web_search"
    elif not state.get('financial_data'):
        state["next_node"] = "financial"
    elif not state.get('wiki_data'):
        state["next_node"] = "wikipedia"
    elif not state.get('news_data'):
        state["next_node"] = "news"
    elif 'conflicts' not in state or state.get('conflicts') is None:
        state["next_node"] = "verification"
    elif not state.get('synthesized_data'):
        state["next_node"] = "synthesis"
    elif not state.get('account_plan'):
        state["next_node"] = "personalized_plan"
    elif not state.get('generic_plan'):
        state["next_node"] = "generic_plan_gen"
    else:
        state["next_node"] = "end"

    if debug:
        print(f"   [Supervisor] Routing to: {state['next_node']}")
        print(f"   [Supervisor] ---")

    return state


def create_research_workflow():
    """
    Create the complete LangGraph workflow for Phase 2
    
    Flow:
    1. Web Search → 2. Financial → 3. Wikipedia → 4. News
    5. Verification → 6. Synthesis → 7. Personalized Plan → 8. Generic Plan
    """
    workflow = StateGraph(ResearchState)
    
    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("financial", financial_node)
    workflow.add_node("wikipedia", wikipedia_node)
    workflow.add_node("news", news_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("personalized_plan", personalized_plan_generator_node)
    workflow.add_node("generic_plan_gen", generic_plan_generator_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s["next_node"],
        {
            "web_search": "web_search",
            "financial": "financial",
            "wikipedia": "wikipedia",
            "news": "news",
            "verification": "verification",
            "synthesis": "synthesis",
            "personalized_plan": "personalized_plan",
            "generic_plan_gen": "generic_plan_gen",
            "end": END
        }
    )

    # All nodes return to supervisor for routing
    for node in ["web_search", "financial", "wikipedia", "news",
                 "verification", "synthesis", "personalized_plan", "generic_plan_gen"]:
        workflow.add_edge(node, "supervisor")
    
    return workflow.compile()


# Test the workflow
if __name__ == "__main__":
    print("Testing workflow creation...")
    
    try:
        workflow = create_research_workflow()
        print("✅ Workflow created successfully!")
        print("   Phase 2 fully implemented")
        print("\n📊 Workflow Steps:")
        print("   1. Web Search")
        print("   2. Financial Data")
        print("   3. Wikipedia")
        print("   4. News")
        print("   5. Verification")
        print("   6. Synthesis")
        print("   7. Personalized Plan")
        print("   8. Generic Plan (for comparison)")
    except Exception as e:
        print(f"❌ Workflow creation failed: {str(e)}")