"""
Company Research Assistant - Simple Implementation
Streamlit UI for generating company account plans
"""
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from research_utils import run_research, format_raw_data
from prompts import (
    get_full_plan_prompt,
    get_section_edit_prompt,
    get_conflict_detection_prompt
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Page configuration
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
    }
    .section-container {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'account_plan' not in st.session_state:
    st.session_state.account_plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'editing_section' not in st.session_state:
    st.session_state.editing_section = None


def add_chat_message(message, sender="system"):
    """Add message to chat history"""
    st.session_state.chat_history.append({
        'sender': sender,
        'message': message
    })


def generate_account_plan(company_name, research_data, focus_areas=""):
    """Generate complete account plan using LLM"""

    # Format research data
    raw_data = format_raw_data(research_data)

    # Create prompt
    prompt = get_full_plan_prompt(company_name, raw_data, focus_areas)

    # Call LLM (using gemini-1.5-flash-latest which is always available)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)

    return response.text


def edit_section(company_name, section_name, current_content, edit_instructions, research_data):
    """Edit a specific section of the account plan"""

    raw_data = format_raw_data(research_data)

    prompt = get_section_edit_prompt(
        company_name,
        section_name,
        current_content,
        edit_instructions,
        raw_data
    )

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)

    return response.text


def parse_account_plan(plan_text):
    """Parse account plan into sections"""
    sections = {}
    current_section = None
    current_content = []

    lines = plan_text.split('\n')

    section_markers = [
        'EXECUTIVE SUMMARY',
        'COMPANY OVERVIEW',
        'FINANCIAL SNAPSHOT',
        'LEADERSHIP',
        'PRODUCTS & SERVICES',
        'RECENT NEWS',
        'SWOT ANALYSIS',
        'OPPORTUNITIES FOR ENGAGEMENT',
        'RISKS / OBJECTIONS',
        'NEXT STEPS',
        'SOURCES & EVIDENCE'
    ]

    for line in lines:
        # Check if line is a section header
        is_section = False
        for marker in section_markers:
            if marker in line.upper() and line.startswith('#'):
                is_section = True
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Start new section
                current_section = marker
                current_content = [line]
                break

        if not is_section and current_section:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


# ============================================================
# MAIN APP
# ============================================================

st.markdown('<div class="main-header">🔍 Company Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">AI-powered account plan generation with multi-source research</p>', unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# INPUT SECTION
# ============================================================

col1, col2 = st.columns([2, 1])

with col1:
    company_name = st.text_input(
        "🏢 Enter Company Name",
        placeholder="e.g., Microsoft, Tesla, Amazon",
        help="Enter the name of the company you want to research"
    )

with col2:
    focus_areas = st.text_area(
        "🎯 Specific Focus Areas (Optional)",
        placeholder="e.g., Cloud services, AI products",
        height=100,
        help="Optional: Specify particular areas to focus on"
    )

start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

st.markdown("---")

# ============================================================
# RESEARCH EXECUTION
# ============================================================

if start_button and company_name:
    st.session_state.chat_history = []  # Reset chat
    add_chat_message(f"Starting research for **{company_name}**...")

    # Run research
    with st.spinner("🔍 Conducting research..."):
        result = run_research(company_name, focus_areas)
        st.session_state.research_data = result['data']

        # Add progress messages to chat
        for msg in result['messages']:
            add_chat_message(msg)

    # Check for conflicts
    conflicts = st.session_state.research_data.get('conflicts', [])
    if conflicts:
        conflict_msg = f"⚠️ Found {len(conflicts)} data conflicts. Proceeding with best available data."
        add_chat_message(conflict_msg)

    # Generate account plan
    add_chat_message("📝 Generating comprehensive account plan...")

    with st.spinner("✍️ Writing account plan..."):
        plan_text = generate_account_plan(
            company_name,
            st.session_state.research_data,
            focus_areas
        )
        st.session_state.account_plan = {
            'text': plan_text,
            'company': company_name,
            'sections': parse_account_plan(plan_text)
        }

    add_chat_message("✅ Account plan complete!")

# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================

if st.session_state.chat_history:
    st.subheader("💬 Research Progress")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            st.markdown(f'<div class="chat-message">{msg["message"]}</div>', unsafe_allow_html=True)

    st.markdown("---")

# ============================================================
# ACCOUNT PLAN DISPLAY WITH SECTION EDITING
# ============================================================

if st.session_state.account_plan:
    st.subheader("📋 Account Plan")

    plan = st.session_state.account_plan
    sections = plan['sections']

    # Display each section with edit button
    for section_name, section_content in sections.items():
        with st.expander(f"📄 {section_name}", expanded=True):
            # Display section content
            st.markdown(section_content)

            # Edit button
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                if st.button(f"✏️ Edit Section", key=f"edit_{section_name}"):
                    st.session_state.editing_section = section_name

            # If this section is being edited
            if st.session_state.editing_section == section_name:
                st.markdown("---")
                st.markdown("**Edit Instructions:**")

                edit_instructions = st.text_area(
                    "What would you like to change?",
                    placeholder="e.g., Add more details about AI products, Update financial data, Make it more concise",
                    key=f"edit_input_{section_name}",
                    height=100
                )

                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    if st.button("💾 Apply Changes", key=f"apply_{section_name}"):
                        with st.spinner("Updating section..."):
                            updated_content = edit_section(
                                plan['company'],
                                section_name,
                                section_content,
                                edit_instructions,
                                st.session_state.research_data
                            )

                            # Update the section
                            st.session_state.account_plan['sections'][section_name] = updated_content

                            # Rebuild full text
                            full_text = '\n\n'.join(st.session_state.account_plan['sections'].values())
                            st.session_state.account_plan['text'] = full_text

                            st.session_state.editing_section = None
                            st.success(f"✅ {section_name} updated!")
                            st.rerun()

                with col_b:
                    if st.button("❌ Cancel", key=f"cancel_{section_name}"):
                        st.session_state.editing_section = None
                        st.rerun()

    st.markdown("---")

    # Export options
    st.subheader("📥 Export")

    col1, col2 = st.columns(2)

    with col1:
        # Download as text
        st.download_button(
            "⬇️ Download as Text",
            st.session_state.account_plan['text'],
            file_name=f"account_plan_{plan['company'].replace(' ', '_')}.txt",
            mime="text/plain"
        )

    with col2:
        # Download as markdown
        st.download_button(
            "⬇️ Download as Markdown",
            st.session_state.account_plan['text'],
            file_name=f"account_plan_{plan['company'].replace(' ', '_')}.md",
            mime="text/markdown"
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>Company Research Assistant | Built with Streamlit & Google Gemini</p>
    <p>Data sources: Tavily, Alpha Vantage, Wikipedia, Google News</p>
</div>
""", unsafe_allow_html=True)
