"""
Company Research Assistant - Streamlit App
Two-Phase Approach: User Onboarding → Target Research
"""
import streamlit as st
import os
from dotenv import load_dotenv
from agents.research import research_user_company
from utils.state import UserContext, create_initial_state

# Load environment variables
load_dotenv()

# Verify Gemini API key
if not os.getenv('GEMINI_API_KEY'):
    st.error("⚠️ GEMINI_API_KEY not found! Please set it in .env file")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
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

# ============================================================
# SIDEBAR - Progress Tracker
# ============================================================

with st.sidebar:
    st.markdown("### 📊 Process Flow")
    st.markdown("---")
    
    # Phase indicators
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
    st.caption("• 100% Free Tools")
    
    # Reset button
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
    
    # Welcome message
    st.markdown("### 👋 Welcome! Let's Get Started")
    st.markdown("""
    Before we research your target companies, I need to understand **your context**.
    This helps me create **personalized** account plans tailored to your unique value proposition.
    """)
    
    st.info("🔒 **Privacy Note:** Your information is only used for this session and is not stored permanently.")
    
    st.markdown("---")
    
    # The form
    with st.form("user_info_form", clear_on_submit=False):
        st.subheader("📝 About You")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Your Name *",
                placeholder="e.g., Sarah Chen",
                help="What should I call you?"
            )
            role = st.text_input(
                "Your Role/Title *",
                placeholder="e.g., Sales Director, Business Development Manager",
                help="Your position in your company"
            )
        
        with col2:
            email = st.text_input(
                "Email (optional)",
                placeholder="sarah@company.com",
                help="Optional - for generating reports"
            )
            research_purpose = st.selectbox(
                "Research Purpose *",
                [
                    "Sales Outreach",
                    "Partnership Opportunity",
                    "Investment Analysis",
                    "Competitive Research"
                ],
                help="What's your goal for researching companies?"
            )
        
        st.markdown("---")
        st.subheader("🏢 About Your Company")
        
        col3, col4 = st.columns(2)
        
        with col3:
            company_name = st.text_input(
                "Your Company Name *",
                placeholder="e.g., CloudSync, TechCorp",
                help="I'll research YOUR company first to understand your context"
            )
            industry = st.text_input(
                "Industry",
                placeholder="e.g., SaaS, Healthcare, FinTech, Manufacturing",
                help="What industry are you in?"
            )
        
        with col4:
            product_service = st.text_area(
                "Your Main Product/Service *",
                placeholder="Describe what your company offers...\ne.g., 'AI-powered CRM platform for small businesses'",
                height=120,
                help="What does your company sell or provide?"
            )
        
        st.markdown("---")
        
        # Submit button
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            submitted = st.form_submit_button(
                "🚀 Continue to Phase 1: Research My Company",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validation
            missing_fields = []
            if not name:
                missing_fields.append("Name")
            if not role:
                missing_fields.append("Role")
            if not company_name:
                missing_fields.append("Company Name")
            if not product_service:
                missing_fields.append("Product/Service")
            
            if missing_fields:
                st.error(f"⚠️ Please fill in the following required fields: {', '.join(missing_fields)}")
            else:
                # Store user context
                st.session_state.user_context = {
                    "name": name,
                    "role": role,
                    "email": email if email else None,
                    "company_name": company_name,
                    "industry": industry if industry else None,
                    "product_service": product_service,
                    "research_purpose": research_purpose
                }
                
                # Move to verification phase
                st.session_state.phase = 'verifying'
                st.success("✅ Information saved! Moving to next step...")
                st.rerun()

# ============================================================
# PHASE 1.2: VERIFY USER'S COMPANY
# ============================================================

elif st.session_state.phase == 'verifying':
    user_ctx = st.session_state.user_context
    
    st.markdown("---")
    st.markdown(f"### 🔍 Step 2: Let me research **{user_ctx['company_name']}**")
    
    st.markdown(f"""
    Hi **{user_ctx['name']}**! Before we research your target companies, let me verify 
    I understand your company correctly. This helps me create more accurate and personalized plans.
    """)
    
    # Progress indicator
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    # Run research
    with st.spinner("🔍 Researching your company..."):
        try:
            progress_text.text("Searching web sources...")
            progress_bar.progress(25)
            
            progress_text.text("Checking Wikipedia...")
            progress_bar.progress(50)
            
            progress_text.text("Gathering recent news...")
            progress_bar.progress(75)
            
            # Actually run the research
            user_research = research_user_company(user_ctx['company_name'])
            
            progress_text.text("Analysis complete!")
            progress_bar.progress(100)
            
            st.session_state.user_company_research = user_research
            
            # Clear progress indicators
            import time
            time.sleep(0.5)
            progress_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"⚠️ Research failed: {str(e)}")
            st.info("You can still continue with manual information.")
            
            # Create minimal research result
            st.session_state.user_company_research = {
                "overview": f"{user_ctx['company_name']} provides {user_ctx['product_service']}",
                "products": [user_ctx['product_service']],
                "key_metrics": {},
                "news": [],
                "sources": [],
                "verified_by_user": False,
                "user_corrections": None
            }
    
    # Display findings
    st.success("✅ Research Complete!")
    st.markdown("---")
    
    st.markdown(f"### 📊 Here's what I found about **{user_ctx['company_name']}**:")
    
    research = st.session_state.user_company_research
    
    # Overview
    if research.get('overview'):
        with st.expander("📋 Company Overview", expanded=True):
            st.markdown(research['overview'])
    
    # Products/Services
    if research.get('products'):
        with st.expander("🎯 Products/Services", expanded=True):
            for product in research['products']:
                st.markdown(f"• {product}")
    
    # Key Metrics
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
    
    # Recent News
    if research.get('news'):
        with st.expander("📰 Recent News"):
            for news_item in research['news']:
                st.markdown(f"• {news_item}")
    
    st.markdown("---")
    
    # Verification
    st.markdown("### ✅ Verification")
    st.markdown("Is this information about your company **correct**?")
    
    corrections = st.text_area(
        "Any corrections or additional context? (optional)",
        placeholder="Add any missing information or corrections...\n\nFor example:\n• We recently launched a new product line\n• Our main focus has shifted to enterprise clients\n• The revenue figure is outdated",
        height=100
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Yes, This Looks Good!", use_container_width=True, type="primary"):
            # Mark as verified
            st.session_state.user_company_research['verified_by_user'] = True
            st.session_state.user_company_research['user_corrections'] = corrections if corrections else None
            
            # Move to follow-up phase
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
    Thanks **{user_ctx['name']}**! Now I understand your company. 
    
    Let me ask a few strategic questions to help me create the most **personalized** 
    account plans for your target companies.
    """)
    
    st.info("💡 **Why these questions?** Your answers help me tailor recommendations specifically to YOUR value proposition and competitive advantages.")
    
    st.markdown("---")
    
    with st.form("follow_up_form"):
        st.subheader("Strategic Context")
        
        value_prop = st.text_area(
            "1. What's your main value proposition? ⭐",
            placeholder="What problem do you solve? Why should customers choose you?\n\nExample: 'We help small businesses automate their sales process with AI, reducing manual data entry by 50% and increasing conversion rates by 30%.'",
            height=120,
            help="This will be used to position your solution against target companies"
        )
        
        ideal_customers = st.text_area(
            "2. Who are your ideal customers?",
            placeholder="Company size, industries, specific roles/titles...\n\nExample: 'Small to mid-sized B2B SaaS companies (10-200 employees) with sales teams of 5-20 people, typically targeting Sales Directors and VPs of Sales.'",
            height=120,
            help="Helps identify which features to emphasize"
        )
        
        customer_challenges = st.text_area(
            "3. What challenges do your customers typically face?",
            placeholder="Before they work with you, what pain points do they experience?\n\nExample: 'Manual data entry taking 2+ hours daily, poor visibility into sales pipeline, missed follow-ups with leads, inconsistent sales process across team.'",
            height=120,
            help="Used to identify opportunities in target companies"
        )
        
        differentiators = st.text_area(
            "4. What makes you different from competitors? ⭐",
            placeholder="Your unique selling points, competitive advantages...\n\nExample: 'Native mobile app (competitors are web-only), real-time collaboration features, fastest implementation (3 days vs 2 weeks), AI-powered insights built-in.'",
            height=120,
            help="Critical for creating your unique engagement strategy"
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
            # Validation (optional but recommended)
            if not value_prop or not differentiators:
                st.error("⚠️ Please fill in at least the Value Proposition and Differentiators (marked with ⭐)")
            else:
                # Store follow-up answers
                st.session_state.follow_up_answers = {
                    "value_proposition": value_prop,
                    "ideal_customers": ideal_customers if ideal_customers else "Not specified",
                    "customer_challenges": customer_challenges if customer_challenges else "Not specified",
                    "differentiators": differentiators
                }
                
                # Mark onboarding as complete
                st.session_state.onboarding_complete = True
                st.session_state.phase = 'research'
                
                st.success("✅ Context saved! Ready to research target companies!")
                st.balloons()
                st.rerun()

# ============================================================
# PHASE 2: TARGET COMPANY RESEARCH (Placeholder)
# ============================================================

elif st.session_state.phase == 'research':
    user_ctx = st.session_state.user_context
    
    st.markdown("---")
    st.markdown("## 🎯 Phase 2: Target Company Research")
    
    st.success("✅ Phase 1 Complete! Your context has been saved.")
    
    # Show context summary
    with st.expander("📋 Your Context Summary (Click to view)", expanded=False):
        st.markdown(f"**Your Company:** {user_ctx['company_name']}")
        st.markdown(f"**Your Role:** {user_ctx['role']}")
        st.markdown(f"**Research Purpose:** {user_ctx['research_purpose']}")
        st.markdown(f"**Your Product:** {user_ctx['product_service'][:100]}...")
        
        follow_up = st.session_state.follow_up_answers
        st.markdown("---")
        st.markdown("**Value Proposition:**")
        st.write(follow_up['value_proposition'][:200] + "...")
        st.markdown("**Differentiators:**")
        st.write(follow_up['differentiators'][:200] + "...")
    
    st.markdown("---")
    
    # Target company input
    st.markdown("### 🔍 Enter Target Company to Research")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        target_company = st.text_input(
            "Target Company Name",
            placeholder="e.g., Microsoft, Tesla, Salesforce, Apple",
            help="Enter the company you want to create an account plan for",
            key="target_company_input"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        research_button = st.button(
            "🚀 Research",
            use_container_width=True,
            type="primary",
            disabled=not target_company
        )
    
    if research_button and target_company:
        st.info("🚧 Phase 2 implementation coming in the next step!")
        st.markdown(f"""
        **Next Steps:**
        1. Research {target_company} using multi-agent system
        2. Detect any conflicting information
        3. Generate personalized account plan using YOUR context
        4. Show side-by-side comparison: Generic vs Personalized
        """)
        
        st.markdown("---")
        st.markdown("### 🎉 Phase 1 is Complete!")
        st.markdown("""
        **What you've accomplished:**
        - ✅ Provided your company context
        - ✅ Verified your company research
        - ✅ Answered strategic questions
        - ✅ Set up personalization context
        
        **What's next (Phase 2):**
        - 🔍 Multi-agent research of target company
        - ✅ Conflict detection & verification
        - 📝 Personalized account plan generation
        - 📤 Export to PDF/JSON
        """)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>🤖 Powered by Google Gemini 2.0 Flash & LangGraph</p>
    <p>💡 100% Free & Open Source Tools</p>
</div>
""", unsafe_allow_html=True)