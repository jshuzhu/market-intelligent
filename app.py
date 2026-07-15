"""
Market Intelligence & B2B Lead Scraper
Streamlit Dashboard - Main Application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)

# ---------- Page Config ----------
st.set_page_config(
    page_title="Market Intelligence 🦀",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Load Environment ----------
load_dotenv()

# ---------- Init Session State ----------
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = os.getenv("GEMINI_API_KEY", "")
if "supabase_url" not in st.session_state:
    st.session_state.supabase_url = os.getenv("SUPABASE_URL", "")
if "supabase_key" not in st.session_state:
    st.session_state.supabase_key = os.getenv("SUPABASE_KEY", "")

# ---------- Sidebar Navigation ----------
st.sidebar.image("https://img.icons8.com/fluency/96/crab.png", width=60)
st.sidebar.title("KetamPandai ⚡")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📈 Trend Analyzer", "💼 Lead Generator", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Tech Stack:** Streamlit · Gemini · Supabase · GitHub")

# ================================================================
# PAGE: HOME
# ================================================================
if page == "🏠 Home":
    st.title("🦀 Market Intelligence & B2B Lead Scraper")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Trend Analyzer")
        st.markdown(
            """
            **For:** `digitalcanvasmy` — Graphic Design Merchandise
            
            Track trending themes for:
            - Stickers & Decals
            - Enamel Pins
            - Art Prints / Posters
            
            *Scrapes Reddit, X/Twitter, and e-commerce reviews.*
            *Uses Gemini Flash Free Tier to summarize trends.*
            """
        )

    with col2:
        st.markdown("### 💼 Lead Generator")
        st.markdown(
            """
            **For:** Web System Development Services
            
            Find businesses that need:
            - Modern websites
            - POS / inventory systems
            - Digital presence upgrades
            
            *Scrapes Google Maps, directories, and evaluates
            website quality via Gemini Flash.*
            """
        )

    st.markdown("---")
    st.info(
        "💡 **How to start:** Go to **Settings** → paste your Gemini API Key & "
        "Supabase credentials → then run a module!"
    )

    # --- Recent Activity from DB ---
    if st.session_state.supabase_url and st.session_state.supabase_key:
        try:
            from utils.supabase_client import Database
            db = Database(st.session_state.supabase_url, st.session_state.supabase_key)

            recent = db.get_trends(limit=5)
            if recent:
                st.markdown("### 📋 Recent Analyses")
                for t in recent[:5]:
                    st.markdown(
                        f"- **{t['theme']}** ({t['niche']}) — Score: {t['score']} "
                        f"— {t['created_at'][:10] if t.get('created_at') else ''}"
                    )
        except Exception:
            pass

# ================================================================
# PAGE: TREND ANALYZER
# ================================================================
elif page == "📈 Trend Analyzer":
    st.title("📈 Trend Analyzer")
    st.caption("Discover trending merchandise themes — no crystal ball needed.")

    # --- API check ---
    if not st.session_state.gemini_key:
        st.warning("⚠️ Gemini API key not set. Go to **Settings** to configure it first.")
    else:
        st.success("✅ Gemini API configured")

    # --- Input Section ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Target Niche")
        niche = st.selectbox(
            "What are you designing for?",
            ["Stickers / Decals", "Enamel Pins", "Art Prints / Posters",
             "T-shirt / Apparel", "Other"]
        )
        if niche == "Other":
            custom_niche = st.text_input("Enter your niche:")

    with col2:
        st.subheader("📅 Timeframe")
        timeframe = st.select_slider(
            "Look back period",
            options=["7 days", "30 days", "90 days"],
            value="30 days"
        )

    # --- Data Sources ---
    st.subheader("📡 Data Sources")
    src_cols = st.columns(4)
    with src_cols[0]:
        reddit = st.checkbox("Reddit", value=True)
    with src_cols[1]:
        twitter = st.checkbox("X / Twitter", value=False)
    with src_cols[2]:
        ecom = st.checkbox("E-commerce Reviews", value=False)
    with src_cols[3]:
        pinterest = st.checkbox("Pinterest", value=False)

    # --- Run Button ---
    st.markdown("---")
    run_btn = st.button("🚀 Run Trend Analysis", type="primary", use_container_width=True)

    # --- Timeframe mapping ---
    tf_map = {"7 days": "week", "30 days": "month", "90 days": "all"}

    # --- Run Button ---
    st.markdown("---")
    run_btn = st.button("🚀 Run Trend Analysis", type="primary", use_container_width=True)

    if run_btn:
        if not st.session_state.gemini_key:
            st.error("Set your Gemini API key in Settings first!")
        else:
            actual_niche = custom_niche if niche == "Other" else niche
            with st.spinner("🕷️ Scraping Reddit & analyzing with Gemini..."):
                try:
                    from utils.trend_pipeline import TrendPipeline

                    pipeline = TrendPipeline(
                        gemini_key=st.session_state.gemini_key,
                        supabase_url=st.session_state.supabase_url,
                        supabase_key=st.session_state.supabase_key
                    )

                    results = pipeline.run(
                        niche=actual_niche,
                        use_reddit=reddit,
                        use_twitter=twitter,
                        use_ecommerce=ecom,
                        timeframe=tf_map.get(timeframe, "month"),
                    )

                    st.session_state["last_results"] = results
                    st.session_state["last_niche"] = actual_niche
                    st.session_state["results_time"] = datetime.now()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
                    logging.exception("Trend analysis error")

    # --- Results Display ---
    st.markdown("### 📊 Results")
    result_tab1, result_tab2, result_tab3 = st.tabs([
        "Trending Themes", "Keyword Cloud", "Raw Data"
    ])

    with result_tab1:
        if "last_results" in st.session_state:
            res = st.session_state["last_results"]
            themes = res.get("themes", [])
            stats = res.get("source_stats", {})

            # Source stats
            cols = st.columns(3)
            with cols[0]:
                st.metric("Reddit posts", stats.get("reddit", 0))
            with cols[1]:
                st.metric("Texts analyzed", res.get("total_texts_analyzed", 0))
            with cols[2]:
                st.metric("Saved to DB", res.get("saved_to_db", 0))

            if themes and themes[0].get("theme") not in ["No data", "Error", "Parse Error"]:
                # Build theme cards
                for i, theme in enumerate(themes, 1):
                    score = theme.get("score", 0)
                    color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

                    with st.container(border=True):
                        tcols = st.columns([1, 4, 1])
                        with tcols[0]:
                            st.markdown(f"### {color}")
                        with tcols[1]:
                            st.markdown(f"**{i}. {theme.get('theme', 'Unknown')}**")
                            st.caption(theme.get("description", ""))
                        with tcols[2]:
                            st.markdown(f"## {score}")
                            st.caption("/100")

                        keywords = theme.get("keywords", [])
                        if keywords:
                            st.markdown(" ".join([
                                f"`{k}`" for k in keywords
                            ]))

                # Bar chart
                st.markdown("---")
                st.subheader("📈 Trend Score Overview")
                df = pd.DataFrame(themes)
                if not df.empty and "score" in df.columns:
                    df = df.sort_values("score", ascending=True)
                    fig = px.bar(
                        df, y="theme", x="score",
                        orientation="h",
                        color="score",
                        color_continuous_scale="Viridis",
                        labels={"theme": "", "score": "Trend Score"}
                    )
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("No trends found. Try a different niche or enable more sources.")
        else:
            st.info("Run analysis to see trending themes here.")

    with result_tab2:
        if "last_results" in st.session_state:
            kws = st.session_state["last_results"].get("keywords", [])
            if kws:
                kw_df = pd.DataFrame({"keyword": kws, "count": [len(k) for k in kws]})
                fig = px.treemap(kw_df, path=["keyword"], values="count",
                                  title="Trending Keywords")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No keywords extracted.")
        else:
            st.info("Keyword visualization will appear here.")

    with result_tab3:
        if "last_results" in st.session_state:
            st.json(st.session_state["last_results"])
        else:
            st.info("Scraped data preview will appear here.")

# ================================================================
# PAGE: LEAD GENERATOR
# ================================================================
elif page == "💼 Lead Generator":
    st.title("💼 B2B Lead Generator")
    st.caption("Find businesses that need your web dev wizardry.")

    # --- API check ---
    if not st.session_state.gemini_key:
        st.warning("⚠️ Gemini API key not set. Go to **Settings** to configure it first.")
    else:
        st.success("✅ Gemini API configured")

    # --- Input Section ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 Target Area")
        location = st.text_input("City / Area", "Kuala Lumpur")

        st.subheader("🏢 Business Types")
        biz_types = st.multiselect(
            "Select industries",
            ["Cafe & Coffee Shop", "Restaurant", "Retail Shop", "Creative Studio",
             "Vendor / Supplier", "Salon & Spa", "Gym & Fitness", "Other"],
            default=["Cafe & Coffee Shop", "Creative Studio"]
        )

    with col2:
        st.subheader("⚙️ Limits")
        max_leads = st.slider("Max leads to scrape", 10, 200, 50)
        min_rating = st.slider("Min rating (Google)", 1.0, 5.0, 3.5, 0.5)

    # --- Run Button ---
    st.markdown("---")
    run_btn = st.button("🚀 Generate Leads", type="primary", use_container_width=True)

    if run_btn:
        if not st.session_state.gemini_key:
            st.error("Set your Gemini API key in Settings first!")
        else:
            with st.spinner("Scraping Google Maps & evaluating websites..."):
                # TODO: Phase 4-5 - Implement scraping + AI pipeline
                st.info("Lead generation engine coming in Phase 4 🛠️")

    # --- Results Placeholder ---
    st.markdown("### 📋 Leads Table")
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        st.selectbox("Filter by", ["All", "Has Website", "No Website", "Needs Improvement"])
    with col_filter2:
        st.number_input("Min score", 0, 100, 50)
    with col_filter3:
        st.text_input("Search", placeholder="Business name...")

    st.info("Run lead generation to see results here.")

    # --- Export ---
    st.download_button(
        label="📥 Export as CSV",
        data="",
        file_name="leads.csv",
        mime="text/csv",
        disabled=True
    )

# ================================================================
# PAGE: SETTINGS
# ================================================================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.markdown("Configure your API keys and database connection.")

    with st.form("settings_form"):
        st.subheader("🔑 API Keys")

        gemini_key = st.text_input(
            "Gemini API Key (Free Tier)",
            type="password",
            value=st.session_state.gemini_key,
            help="Get your key: https://aistudio.google.com/app/apikey"
        )

        st.markdown("---")
        st.subheader("🗄️ Supabase (Database)")

        supabase_url = st.text_input(
            "Supabase Project URL",
            value=st.session_state.supabase_url
        )
        supabase_key = st.text_input(
            "Supabase Anon / Service Key",
            type="password",
            value=st.session_state.supabase_key
        )

        st.markdown("---")
        saved = st.form_submit_button("💾 Save Settings", type="primary")

        if saved:
            st.session_state.gemini_key = gemini_key
            st.session_state.supabase_url = supabase_url
            st.session_state.supabase_key = supabase_key
            st.success("Settings saved for this session!")

    # --- Connection Test ---
    st.markdown("---")
    st.subheader("🧪 Connection Test")
    if st.button("Test Supabase Connection"):
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                client = create_client(supabase_url, supabase_key)
                client.table("_dummy").select("*").limit(1).execute()
                st.success("✅ Supabase connection OK!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
        else:
            st.warning("Enter Supabase URL and key first.")
