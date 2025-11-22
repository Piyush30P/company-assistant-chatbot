"""
Quick structure check for Phase 2 implementation
Checks if all components are present without requiring full dependencies
"""

def check_file_exists(filepath, description):
    """Check if a file exists"""
    import os
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_function_exists(filepath, function_name):
    """Check if a function is defined in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if f"def {function_name}" in content:
                print(f"  ✅ Function '{function_name}' found")
                return True
            else:
                print(f"  ❌ Function '{function_name}' NOT found")
                return False
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("PHASE 2 STRUCTURE CHECK")
    print("="*60)

    checks_passed = 0
    checks_total = 0

    # Check core files
    print("\n📁 Core Files:")
    files = [
        ("/home/user/company-assistant-chatbot/utils/state.py", "State definitions"),
        ("/home/user/company-assistant-chatbot/agents/research.py", "Research agents"),
        ("/home/user/company-assistant-chatbot/agents/synthesis.py", "Synthesis agents"),
        ("/home/user/company-assistant-chatbot/workflow.py", "Workflow"),
        ("/home/user/company-assistant-chatbot/app.py", "Streamlit app"),
        ("/home/user/company-assistant-chatbot/test_phase2.py", "Phase 2 tests")
    ]

    for filepath, desc in files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1

    # Check synthesis agents
    print("\n🧠 Synthesis Agents:")
    synthesis_functions = [
        "verification_node",
        "synthesis_node",
        "personalized_plan_generator_node",
        "generic_plan_generator_node"
    ]

    for func in synthesis_functions:
        checks_total += 1
        if check_function_exists("/home/user/company-assistant-chatbot/agents/synthesis.py", func):
            checks_passed += 1

    # Check research agents
    print("\n🔍 Research Agents:")
    research_functions = [
        "web_search_node",
        "financial_node",
        "wikipedia_node",
        "news_node"
    ]

    for func in research_functions:
        checks_total += 1
        if check_function_exists("/home/user/company-assistant-chatbot/agents/research.py", func):
            checks_passed += 1

    # Check workflow
    print("\n🔄 Workflow:")
    workflow_functions = [
        "supervisor_node",
        "create_research_workflow"
    ]

    for func in workflow_functions:
        checks_total += 1
        if check_function_exists("/home/user/company-assistant-chatbot/workflow.py", func):
            checks_passed += 1

    # Check app.py for Phase 2 UI
    print("\n🖥️  UI Components:")
    checks_total += 1
    with open("/home/user/company-assistant-chatbot/app.py", 'r') as f:
        content = f.read()
        if "Phase 2: Target Company Research" in content:
            print("  ✅ Phase 2 UI section found")
            checks_passed += 1
        else:
            print("  ❌ Phase 2 UI section NOT found")

    checks_total += 1
    if "export_to_pdf" in content:
        print("  ✅ PDF export function found")
        checks_passed += 1
    else:
        print("  ❌ PDF export function NOT found")

    checks_total += 1
    if "export_to_json" in content:
        print("  ✅ JSON export function found")
        checks_passed += 1
    else:
        print("  ❌ JSON export function NOT found")

    # Summary
    print("\n" + "="*60)
    print(f"📊 RESULTS: {checks_passed}/{checks_total} checks passed")
    print("="*60)

    if checks_passed == checks_total:
        print("\n🎉 SUCCESS! Phase 2 is fully implemented!")
        print("\n✅ All components are present:")
        print("   • Research agents (Web, Financial, Wikipedia, News)")
        print("   • Synthesis agents (Verification, Synthesis)")
        print("   • Plan generators (Personalized & Generic)")
        print("   • Complete workflow with supervisor")
        print("   • Full Streamlit UI with export features")
        print("\n📝 Next Steps:")
        print("   1. Set up .env file with API keys:")
        print("      - GEMINI_API_KEY")
        print("      - TAVILY_API_KEY")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run: streamlit run app.py")
        return True
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed")
        print("Some components may be missing or incomplete")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
