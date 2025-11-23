"""
Quick test to verify Alpha Vantage API is working
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_alpha_vantage():
    """Test if Alpha Vantage API key is set and working"""

    # Check if API key is set
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not api_key or api_key == 'your_alpha_vantage_api_key_here':
        print("❌ ALPHA_VANTAGE_API_KEY not set or still using default value")
        print("   Get your free key at: https://www.alphavantage.co/support/#api-key")
        return False

    print(f"✅ Alpha Vantage API key found: {api_key[:8]}...")

    # Test the API
    try:
        from alpha_vantage.fundamentaldata import FundamentalData

        fd = FundamentalData(key=api_key, output_format='json')
        data, _ = fd.get_company_overview(symbol='MSFT')

        if data and 'Symbol' in data:
            print(f"✅ Alpha Vantage API is working!")
            print(f"   Test company: {data.get('Name', 'N/A')}")
            print(f"   Sector: {data.get('Sector', 'N/A')}")
            print(f"   Market Cap: ${int(data.get('MarketCapitalization', 0)):,}")
            return True
        else:
            print("❌ Alpha Vantage returned empty data")
            return False

    except Exception as e:
        print(f"❌ Alpha Vantage API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Alpha Vantage API...\n")
    success = test_alpha_vantage()

    if success:
        print("\n🎉 All good! Alpha Vantage is working.")
        print("   You can now run: streamlit run app.py")
    else:
        print("\n⚠️ Alpha Vantage not working, but the app will still work with basic data.")
        print("   You can still run: streamlit run app.py")
