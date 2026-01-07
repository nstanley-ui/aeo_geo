# --- SECTION 3: INFRASTRUCTURE & OPTIMIZATION ---
    st.subheader("📄 Infrastructure & Optimization")
    
    # Context Banner
    st.info("💡 **Why Optimize?** Even if these files exist, they often lack specific instructions for AI Agents (e.g., attribution rules or 'Answer-First' formatting). Our generator builds improved versions based on your actual content.")

    # Master Generator Button
    col_gen_action, col_gen_info = st.columns([1, 2])
    with col_gen_action:
        if st.button("✨ Generate Optimized Assets", type="primary", use_container_width=True):
            with st.spinner("Crawling site structure and content..."):
                st.session_state.generated_files = crawl_domain(st.session_state.domain)
                st.rerun()
    with col_gen_info:
        if st.session_state.generated_files:
            st.success("✅ Optimization complete! Download your upgraded files below.")
        else:
            st.caption("Click to scan your site and build AI-ready versions of llms.txt, ai.txt, and robots.txt.")

    st.markdown("---")

    # The Cards (Status + Action Combined)
    file_map = {"llm_txt": "llms.txt", "ai_txt": "ai.txt", "robots_txt": "robots.txt"}
    file_cols = st.columns(3)
    
    for idx, (f_key, f_display_default) in enumerate(file_map.items()):
        with file_cols[idx]:
            # Data Extraction
            file_info = data['aeo'].get(f_key, {})
            f_name = file_info.get('filename', f_display_default)
            exists = file_info.get('exists', False)
            manual_url = get_file_url(st.session_state.domain, f_name)
            
            # Card Container
            with st.container():
                # 1. Header & Status
                st.markdown(f"#### {f_name}")
                if exists:
                    st.markdown(f":green-background[Found] &nbsp; [Verify Live Link 🔗]({manual_url})")
                else:
                    st.markdown(f":red-background[Missing] &nbsp; [Verify Live Link 🔗]({manual_url})")
                
                st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True) # Spacer

                # 2. Optimization Action
                if st.session_state.generated_files:
                    # If files are generated, show the specific download button
                    file_content = st.session_state.generated_files.get(f_key, "") # Note: generator keys match check_aeo keys
                    
                    # Special handling if key mismatch occurs in generator vs checker
                    if not file_content and f_key == 'llm_txt': file_content = st.session_state.generated_files.get('llm_txt', "")

                    if file_content:
                        btn_label = "⬇️ Download Improved Version" if exists else "⬇️ Download New File"
                        st.download_button(
                            label=btn_label,
                            data=file_content,
                            file_name=f_name,
                            mime="text/plain",
                            use_container_width=True
                        )
                    else:
                        st.warning("Could not generate.")
                else:
                    # Placeholder state
                    st.button("Waiting for generator...", disabled=True, key=f"placeholder_{idx}", use_container_width=True)

