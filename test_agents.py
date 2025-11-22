"""
Test script for individual agents
Run this to verify your setup is working correctly
"""
import os
from dotenv import load_dotenv
from agents.research import research_user_company, search_web_duckduckgo, get_wikipedia_summary

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if Gemini API key is set"""
    print("\n" + "="*60)
    print("TEST 1: Checking API Key")
    print("="*60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("✅ GEMINI_API_KEY found!")
        print(f"   Key starts with: {api_key[:10]}...")
        return True
    else:
        print("❌ GEMINI_API_KEY not found!")
        print("   Please set it in your .env file")
        return False


def test_gemini_llm():
    """Test Gemini LLM connection"""
    print("\n" + "="*60)
    print("TEST 2: Testing Gemini LLM")
    print("="*60)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
        response = llm.invoke("Say 'Hello, Jarvis!' in a friendly way.")
        
        print("✅ Gemini LLM working!")
        print(f"   Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Gemini LLM failed: {str(e)}")
        return False


def test_duckduckgo_search():
    """Test DuckDuckGo search"""
    print("\n" + "="*60)
    print("TEST 3: Testing DuckDuckGo Search")
    print("="*60)
    
    try:
        results = search_web_duckduckgo("Microsoft company", max_results=3)
        
        if results:
            print(f"✅ DuckDuckGo search working!")
            print(f"   Found {len(results)} results")
            print(f"   First result: {results[0].get('title', 'N/A')}")
            return True
        else:
            print("⚠️ No results returned")
            return False
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {str(e)}")
        return False


def test_wikipedia():
    """Test Wikipedia API"""
    print("\n" + "="*60)
    print("TEST 4: Testing Wikipedia")
    print("="*60)
    
    try:
        summary = get_wikipedia_summary("Microsoft", sentences=2)
        
        if summary:
            print("✅ Wikipedia working!")
            print(f"   Summary: {summary[:100]}...")
            return True
        else:
            print("⚠️ No summary returned")
            return False
    except Exception as e:
        print(f"❌ Wikipedia failed: {str(e)}")
        return False


def test_user_company_research():
    """Test full user company research"""
    print("\n" + "="*60)
    print("TEST 5: Testing User Company Research")
    print("="*60)
    
    try:
        print("Researching Microsoft (this may take 15-30 seconds)...")
        result = research_user_company("Microsoft")
        
        print("\n✅ User company research working!")
        print("\nResults:")
        print("-" * 60)
        
        if result.get('overview'):
            print(f"\n📋 Overview:\n{result['overview'][:200]}...")
        
        if result.get('products'):
            print(f"\n🎯 Products ({len(result['products'])}):")
            for product in result['products'][:3]:
                print(f"   • {product}")
        
        if result.get('key_metrics'):
            print(f"\n💰 Key Metrics:")
            for key, value in result['key_metrics'].items():
                print(f"   • {key}: {value}")
        
        if result.get('news'):
            print(f"\n📰 Recent News ({len(result['news'])}):")
            for news in result['news'][:2]:
                print(f"   • {news}")
        
        return True
    except Exception as e:
        print(f"❌ User company research failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING ALL TESTS")
    print("="*60)
    
    tests = [
        ("API Key", test_api_key),
        ("Gemini LLM", test_gemini_llm),
        ("DuckDuckGo Search", test_duckduckgo_search),
        ("Wikipedia", test_wikipedia),
        ("User Company Research", test_user_company_research)
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
        print("\n🎉 All tests passed! You're ready to build!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n✅ Next Steps:")
        print("1. Run: streamlit run app.py")
        print("2. Fill in the onboarding form")
        print("3. Test Phase 1 flow")
    else:
        print("\n🔧 Fix the failing tests first:")
        print("1. Check your .env file has GEMINI_API_KEY")
        print("2. Verify internet connection")
        print("3. Try running individual tests")