import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
from execution.check_aeo import check_domain
from execution.check_socials import audit_socials
from execution.check_competitors import check_competitors
from execution.crawl_site import crawl_domain

# Page Configuration
st.set_page_config(page_title="Mojo AEO Checker", page_icon="🚀", layout="wide")

# Custom CSS for "Glassmorphic" feel
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        color: #f8fafc;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🚀 Mojo AEO Checker")
st.markdown("### Visibility analysis for the AI Agent Economy")

# Sidebar
st.sidebar.header("Configuration")
domain = st.sidebar.text_input("Target Domain", "ironhorse.io")
run_btn = st.sidebar.button("Run Audit", type="primary")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Domain Audit", "⚙️ File Generator", "⚔️ Competitors"])

if run_btn:
    with st.spinner(f"Analyzing {domain}..."):
        # Run Audits
        aeo_data = check_domain(domain)
        social_data = audit_socials(domain)
        
        # Calculate Overall Score
        overall_score = (aeo_data.get("aeo_score", 0) + social_data.get("overall_social_score", 0)) // 2

    # --- TAB 1: AUDIT ---
    with tab1:
        # Score Section
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Overall Mojo Score", f"{overall_score}/100")
            
            # Radar Chart
            categories = ['AEO Score', 'Social Score', 'LinkedIn', 'Crunchbase', 'Reddit']
            values = [
                aeo_data.get("aeo_score", 0),
                social_data.get("overall_social_score", 0),
                social_data['platforms'][0]['score'],
                social_data['platforms'][1]['score'],
                social_data['platforms'][2]['score']
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line_color='#6366f1'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Agent Infrastructure")
            
            # File Checks
            files = ["llm_txt", "ai_txt", "robots_txt"]
            for f in files:
                data = aeo_data.get(f, {})
                grade = data.get("grade", "N/A")
                color = "green" if grade == "Great" else "orange" if grade == "Average" else "red"
                
                with st.expander(f"📄 {f.replace('_', '.')} - :{color}[{grade}]"):
                    st.write(f"**Status:** {'Found' if data.get('exists') else 'Missing'}")
                    st.write(f"**Grade:** {grade}")
                    if data.get('content'):
                        st.code(data['content'], language='text')
            
            # Advanced Checks
            st.subheader("Advanced Content Signals")
            adv_cols = st.columns(2)
            for idx, (key, val) in enumerate(aeo_data.get("advanced_checks", {}).items()):
                with adv_cols[idx % 2]:
                    st.info(f"**{key.replace('_', ' ').title()}**: {val['detail']}")

    # --- TAB 2: GENERATOR ---
    with tab2:
        st.header("Generate Optimized Files")
        if st.button("Generate Files"):
            with st.spinner("Crawling site..."):
                gen_files = crawl_domain(domain)
                
            st.success(f"Crawled {gen_files['analysis']['pages_crawled']} pages")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("Download llm.txt", gen_files['llm_txt'], "llm.txt")
                st.code(gen_files['llm_txt'], language="markdown")
            with c2:
                st.download_button("Download ai.txt", gen_files['ai_txt'], "ai.txt")
                st.code(gen_files['ai_txt'], language="text")
            with c3:
                st.download_button("Download robots.txt", gen_files['robots_txt'], "robots.txt")
                st.code(gen_files['robots_txt'], language="text")

    # --- TAB 3: COMPETITORS ---
    with tab3:
        st.header("Competitor Benchmarking")
        comp_data = check_competitors(domain)
        
        df = pd.DataFrame(comp_data['competitors'])
        st.bar_chart(df.set_index('name')['score'])
        st.table(df)

else:
    with tab1:
        st.info("👈 Enter a domain and click 'Run Audit' to start.")