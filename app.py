"""
Company Research Assistant - Streamlit App
Two-Phase Approach: User Onboarding → Target Research
COMPLETE IMPLEMENTATION
"""
import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agents.research import research_user_company
from utils.state import create_initial_state
from workflow import create_research_workflow
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Load environment variables
load_dotenv()

# Verify API keys
if not os.getenv('GEMINI_API_KEY'):
    st.error("⚠️ GEMINI_API_KEY not found! Please set it in .env file")
    st.stop()
if not os.getenv('TAVILY_API_KEY'):
    st.error("⚠️ TAVILY_API_KEY not found! Please set it in .env file")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'phase' not in st.session_state:
    st.session_state.phase = 'onboarding'
if 'user_context' not in st.session_state:
    st.session_state.user_context = None
if 'user_company_research' not in st.session_state:
    st.session_state.user_company_research = None
if 'follow_up_answers' not in st.session_state:
    st.session_state.follow_up_answers = None
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = None

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def export_to_json(data, filename="account_plan.json"):
    """Export data to JSON"""
    json_str = json.dumps(data, indent=2)
    return json_str

def export_to_pdf(content, filename="account_plan.pdf"):
    """Export content to PDF"""
    from io import BytesIO
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Split content into lines and create paragraphs
    lines = content.split('\n')
    for line in lines:
        if line.strip():
            if line.startswith('##'):
                # Header
                story.append(Paragraph(line.replace('##', '').strip(), styles['Heading2']))
            elif line.startswith('#'):
                # Title
                story.append(Paragraph(line.replace('#', '').strip(), styles['Heading1']))
            else:
                # Normal text
                story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 📊 Process Flow")
    st.markdown("---")
    
    phases = {
        'onboarding': ('📋', 'Phase 1: Tell us about yourself', 'info'),
        'verifying': ('✅', 'Phase 1: Verifying your company', 'info'),
        'follow_up': ('🤔', 'Phase 1: Context gathering', 'info'),
        'research': ('🔍', 'Phase 2: Researching target', 'success'),
        'complete': ('✨', 'Complete!', 'success')
    }
    
    current_phase = st.session_state.phase
    for phase_key, (icon, label, status) in phases.items():
        if phase_key == current_phase:
            if status == 'info':
                st.info(f"{icon} **{label}**")
            else:
                st.success(f"{icon} **{label}**")
        else:
            st.markdown(f"{icon} {label}")
    
    st.markdown("---")
    st.caption("💡 Powered by:")
    st.caption("• Google Gemini 2.0 Flash")
    st.caption("• LangGraph Multi-Agent")
    st.caption("• Tavily Search API")
    
    if st.session_state.phase != 'onboarding':
        st.markdown("---")
        if st.button("🔄 Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ============================================================
# MAIN HEADER
# ============================================================

st.markdown('<div class="main-header">🔍 Company Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent account planning for sales professionals</div>', unsafe_allow_html=True)

# ============================================================
# PHASE 1.1: USER ONBOARDING FORM
# ============================================================

if st.session_state.phase == 'onboarding':
    st.markdown("---")
    st.markdown("### 👋 Welcome! Let's Get Started")
    st.markdown("""
    Before we research your target companies, I need to understand **your context**.
    This helps me create **personalized** account plans tailored to your unique value proposition.
    """)
    
    st.info("🔒 **Privacy Note:** Your information is only used for this session and is not stored permanently.")
    st.markdown("---")
    
    with st.form("user_info_form", clear_on_submit=False):
        st.subheader("📝 About You")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Your Name *", placeholder="e.g., Sarah Chen")
            role = st.text_input("Your Role/Title *", placeholder="e.g., Sales Director")
        
        with col2:
            email = st.text_input("Email (optional)", placeholder="sarah@company.com")
            research_purpose = st.selectbox(
                "Research Purpose *",
                ["Sales Outreach", "Partnership Opportunity", "Investment Analysis", "Competitive Research"]
            )
        
        st.markdown("---")
        st.subheader("🏢 About Your Company")
        
        col3, col4 = st.columns(2)
        
        with col3:
            company_name = st.text_input("Your Company Name *", placeholder="e.g., CloudSync, TechCorp")
            industry = st.text_input("Industry", placeholder="e.g., SaaS, Healthcare, FinTech")
        
        with col4:
            product_service = st.text_area(
                "Your Main Product/Service *",
                placeholder="Describe what your company offers...",
                height=120
            )
        
        st.markdown("---")
        
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            submitted = st.form_submit_button(
                "🚀 Continue to Phase 1: Research My Company",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            missing_fields = []
            if not name: missing_fields.append("Name")
            if not role: missing_fields.append("Role")
            if not company_name: missing_fields.append("Company Name")
            if not product_service: missing_fields.append("Product/Service")
            
            if missing_fields:
                st.error(f"⚠️ Please fill in: {', '.join(missing_fields)}")
            else:
                st.session_state.user_context = {
                    "name": name,
                    "role": role,
                    "email": email if email else None,
                    "company_name": company_name,
                    "industry": industry if industry else None,
                    "product_service": product_service,
                    "research_purpose": research_purpose
                }
                st.session_state.phase = 'verifying'
                st.success("✅ Information saved!")
                st.rerun()

# ============================================================
# PHASE 1.2: VERIFY USER'S COMPANY
# ============================================================

elif st.session_state.phase == 'verifying':
    user_ctx = st.session_state.user_context
    
    st.markdown("---")
    st.markdown(f"### 🔍 Step 2: Let me research **{user_ctx['company_name']}**")
    
    st.markdown(f"""
    Hi **{user_ctx['name']}**! Let me verify I understand your company correctly.
    """)
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    with st.spinner("🔍 Researching your company..."):
        try:
            progress_text.text("Searching web sources...")
            progress_bar.progress(25)
            
            progress_text.text("Checking Wikipedia...")
            progress_bar.progress(50)
            
            progress_text.text("Gathering news...")
            progress_bar.progress(75)
            
            user_research = research_user_company(user_ctx['company_name'])
            
            progress_text.text("Complete!")
            progress_bar.progress(100)
            
            st.session_state.user_company_research = user_research
            
            import time
            time.sleep(0.5)
            progress_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"⚠️ Research failed: {str(e)}")
            st.session_state.user_company_research = {
                "overview": f"{user_ctx['company_name']} provides {user_ctx['product_service']}",
                "products": [user_ctx['product_service']],
                "key_metrics": {},
                "news": [],
                "sources": [],
                "verified_by_user": False,
                "user_corrections": None
            }
    
    st.success("✅ Research Complete!")
    st.markdown("---")
    
    st.markdown(f"### 📊 Here's what I found about **{user_ctx['company_name']}**:")
    
    research = st.session_state.user_company_research
    
    if research.get('overview'):
        with st.expander("📋 Company Overview", expanded=True):
            st.markdown(research['overview'])
    
    if research.get('products'):
        with st.expander("🎯 Products/Services", expanded=True):
            for product in research['products']:
                st.markdown(f"• {product}")
    
    if research.get('key_metrics') and research['key_metrics']:
        with st.expander("💰 Key Metrics"):
            metrics = research['key_metrics']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Revenue", metrics.get('revenue', 'N/A'))
            with col2:
                st.metric("Employees", metrics.get('employees', 'N/A'))
            with col3:
                st.metric("Founded", metrics.get('founded', 'N/A'))
    
    if research.get('news'):
        with st.expander("📰 Recent News"):
            for news_item in research['news']:
                st.markdown(f"• {news_item}")
    
    st.markdown("---")
    st.markdown("### ✅ Verification")
    st.markdown("Is this information about your company **correct**?")
    
    corrections = st.text_area(
        "Any corrections or additional context? (optional)",
        placeholder="Add any missing information or corrections...",
        height=100
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Yes, This Looks Good!", use_container_width=True, type="primary"):
            st.session_state.user_company_research['verified_by_user'] = True
            st.session_state.user_company_research['user_corrections'] = corrections if corrections else None
            st.session_state.phase = 'follow_up'
            st.success("✅ Great! Moving to next step...")
            st.rerun()

# ============================================================
# PHASE 1.3: FOLLOW-UP QUESTIONS
# ============================================================

elif st.session_state.phase == 'follow_up':
    user_ctx = st.session_state.user_context
    
    st.markdown("---")
    st.markdown("### 🤔 Step 3: A Few More Questions")
    
    st.markdown(f"""
    Thanks **{user_ctx['name']}**! Now let me ask a few strategic questions to create
    the most **personalized** account plans.
    """)
    
    st.info("💡 **Why these questions?** Your answers help me tailor recommendations to YOUR value proposition.")
    
    st.markdown("---")
    
    with st.form("follow_up_form"):
        st.subheader("Strategic Context")
        
        value_prop = st.text_area(
            "1. What's your main value proposition? ⭐",
            placeholder="What problem do you solve? Why should customers choose you?",
            height=120
        )
        
        ideal_customers = st.text_area(
            "2. Who are your ideal customers?",
            placeholder="Company size, industries, specific roles/titles...",
            height=120
        )
        
        customer_challenges = st.text_area(
            "3. What challenges do your customers typically face?",
            placeholder="Before they work with you, what pain points do they experience?",
            height=120
        )
        
        differentiators = st.text_area(
            "4. What makes you different from competitors? ⭐",
            placeholder="Your unique selling points, competitive advantages...",
            height=120
        )
        
        st.markdown("---")
        
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            submitted = st.form_submit_button(
                "💾 Save Context & Continue to Phase 2",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            if not value_prop or not differentiators:
                st.error("⚠️ Please fill in at least Value Proposition and Differentiators (marked with ⭐)")
            else:
                st.session_state.follow_up_answers = {
                    "value_proposition": value_prop,
                    "ideal_customers": ideal_customers if ideal_customers else "Not specified",
                    "customer_challenges": customer_challenges if customer_challenges else "Not specified",
                    "differentiators": differentiators
                }
                st.session_state.onboarding_complete = True
                st.session_state.phase = 'research'
                st.success("✅ Context saved! Ready to research target companies!")
                st.balloons()
                st.rerun()

# ============================================================
# PHASE 2: TARGET COMPANY RESEARCH
# ============================================================

elif st.session_state.phase == 'research':
    user_ctx = st.session_state.user_context
    
    st.markdown("---")
    st.markdown("## 🎯 Phase 2: Target Company Research")
    
    st.success("✅ Phase 1 Complete! Your context has been saved.")
    
    # Show context summary
    with st.expander("📋 Your Context Summary", expanded=False):
        st.markdown(f"**Your Company:** {user_ctx['company_name']}")
        st.markdown(f"**Your Role:** {user_ctx['role']}")
        st.markdown(f"**Research Purpose:** {user_ctx['research_purpose']}")
        
        follow_up = st.session_state.follow_up_answers
        st.markdown("---")
        st.markdown("**Value Proposition:**")
        st.write(follow_up['value_proposition'][:200] + "...")
        st.markdown("**Differentiators:**")
        st.write(follow_up['differentiators'][:200] + "...")
    
    st.markdown("---")
    
    # Target company input
    if not st.session_state.research_complete:
        st.markdown("### 🔍 Enter Target Company to Research")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            target_company = st.text_input(
                "Target Company Name",
                placeholder="e.g., Microsoft, Tesla, Salesforce, Apple",
                key="target_company_input"
            )
        
        with col2:
            st.write("")
            st.write("")
            research_button = st.button(
                "🚀 Research",
                use_container_width=True,
                type="primary",
                disabled=not target_company
            )
        
        if research_button and target_company:
            # Initialize workflow state
            initial_state = create_initial_state(
                phase="research",
                user_context=user_ctx
            )
            initial_state['target_company_name'] = target_company
            initial_state['follow_up_answers'] = st.session_state.follow_up_answers
            
            # Create and run workflow
            st.markdown("---")
            st.markdown(f"### 🔬 Researching **{target_company}**...")
            
            progress_container = st.container()
            
            with progress_container:
                progress_placeholder = st.empty()
                
                try:
                    workflow = create_research_workflow()
                    
                    # Run workflow and display progress
                    final_state = None
                    for step_output in workflow.stream(initial_state, {"recursion_limit": 50}):
                        if 'progress_messages' in step_output:
                            latest_messages = step_output.get('progress_messages', [])
                            if latest_messages:
                                with progress_placeholder.container():
                                    for msg in latest_messages[-5:]:  # Show last 5 messages
                                        st.text(msg)
                        final_state = step_output
                    
                    # Store final state
                    st.session_state.workflow_state = final_state
                    st.session_state.research_complete = True
                    
                    progress_placeholder.empty()
                    st.success("🎉 Research Complete!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Research failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Display results if research is complete
    if st.session_state.research_complete and st.session_state.workflow_state:
        st.markdown("---")
        st.markdown("## 📊 Research Results")
        
        state = st.session_state.workflow_state
        
        # Show tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Account Plans", "🔍 Research Data", "⚠️ Conflicts", "📤 Export"])
        
        with tab1:
            st.markdown("### Compare: Personalized vs Generic")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Personalized Plan")
                st.markdown("*Uses YOUR context and value proposition*")
                
                if state.get('account_plan'):
                    plan = state['account_plan']
                    st.markdown(plan['content'])
                else:
                    st.warning("Personalized plan not generated")
            
            with col2:
                st.markdown("#### 📄 Generic Plan")
                st.markdown("*Standard approach without personalization*")
                
                if state.get('generic_plan'):
                    generic = state['generic_plan']
                    st.markdown(generic['content'])
                else:
                    st.warning("Generic plan not generated")
        
        with tab2:
            st.markdown("### Research Findings")
            
            # Web Results
            if state.get('web_results'):
                with st.expander(f"🌐 Web Search Results ({len(state['web_results'])} sources)"):
                    for i, result in enumerate(state['web_results'][:5], 1):
                        st.markdown(f"**{i}. {result.get('title', 'N/A')}**")
                        st.markdown(f"{result.get('snippet', 'N/A')}")
                        st.markdown(f"[Source]({result.get('url', '#')})")
                        st.markdown("---")
            
            # Financial Data
            if state.get('financial_data'):
                with st.expander("💰 Financial Information"):
                    fin = state['financial_data']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Revenue", f"${fin.get('revenue', 'N/A'):,}" if isinstance(fin.get('revenue'), int) else fin.get('revenue', 'N/A'))
                    with col2:
                        st.metric("Market Cap", f"${fin.get('market_cap', 'N/A'):,}" if isinstance(fin.get('market_cap'), int) else fin.get('market_cap', 'N/A'))
                    with col3:
                        st.metric("Employees", f"{fin.get('employees', 'N/A'):,}" if isinstance(fin.get('employees'), int) else fin.get('employees', 'N/A'))
            
            # Wikipedia
            if state.get('wiki_data'):
                with st.expander("📚 Wikipedia Overview"):
                    st.markdown(state['wiki_data'].get('summary', 'N/A'))
            
            # News
            if state.get('news_data'):
                with st.expander(f"📰 Recent News ({len(state['news_data'])} articles)"):
                    for news in state['news_data']:
                        st.markdown(f"**{news.get('title', 'N/A')}**")
                        st.markdown(f"[Read more]({news.get('link', '#')})")
                        st.markdown("---")
        
        with tab3:
            st.markdown("### Conflict Detection")
            
            conflicts = state.get('conflicts', [])
            
            if conflicts:
                st.warning(f"⚠️ Found {len(conflicts)} potential conflict(s)")
                for i, conflict in enumerate(conflicts, 1):
                    st.markdown(f"**{i}. {conflict.get('description', 'Unknown conflict')}**")
                    st.markdown(f"Sources: {conflict.get('sources', 'Unknown')}")
                    st.markdown(f"Confidence: {conflict.get('confidence', 'MEDIUM')}")
                    st.markdown("---")
            else:
                st.success("✅ No conflicts detected in research data")
        
        with tab4:
            st.markdown("### Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 Export Personalized Plan")
                
                if state.get('account_plan'):
                    # JSON Export
                    json_data = export_to_json(state['account_plan'])
                    st.download_button(
                        "⬇️ Download as JSON",
                        json_data,
                        file_name=f"account_plan_{state['target_company_name']}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    # PDF Export
                    pdf_buffer = export_to_pdf(state['account_plan']['content'])
                    st.download_button(
                        "⬇️ Download as PDF",
                        pdf_buffer,
                        file_name=f"account_plan_{state.get('target_company_name', 'company')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col2:
                st.markdown("#### 📊 Export Full Research")
                
                full_data = {
                    "target_company": state.get('target_company_name'),
                    "generated_at": datetime.now().isoformat(),
                    "user_company": user_ctx['company_name'],
                    "research_data": {
                        "web_results": state.get('web_results', []),
                        "financial_data": state.get('financial_data', {}),
                        "wiki_data": state.get('wiki_data', {}),
                        "news_data": state.get('news_data', [])
                    },
                    "synthesized_data": state.get('synthesized_data', ''),
                    "account_plan": state.get('account_plan', {}),
                    "conflicts": state.get('conflicts', [])
                }
                
                json_data = export_to_json(full_data)
                st.download_button(
                    "⬇️ Download Full Report (JSON)",
                    json_data,
                    file_name=f"full_research_{state.get('target_company_name', 'company')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Research another company
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Research Another Company", use_container_width=True, type="primary"):
                st.session_state.research_complete = False
                st.session_state.workflow_state = None
                st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>🤖 Powered by Google Gemini 2.0 Flash, LangGraph & Tavily</p>
    <p>💡 100% Free & Open Source Tools</p>
</div>
""", unsafe_allow_html=True)