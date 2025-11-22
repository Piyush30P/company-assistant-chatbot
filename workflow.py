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
    if not state.get("web_results"):
        state["next_node"] = "web_search"
    elif not state.get("financial_data"):
        state["next_node"] = "financial"
    elif not state.get("wiki_data"):
        state["next_node"] = "wikipedia"
    elif not state.get("news_data"):
        state["next_node"] = "news"
    elif not state.get("conflicts"):
        state["next_node"] = "verification"
    elif not state.get("synthesized_data"):
        state["next_node"] = "synthesis"
    elif not state.get("account_plan"):
        state["next_node"] = "personalized_plan"
    elif not state.get("generic_plan"):
        state["next_node"] = "generic_plan"
    else:
        state["next_node"] = "end"
    
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
    workflow.add_node("generic_plan", generic_plan_generator_node)
    
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
            "generic_plan": "generic_plan",
            "end": END
        }
    )
    
    # All nodes return to supervisor for routing
    for node in ["web_search", "financial", "wikipedia", "news", 
                 "verification", "synthesis", "personalized_plan", "generic_plan"]:
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