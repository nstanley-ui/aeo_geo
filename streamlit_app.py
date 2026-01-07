# --- SECTION 3: INFRASTRUCTURE & OPTIMIZATION ---
    st.subheader("📄 Infrastructure & Optimization")
    
    # Context Banner
    st.info("💡 **Why Optimize?** Even if files exist, they may be graded 'Poor' or 'Average' if they lack specific agent instructions. Our generator upgrades them to 'Great' standards.")

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
    
    # Grade Color Mapping
    grade_map = {
        "Great": "green",
        "Good": "blue", 
        "Average": "orange",
        "Poor": "red",
        "Missing": "red"
    }
    
    for idx, (f_key, f_display_default) in enumerate(file_map.items()):
        with file_cols[idx]:
            # Data Extraction
            file_info = data['aeo'].get(f_key, {})
            f_name = file_info.get('filename', f_display_default)
            exists = file_info.get('exists', False)
            grade = file_info.get('grade', 'Missing')
            manual_url = get_file_url(st.session_state.domain, f_name)
            color = grade_map.get(grade, "gray")
            
            # Card Container
            with st.container(border=True):
                # 1. Header & Quality Grade
                st.markdown(f"#### {f_name}")
                
                # The Quality Badge
                if exists:
                    st.markdown(f":{color}-background[**Grade: {grade}**]")
                else:
                    st.markdown(f":red-background[**Status: Missing**]")
                
                # Contextual verification link
                st.markdown(f"<div style='font-size: 0.8rem; margin-top: 5px;'><a href='{manual_url}' target='_blank' style='text-decoration:none;'>🔗 Verify Live Link</a></div>", unsafe_allow_html=True)
                
                # 2. Divider ("Current vs Optimized")
                st.markdown("---")
                
                # 3. Optimization Action
                if st.session_state.generated_files:
                    # If files are generated, show the specific download button
                    file_content = st.session_state.generated_files.get(f_key, "") 
                    if not file_content and f_key == 'llm_txt': file_content = st.session_state.generated_files.get('llm_txt', "")

                    if file_content:
                        # Smart Labeling
                        if grade == "Great":
                            btn_label = "⬇️ Download (No Changes Needed)"
                            btn_type = "secondary"
                        elif exists:
                            btn_label = f"✨ Upgrade to 'Great'"
                            btn_type = "primary"
                        else:
                            btn_label = "✨ Create New File"
                            btn_type = "primary"
                            
                        st.download_button(
                            label=btn_label,
                            data=file_content,
                            file_name=f_name,
                            mime="text/plain",
                            use_container_width=True,
                            type=btn_type
                        )
                    else:
                        st.warning("Could not generate.")
                else:
                    # Placeholder state
                    st.button("Waiting for generator...", disabled=True, key=f"placeholder_{idx}", use_container_width=True)True)




