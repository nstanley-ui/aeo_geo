import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from execution.check_aeo import check_domain
from execution.check_socials import audit_socials
from execution.check_competitors import check_competitors
from execution.crawl_site import crawl_domain

# --- Page Configuration ---
st.set_page_config(
    page_title="Mojo AEO Checker", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom Styling (Soft/Warm Theme) ---
st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background: radial-gradient(circle at top left, #fff7ed, #e7e5e4);
        color: #44403c;
    }
    
    /* Card Styling */
    div[data-testid="stMetric"], div.stExpander {
        background-color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 10px;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3);
    }
    
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1c1917; }
    .stMarkdown a { color: #ea580c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'domain' not in st.session_state:
    st.session_state.domain = 'demandbase.com'
if 'entity_data' not in st.session_state:
    st.session_state.entity_data = {'name': '', 'type': 'Organization'}
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = None  # Store generated files here so buttons persist

# --- Helper Functions ---
def get_file_url(domain, filename):
    clean_domain = domain.replace("https://", "").replace("http://", "").strip("/")
    return f"https://{clean_domain}/{filename}"

def get_engine_status(content, bot_name):
    if not content: return "Unknown", "gray"
    if f"User-agent: {bot_name}" in content and "Disallow: /" in content: return "Blocked", "red"
    if f"User-agent: {bot_name}" in content and "Allow: /" in content: return "Allowed", "green"
    return "Implicit Allow", "green"

# --- UI: STEP 1 (Input) ---
if st.session_state.step == 'input':
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🚀 MOJO AEO CHECKER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #78716c; margin-bottom: 40px;'>Visibility Intelligence for the Agent Economy</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        domain_input = st.text_input("Enter Domain", value=st.session_state.domain, placeholder="company.com")
        if st.button("Start Audit", use_container_width=True):
            st.session_state.domain = domain_input
            detected_name = domain_input.split('.')[0].capitalize()
            st.session_state.entity_data['name'] = detected_name
            st.session_state.step = 'confirm'
            st.rerun()

# --- UI: STEP 2 (Entity Confirmation) ---
elif st.session_state.step == 'confirm':
    st.markdown("### 🛡️ Verify Identity")
    st.info("Why this matters: Accurate scoring requires establishing the correct semantic entity before analysis begins.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.entity_data['name'] = st.text_input("Brand Name", st.session_state.entity_data['name'])
    with c2:
        # Removed Person, kept Organization and Product
        st.session_state.entity_data['type'] = st.selectbox("Entity Type", ["Organization", "Product"])
        if st.session_state.entity_data['type'] == "Product":
            st.caption("ℹ️ We will check for 'Product' schema markup instead of 'Organization'.")
        
    c_back, c_go = st.columns([1, 2])
    with c_back:
        if st.button("← Back"):
            st.session_state.step = 'input'
            st.rerun()
    with c_go:
        if st.button("Confirm & Analyze 🚀", type="primary"):
            st.session_state.step = 'results'
            st.rerun()

# --- UI: STEP 3 (Results Dashboard) ---
elif st.session_state.step == 'results':
    
    # Header Row: Title on Left, Reset Button on Right
    head_c1, head_c2 = st.columns([3, 1])
    with head_c1:
        st.markdown(f"## Analysis: {st.session_state.entity_data['name']}")
        st.caption(f"Target: {st.session_state.domain} | Type: {st.session_state.entity_data['type']}")
    with head_c2:
        if st.button("🔄 Start New Audit", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.generated_files = None # Clear generated files
            st.session_state.step = 'input'
            st.rerun()

    # Run analysis
    if st.session_state.analysis_result is None:
        with st.spinner(f"Analyzing semantic protocols for {st.session_state.domain}..."):
            aeo_data = check_domain(st.session_state.domain, st.session_state.entity_data['type'])
            social_data = audit_socials(st.session_state.domain)
            overall_score = (aeo_data.get("aeo_score", 0) + social_data.get("overall_social_score", 0)) // 2
            
            st.session_state.analysis_result = {
                "aeo": aeo_data,
                "social": social_data,
                "score": overall_score
            }

    data = st.session_state.analysis_result
    
    # Top Row: Score & Engine Status
    col_score, col_engines = st.columns([1, 2])
    
    with col_score:
        st.metric("Overall Mojo Score", f"{data['score']}/100")
        categories = ['AEO Score', 'Social Score', 'LinkedIn', 'Crunchbase', 'Reddit']
        values = [
            data['aeo'].get("aeo_score", 0),
            data['social'].get("overall_social_score", 0),
            data['social']['platforms'][0]['score'],
            data['social']['platforms'][1]['score'],
            data['social']['platforms'][2]['score']
        ]
        fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#ea580c'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=20, r=20, t=20, b=20), height=200)
        st.plotly_chart(fig, use_container_width=True)

    with col_engines:
        st.subheader("🤖 Engine Visibility")
        robots_content = data['aeo']['robots_txt'].get('content', '')
        engines = [("GPT-4 (OpenAI)", "GPTBot"), ("Claude 3", "ClaudeBot"), ("Perplexity", "PerplexityBot"), ("Gemini", "Google-Extended")]
        e_cols = st.columns(2)
        for i, (name, bot_id) in enumerate(engines):
            status, color = get_engine_status(robots_content, bot_id)
            with e_cols[i % 2]:
                st.markdown(f"<div style='padding:10px; border:1px solid #ddd; border-radius:8px; margin-bottom:10px; background:rgba(255,255,255,0.5)'><strong>{name}</strong><br><span style='color:{color}; font-weight:bold;'>● {status}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Middle Row: File Inspector
    st.subheader("📄 Agent Infrastructure Files")
    file_map = {"llm_txt": "llms.txt", "ai_txt": "ai.txt", "robots_txt": "robots.txt"}
    file_cols = st.columns(3)
    
    for idx, (f_key, f_display_default) in enumerate(file_map.items()):
        with file_cols[idx]:
            file_info = data['aeo'].get(f_key, {})
            f_name = file_info.get('filename', f_display_default)
            exists = file_info.get('exists', False)
            grade = file_info.get('grade', 'Missing')
            manual_url = get_file_url(st.session_state.domain, f_name)
            
            with st.container(border=True):
                st.markdown(f"**{f_name}**")
                if exists: st.markdown(f":green-background[Found] **Grade: {grade}**")
                else: st.markdown(f":red-background[Not Detected by Bot]")
                st.markdown(f"🔗 [Open live link to verify]({manual_url})")
                if exists and file_info.get('content'):
                    with st.expander("View Content"):
                        st.code(file_info['content'][:500] + "...", language="text")

    st.markdown("---")
    
    # Bottom Row: File Generator
    st.subheader("🛠️ Generator")
    
    # 1. Generate Button
    if st.button("Generate Optimized Files"):
        with st.spinner("Crawling site to build assets..."):
            st.session_state.generated_files = crawl_domain(st.session_state.domain)
            st.rerun() # Force rerun to show buttons immediately
            
    # 2. Show Download Buttons (Persistent State)
    if st.session_state.generated_files:
        gen_files = st.session_state.generated_files
        st.success(f"Generated assets based on {gen_files['analysis']['pages_crawled']} crawled pages.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(f"Download llms.txt", gen_files['llm_txt'], "llms.txt")
        with c2:
            st.download_button(f"Download ai.txt", gen_files['ai_txt'], "ai.txt")
        with c3:
            st.download_button(f"Download robots.txt", gen_files['robots_txt'], "robots.txt")
            
        with st.expander("Preview Generated llms.txt"):
            st.code(gen_files['llm_txt'])
