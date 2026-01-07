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

# --- Custom Styling (HubSpot/Scrunch Inspired) ---
st.markdown("""
    <style>
    /* Global Theme */
    .stApp {
        background: radial-gradient(circle at top left, #fff7ed, #f5f5f4);
        color: #44403c;
    }
    
    /* Card Styling */
    div[data-testid="stMetric"], div.stExpander, div.stContainer {
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(231, 229, 228, 0.8);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        padding: 15px;
    }

    /* Buttons */
    div.stButton > button {
        background: #ea580c;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background: #c2410c;
        transform: translateY(-2px);
    }
    
    /* Progress Bars (HubSpot Style) */
    .stProgress > div > div > div > div {
        background-color: #ea580c;
    }
    
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1c1917; }
    .metric-label { font-size: 0.8rem; text-transform: uppercase; color: #78716c; font-weight: 700; letter-spacing: 0.05em; }
    .metric-value { font-size: 1.5rem; font-weight: 800; color: #1c1917; }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'step' not in st.session_state: st.session_state.step = 'input'
if 'domain' not in st.session_state: st.session_state.domain = 'demandbase.com'
if 'entity_data' not in st.session_state: st.session_state.entity_data = {'name': '', 'type': 'Organization'}
if 'analysis_result' not in st.session_state: st.session_state.analysis_result = None
if 'generated_files' not in st.session_state: st.session_state.generated_files = None

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
    st.markdown("<h1 style='text-align: center;'>🚀 MOJO AEO CHECKER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #78716c;'>Diagnostic Intelligence for the Agent Economy</p>", unsafe_allow_html=True)
    
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
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.entity_data['name'] = st.text_input("Brand Name", st.session_state.entity_data['name'])
    with c2:
        st.session_state.entity_data['type'] = st.selectbox("Entity Type", ["Organization", "Product"])
        
    c_back, c_go = st.columns([1, 2])
    with c_back:
        if st.button("← Back"): st.session_state.step = 'input'; st.rerun()
    with c_go:
        if st.button("Confirm & Analyze 🚀", type="primary"): st.session_state.step = 'results'; st.rerun()

# --- UI: STEP 3 (Results Dashboard) ---
elif st.session_state.step == 'results':
    
    # Header
    head_c1, head_c2 = st.columns([3, 1])
    with head_c1:
        st.markdown(f"## {st.session_state.entity_data['name']}")
        st.caption(f"Domain: {st.session_state.domain}")
    with head_c2:
        if st.button("🔄 New Audit", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.generated_files = None
            st.session_state.step = 'input'
            st.rerun()

    if st.session_state.analysis_result is None:
        with st.spinner("Analyzing infrastructure & competitors..."):
            aeo_data = check_domain(st.session_state.domain, st.session_state.entity_data['type'])
            social_data = audit_socials(st.session_state.domain)
            comp_data = check_competitors(st.session_state.domain) # Fetch competitors now
            
            # --- New Logic: Breakdown Scores ---
            tech_score = aeo_data.get("aeo_score", 0) # Files & Tech
            trust_score = social_data.get("overall_social_score", 0) # Socials
            # Simulate content score for now based on Schema presence
            content_score = 85 if aeo_data["metadata"]["schema_org"] else 40 
            
            overall_score = int((tech_score + trust_score + content_score) / 3)
            
            st.session_state.analysis_result = {
                "aeo": aeo_data,
                "social": social_data,
                "competitors": comp_data,
                "scores": {
                    "overall": overall_score,
                    "tech": tech_score,
                    "trust": trust_score,
                    "content": content_score
                }
            }

    data = st.session_state.analysis_result
    scores = data['scores']

    # --- SECTION 1: HUBSPOT-STYLE DIAGNOSTICS ---
    col_main, col_detail = st.columns([1, 2])
    
    with col_main:
        # Main Score Card
        st.markdown(f"""
        <div style="text-align:center; padding:20px;">
            <div style="font-size:4rem; font-weight:900; color:#ea580c; line-height:1;">{scores['overall']}</div>
            <div style="font-size:0.9rem; font-weight:700; text-transform:uppercase; color:#78716c;">Mojo Authority Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Engine Status Mini-Grid
        st.markdown("##### 🤖 Engine Access")
        robots_content = data['aeo']['robots_txt'].get('content', '')
        engines = [("GPT-4", "GPTBot"), ("Claude", "ClaudeBot"), ("Pplx", "PerplexityBot"), ("Gemini", "Google-Extended")]
        
        e_grid = st.columns(2)
        for i, (name, bot_id) in enumerate(engines):
            status, color = get_engine_status(robots_content, bot_id)
            with e_grid[i % 2]:
                st.markdown(f"<div style='font-size:0.75rem; padding:4px; border-left:3px solid {color}; margin-bottom:4px;'>{name}</div>", unsafe_allow_html=True)

    with col_detail:
        st.markdown("### Performance Drivers")
        
        # 1. Tech Health
        st.markdown(f"<div class='metric-label'>Infrastructure Health <span style='float:right'>{scores['tech']}/100</span></div>", unsafe_allow_html=True)
        st.progress(scores['tech'] / 100)
        st.caption("Based on robots.txt, llms.txt, and ai.txt protocols.")
        
        # 2. Entity Trust
        st.markdown(f"<div class='metric-label'>Entity Trust <span style='float:right'>{scores['trust']}/100</span></div>", unsafe_allow_html=True)
        st.progress(scores['trust'] / 100)
        st.caption("Based on Knowledge Graph verification and Social footprint.")
        
        # 3. Content Signal
        st.markdown(f"<div class='metric-label'>Content Signal <span style='float:right'>{scores['content']}/100</span></div>", unsafe_allow_html=True)
        st.progress(scores['content'] / 100)
        st.caption("Based on Schema markup and 'Answer-First' formatting.")

    st.markdown("---")

    # --- SECTION 2: SCRUNCH-STYLE SHARE OF VOICE ---
    st.subheader("🏆 Share of Voice Leaderboard")
    
    # Simulate a "Total Market" calculation to get percentages
    comps = data['competitors']['competitors']
    total_market_points = sum(c['score'] for c in comps) + scores['overall']
    
    # Add User to list for comparison
    ranking_list = comps + [{'name': f"{st.session_state.entity_data['name']} (You)", 'score': scores['overall'], 'is_user': True}]
    ranking_list.sort(key=lambda x: x['score'], reverse=True)
    
    # Render Leaderboard
    for rank, entity in enumerate(ranking_list, 1):
        sov_percent = int((entity['score'] / total_market_points) * 100)
        is_user = entity.get('is_user', False)
        bg_color = "rgba(234, 88, 12, 0.1)" if is_user else "rgba(255,255,255,0.5)"
        border_color = "#ea580c" if is_user else "#e7e5e4"
        
        cols = st.columns([1, 4, 2])
        with cols[0]:
            st.markdown(f"<h3 style='text-align:center; color:#a8a29e;'>#{rank}</h3>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div style='font-weight:bold; font-size:1.1rem;'>{entity['name']}</div>", unsafe_allow_html=True)
            st.progress(sov_percent / 100)
        with cols[2]:
            st.markdown(f"<div style='text-align:right; font-weight:900; font-size:1.2rem; color:#78716c;'>{sov_percent}%</div>", unsafe_allow_html=True)
            st.caption("Est. Share of Voice")
        st.markdown(f"<hr style='margin:5px 0; border-top: 1px solid {border_color};'>", unsafe_allow_html=True)

    st.markdown("---")

    # --- SECTION 3: INFRASTRUCTURE (Original Mojo Features) ---
    st.subheader("📄 Agent Files")
    file_map = {"llm_txt": "llms.txt", "ai_txt": "ai.txt", "robots_txt": "robots.txt"}
    file_cols = st.columns(3)
    
    for idx, (f_key, f_display_default) in enumerate(file_map.items()):
        with file_cols[idx]:
            file_info = data['aeo'].get(f_key, {})
            f_name = file_info.get('filename', f_display_default)
            exists = file_info.get('exists', False)
            manual_url = get_file_url(st.session_state.domain, f_name)
            
            with st.container():
                st.markdown(f"**{f_name}**")
                if exists: st.markdown(f":green-background[Found]")
                else: st.markdown(f":red-background[Missing]")
                st.markdown(f"🔗 [Verify Link]({manual_url})")

    # Generator
    st.markdown("##### 🛠️ Fix Missing Files")
    if st.button("Generate Optimized Files"):
        with st.spinner("Crawling site..."):
            st.session_state.generated_files = crawl_domain(st.session_state.domain)
            st.rerun()
            
    if st.session_state.generated_files:
        gen = st.session_state.generated_files
        c1, c2, c3 = st.columns(3)
        with c1: st.download_button("Download llms.txt", gen['llm_txt'], "llms.txt")
        with c2: st.download_button("Download ai.txt", gen['ai_txt'], "ai.txt")
        with c3: st.download_button("Download robots.txt", gen['robots_txt'], "robots.txt")

