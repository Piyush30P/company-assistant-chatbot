# 🔍 Company Research Assistant

AI-powered research assistant that creates **personalized account plans** for sales professionals.

**Unique Two-Phase Approach:**
1. **Phase 1**: Learn about YOU (your company, value prop, differentiators)
2. **Phase 2**: Research target companies and create **personalized** plans

---

## 🌟 Key Features

### Phase 1 Features ✅ (Implemented)
- 📋 **User Onboarding** - Collect salesperson context
- 🔍 **User Company Research** - Research YOUR company first
- ✅ **Verification** - User validates research accuracy
- 🤔 **Smart Questions** - Context-gathering follow-ups

### Phase 2 Features 🚧 (Coming Next)
- 🔍 **Multi-Source Research** - Web, Financial, Wikipedia, News
- ⚠️ **Conflict Detection** - Identify contradicting information
- 📝 **Personalized Plans** - Uses YOUR context, not generic
- 📊 **Source Attribution** - Every fact cited with confidence
- 📤 **Export** - PDF, JSON formats

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key (free)

### Installation

1. **Clone/Download this directory**
```bash
cd company-research-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Get Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

5. **Create .env file**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your key:
GEMINI_API_KEY=your_actual_key_here
```

6. **Test your setup**
```bash
python test_agents.py
```

You should see:
```
✅ All tests passed! You're ready to build!
```

7. **Run the app**
```bash
streamlit run app.py
```

Your browser will open to `http://localhost:8501`

---

## 📁 Project Structure

```
company-research-assistant/
├── .env                    # Your API keys (create this!)
├── .env.example            # Template for .env
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── app.py                 # Main Streamlit app ⭐
├── workflow.py            # LangGraph workflow (Phase 2)
├── test_agents.py         # Test your setup
│
├── agents/
│   ├── __init__.py
│   ├── research.py        # Research agents ⭐
│   ├── supervisor.py      # Routing logic (Phase 2)
│   └── synthesis.py       # Plan generation (Phase 2)
│
├── utils/
│   ├── __init__.py
│   └── state.py          # State definitions ⭐
│
└── data/
    ├── cache/            # Cached results (auto-created)
    └── plans/            # Generated plans (auto-created)
```

Files marked with ⭐ are the core files you'll work with.

---

## 🎯 Usage Guide

### Phase 1: Onboarding (Implemented)

1. **Start the app**
```bash
streamlit run app.py
```

2. **Fill in your information**
   - Your name and role
   - Your company name
   - Your product/service description
   - Research purpose

3. **Review your company research**
   - Agent researches YOUR company
   - Verify the information is correct
   - Add any corrections

4. **Answer context questions**
   - Value proposition
   - Ideal customers
   - Customer challenges
   - Differentiators

5. **You're ready for Phase 2!**

### Phase 2: Target Research (Coming Next)
- Enter target company name
- Agent researches using multiple sources
- Detects conflicts, asks for resolution
- Generates personalized account plan
- Export to PDF/JSON

---

## 🛠️ Tech Stack (100% Free!)

| Component | Technology | Cost |
|-----------|-----------|------|
| **LLM** | Google Gemini 2.0 Flash | FREE (1,500 RPD) |
| **Search** | DuckDuckGo | FREE (unlimited) |
| **Financial** | yfinance | FREE (unlimited) |
| **Company Info** | Wikipedia | FREE (unlimited) |
| **News** | Google News RSS | FREE (unlimited) |
| **Framework** | LangChain + LangGraph | FREE (open source) |
| **UI** | Streamlit | FREE |
| **Storage** | Local (JSON/SQLite) | FREE |

**Total Cost: $0** 💰

---

## 🧪 Testing

### Run All Tests
```bash
python test_agents.py
```

### Test Individual Components

**Test Gemini:**
```python
python -c "from agents.research import llm; print(llm.invoke('Hello!').content)"
```

**Test Web Search:**
```python
python -c "from agents.research import search_web_duckduckgo; print(search_web_duckduckgo('Microsoft', 3))"
```

**Test Wikipedia:**
```python
python -c "from agents.research import get_wikipedia_summary; print(get_wikipedia_summary('Microsoft'))"
```

**Test User Company Research:**
```python
python -c "from agents.research import research_user_company; print(research_user_company('Microsoft'))"
```

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not found"
**Solution:** 
1. Check `.env` file exists in project root
2. Verify format: `GEMINI_API_KEY=your_key_here` (no spaces, no quotes)
3. Restart the app after editing .env

### Error: "Rate limit exceeded"
**Solution:** 
- Gemini free tier: 1,500 requests/day
- Wait 1 minute between requests
- Use caching (implemented in Phase 2)

### Error: "DuckDuckGo search failed"
**Solution:**
- Check internet connection
- DuckDuckGo might be temporarily down
- Add delay between searches: `time.sleep(2)`

### Error: "Wikipedia lookup failed"
**Solution:**
- Try exact company name
- Check internet connection
- Try different search terms

### Error: "Module not found"
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📚 Development Guide

### Adding New Research Agents

1. Add function to `agents/research.py`:
```python
def new_agent_node(state: ResearchState) -> ResearchState:
    state['progress_messages'].append("🔍 Running new agent...")
    # Your logic here
    state['progress_messages'].append("✅ Complete!")
    return state
```

2. Update `workflow.py` to include new agent

3. Test with `test_agents.py`

### Modifying the UI

Edit `app.py` - all UI code is there using Streamlit.

Common modifications:
- Change form fields: Search for `st.text_input` or `st.text_area`
- Add new pages: Use `st.session_state.phase`
- Style changes: Modify CSS in `st.markdown()`

---

## 🎬 Demo Preparation

### Test Scenarios

**Scenario 1: Confused User**
- Fill form incompletely
- Verify error messages show

**Scenario 2: Normal Flow**
- Complete full Phase 1
- Verify research shows correctly
- Verify follow-up questions save

**Scenario 3: Different Companies**
- Test with Microsoft
- Test with Tesla
- Test with Apple

### Demo Companies
Use these for your demo (well-known, good data):
- Microsoft (MSFT)
- Tesla (TSLA)
- Apple (AAPL)
- Salesforce (CRM)

---

## 📊 Current Status

### ✅ Completed (Phase 1)
- [x] Project structure
- [x] User onboarding form
- [x] User company research agent
- [x] Verification step
- [x] Follow-up questions
- [x] Context storage
- [x] Streamlit UI for Phase 1
- [x] Testing framework

### 🚧 In Progress (Phase 2)
- [ ] Target company research workflow
- [ ] Conflict detection agent
- [ ] Personalized plan generator
- [ ] Source attribution
- [ ] Export functionality

### 📅 Timeline
- **Day 1 (Today)**: Phase 1 complete ✅
- **Day 2 (Tomorrow)**: Phase 2 implementation

---

## 💡 Tips & Best Practices

### For Development
1. **Test frequently**: Run `test_agents.py` after changes
2. **Use print statements**: Debug with `print()` liberally
3. **Check progress**: `state['progress_messages']` shows flow
4. **Save often**: Use git or manual backups

### For Demo
1. **Prepare profiles**: 2-3 demo user profiles ready
2. **Test companies**: Microsoft, Tesla work best
3. **Show comparison**: Generic vs Personalized side-by-side
4. **Explain decisions**: Why two-phase? Why personalized?

---

## 🤝 Contributing

This is a personal project for the Eightfold.ai assignment.

---

## 📝 License

MIT License - feel free to use for learning!

---

## 🙏 Acknowledgments

- Google Gemini for free LLM API
- LangChain team for amazing framework
- DuckDuckGo for free search
- Streamlit for easy UI

---

## 📧 Contact

**Name:** Jarvis
**Institution:** Vishwakarma Institute of Technology (VIT) Pune
**Program:** B.Tech Information Technology

---

## 🎯 Next Steps

1. ✅ Complete Phase 1 (Done!)
2. ⏳ Implement Phase 2 target research
3. ⏳ Add conflict detection
4. ⏳ Create personalized plan generator
5. ⏳ Add export functionality
6. ⏳ Test with different personas
7. ⏳ Record demo video
8. ⏳ Submit before deadline

**You're on track! Keep going! 🚀**