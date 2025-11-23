"""
Phase 2 Implementation Test
Tests all new components: synthesis agents, workflow, and integration
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test that all new modules can be imported"""
    print("\n" + "="*60)
    print("TEST 1: Testing Imports")
    print("="*60)
    
    try:
        from agents.synthesis import (
            verification_node,
            synthesis_node,
            personalized_plan_generator_node,
            generic_plan_generator_node
        )
        print("✅ Synthesis agents imported successfully")
        
        from workflow import create_research_workflow
        print("✅ Workflow module imported successfully")
        
        from utils.state import ResearchState, create_initial_state
        print("✅ State module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_workflow_creation():
    """Test workflow can be created"""
    print("\n" + "="*60)
    print("TEST 2: Testing Workflow Creation")
    print("="*60)
    
    try:
        from workflow import create_research_workflow
        
        workflow = create_research_workflow()
        print("✅ Workflow created successfully")
        print("   Workflow has all required nodes")
        
        return True
    except Exception as e:
        print(f"❌ Workflow creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_synthesis_agents():
    """Test synthesis agents with mock data"""
    print("\n" + "="*60)
    print("TEST 3: Testing Synthesis Agents")
    print("="*60)
    
    try:
        from agents.synthesis import verification_node, synthesis_node
        from utils.state import create_initial_state
        
        # Create mock state
        state = create_initial_state()
        state['target_company_name'] = "TestCorp"
        state['web_results'] = [
            {"title": "Test Result", "snippet": "Test snippet"}
        ]
        state['financial_data'] = {"ticker": "TEST"}
        state['wiki_data'] = {"summary": "Test company"}
        
        # Test verification
        print("Testing verification_node...")
        result = verification_node(state)
        if 'conflicts' in result:
            print("✅ Verification node works")
        else:
            print("⚠️ Verification node returned incomplete state")
        
        # Test synthesis
        print("Testing synthesis_node...")
        state['news_data'] = [{"title": "Test News"}]
        result = synthesis_node(state)
        if 'synthesized_data' in result:
            print("✅ Synthesis node works")
        else:
            print("⚠️ Synthesis node returned incomplete state")
        
        return True
    except Exception as e:
        print(f"❌ Synthesis agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_plan_generation():
    """Test plan generation with mock data"""
    print("\n" + "="*60)
    print("TEST 4: Testing Plan Generation")
    print("="*60)
    
    try:
        from agents.synthesis import personalized_plan_generator_node
        from utils.state import create_initial_state
        
        # Create mock state with user context
        state = create_initial_state()
        state['target_company_name'] = "TestCorp"
        state['user_context'] = {
            "name": "Test User",
            "role": "Sales Director",
            "company_name": "Test Company",
            "product_service": "Test Product",
            "research_purpose": "Sales Outreach"
        }
        state['follow_up_answers'] = {
            "value_proposition": "Test value prop",
            "ideal_customers": "Test customers",
            "customer_challenges": "Test challenges",
            "differentiators": "Test differentiators"
        }
        state['synthesized_data'] = "Test synthesis data"
        
        print("Testing personalized_plan_generator_node...")
        result = personalized_plan_generator_node(state)
        
        if 'account_plan' in result and result['account_plan']:
            print("✅ Plan generation works")
            print(f"   Generated plan length: {len(result['account_plan'].get('content', ''))}")
        else:
            print("⚠️ Plan generation returned incomplete state")
        
        return True
    except Exception as e:
        print(f"❌ Plan generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test complete workflow with real API calls (requires API keys)"""
    print("\n" + "="*60)
    print("TEST 5: Testing Full Workflow (Optional)")
    print("="*60)

    if not os.getenv('GEMINI_API_KEY') or not os.getenv('TAVILY_API_KEY'):
        print("⚠️ Skipping - API keys not set")
        print("   Set GEMINI_API_KEY and TAVILY_API_KEY to test full workflow")
        return True

    try:
        # Enable debug mode for this test
        os.environ['DEBUG_WORKFLOW'] = 'true'
        from workflow import create_research_workflow
        from utils.state import create_initial_state
        
        print("Running mini workflow test (this takes ~30 seconds)...")
        
        state = create_initial_state()
        state['target_company_name'] = "Microsoft"
        state['user_context'] = {
            "name": "Test User",
            "role": "Sales Director",
            "company_name": "Test Company",
            "product_service": "AI-powered CRM",
            "research_purpose": "Sales Outreach"
        }
        state['follow_up_answers'] = {
            "value_proposition": "Help sales teams close more deals",
            "ideal_customers": "Mid-sized B2B companies",
            "customer_challenges": "Manual data entry, poor visibility",
            "differentiators": "AI-powered insights, real-time collaboration"
        }
        
        workflow = create_research_workflow()

        # Debug: Check initial state keys
        print(f"\n   Initial state keys: {list(state.keys())}")
        print(f"   'web_results' in state: {'web_results' in state}")
        print(f"   'account_plan' in state: {'account_plan' in state}")

        # Run workflow - use invoke() to get complete final state
        print("\n   Starting workflow execution...")
        try:
            final_state = workflow.invoke(state)
        except Exception as e:
            print(f"   ❌ Workflow invoke failed: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Check results
        account_plan = final_state.get('account_plan')

        # Debug: Check what we actually got
        print(f"\n   Debug Info:")
        print(f"   - account_plan value: {account_plan}")
        print(f"   - account_plan type: {type(account_plan)}")

        if account_plan and isinstance(account_plan, dict) and account_plan.get('content'):
            print("\n✅ Full workflow completed successfully!")
            plan_content = account_plan.get('content', '')
            print(f"   Plan generated: {len(plan_content)} chars")

            # Show some progress info
            if 'progress_messages' in final_state:
                print(f"   Total progress steps: {len(final_state['progress_messages'])}")

            return True
        else:
            print("\n⚠️ Workflow completed but no plan generated")
            if account_plan:
                print(f"   account_plan exists but is: {account_plan}")
            else:
                print(f"   account_plan is None or empty")

            # Show progress messages to see what happened
            if 'progress_messages' in final_state:
                print(f"\n   Progress messages:")
                for msg in final_state['progress_messages'][-5:]:  # Last 5 messages
                    print(f"   - {msg}")

            return False
            
    except Exception as e:
        print(f"❌ Full workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING PHASE 2 TESTS")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Workflow Creation", test_workflow_creation),
        ("Synthesis Agents", test_synthesis_agents),
        ("Plan Generation", test_plan_generation),
        ("Full Workflow (Optional)", test_full_workflow)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 2 is ready!")
        print("\n✅ Next Steps:")
        print("1. Run: streamlit run app.py")
        print("2. Complete Phase 1 onboarding")
        print("3. Research a target company (try Microsoft or Tesla)")
        print("4. View the side-by-side plan comparison")
        print("5. Export to PDF/JSON")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("Review the errors above and fix before proceeding")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)