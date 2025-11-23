# Alpha Vantage Setup Guide

**Alpha Vantage** provides reliable financial data with a generous free tier (500 requests/day).

---

## 🎯 Why Alpha Vantage?

### **Benefits over Yahoo Finance:**
- ✅ **500 requests/day** free tier (vs Yahoo's aggressive rate limiting)
- ✅ **No 429 errors** - stable and reliable
- ✅ **Official API** with proper documentation
- ✅ **Better data quality** - enterprise-grade financial data
- ✅ **Easy to use** - simple REST API

### **Free Tier Limits:**
- 500 API calls per day
- 5 API calls per minute
- Perfect for demos and small projects

---

## 🔑 Get Your Free API Key

### **Step 1: Sign Up**

1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Click "GET FREE API KEY"
4. Check your email for the API key

**No credit card required!** 💳❌

---

## ⚙️ Setup Instructions

### **Step 2: Install Dependencies**

```bash
pip install alpha-vantage
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

---

### **Step 3: Add API Key to .env**

Open (or create) your `.env` file and add:

```bash
# Alpha Vantage API Key (Optional - for financial data)
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
```

Replace `your_actual_api_key_here` with your real API key from the email.

**Example `.env` file:**
```bash
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
TAVILY_API_KEY=tvly-XXXXXXXXXXXXXXXXXXXXXXXX
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678
```

---

## 🧪 Test It Works

Run this quick test:

```bash
python -c "
import os
from dotenv import load_dotenv
from alpha_vantage.fundamentaldata import FundamentalData

load_dotenv()
key = os.getenv('ALPHA_VANTAGE_API_KEY')

if key:
    fd = FundamentalData(key=key, output_format='json')
    data, _ = fd.get_company_overview(symbol='MSFT')
    print(f'✅ Alpha Vantage works! Company: {data.get(\"Name\")}')
else:
    print('❌ API key not found in .env file')
"
```

**Expected output:**
```
✅ Alpha Vantage works! Company: Microsoft Corporation
```

---

## 🔄 How It Works in the App

The financial data agent now uses a **smart fallback system**:

```
1. Try Alpha Vantage first (if API key is set)
   ├─ Success? → Use Alpha Vantage data ✅
   └─ Failed? → Try Yahoo Finance

2. Try Yahoo Finance (fallback)
   ├─ Success? → Use Yahoo Finance data ⚠️
   └─ Failed? → Skip financial data, continue workflow
```

**No financial data?** The workflow continues with:
- Web search results
- Wikipedia overview
- Recent news

---

## 📊 Data You Get

Alpha Vantage provides:

- **Revenue** (TTM - Trailing Twelve Months)
- **Market Capitalization**
- **P/E Ratio** (Price-to-Earnings)
- **Employee Count**
- **Sector** (e.g., Technology, Healthcare)
- **Industry** (e.g., Software, Pharmaceuticals)
- **Website**
- **Company Description**
- **And more...**

---

## ⚠️ Rate Limits

### **Free Tier:**
- **500 calls/day** total
- **5 calls/minute** max

### **If You Hit the Limit:**
The app automatically:
1. Shows a warning message
2. Falls back to Yahoo Finance
3. If that fails too, continues without financial data

**No crashes! No errors!** 🎉

---

## 🆚 Alpha Vantage vs Yahoo Finance

| Feature | Alpha Vantage | Yahoo Finance |
|---------|--------------|---------------|
| **Rate Limit** | 500/day, 5/min | Very aggressive (varies) |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Data Quality** | Enterprise-grade | Good |
| **API Type** | Official REST API | Unofficial scraping |
| **Free Tier** | ✅ 500 requests/day | ✅ Unlimited (but rate-limited) |
| **Setup** | Requires API key | No setup |
| **Best For** | Production, demos | Quick tests, backup |

---

## 🚀 Running the App

After setup:

```bash
streamlit run app.py
```

1. Complete Phase 1 (your company info)
2. Research a target company (e.g., "Microsoft")
3. Watch it fetch financial data from Alpha Vantage!

You'll see:
```
💰 Fetching financial data...
✅ Financial data retrieved (Alpha Vantage)
```

---

## 🐛 Troubleshooting

### **Error: "Invalid API key"**
- Check your `.env` file has the correct key
- Make sure no extra spaces or quotes
- Verify the key in your email

### **Error: "Rate limit exceeded"**
- You've used 500 requests today
- Wait until tomorrow (resets at midnight UTC)
- Or the app will use Yahoo Finance as fallback

### **Error: "Module not found: alpha_vantage"**
```bash
pip install alpha-vantage
```

### **No financial data showing**
- Check your `.env` file exists
- Verify `ALPHA_VANTAGE_API_KEY` is set
- Try the test script above

---

## 📚 Additional Resources

- **Alpha Vantage Documentation:** https://www.alphavantage.co/documentation/
- **Python Library Docs:** https://github.com/RomelTorres/alpha_vantage
- **Get API Key:** https://www.alphavantage.co/support/#api-key

---

## ✅ Summary

1. Sign up at https://www.alphavantage.co/support/#api-key
2. Get your free API key (500 requests/day)
3. Add to `.env` file: `ALPHA_VANTAGE_API_KEY=your_key`
4. Run: `pip install alpha-vantage`
5. Test: `streamlit run app.py`

**That's it! No more 429 errors!** 🎉
