"""
Market Intelligence Dashboard — Visual-First UI
Scrapes: Reddit, Etsy, Instagram, TikTok, Shopee, Facebook
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv()

# ---------- Config ----------
st.set_page_config(
    page_title="Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Session State ----------
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = os.getenv("GEMINI_API_KEY", "")
if "supabase_url" not in st.session_state:
    st.session_state.supabase_url = os.getenv("SUPABASE_URL", "")
if "supabase_key" not in st.session_state:
    st.session_state.supabase_key = os.getenv("SUPABASE_KEY", "")
if "results" not in st.session_state:
    st.session_state.results = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------- Color Palette ----------
COLORS = {
    "reddit": "#FF4500",
    "etsy": "#F56400",
    "instagram": "#E4405F",
    "tiktok": "#000000",
    "shopee": "#EE4D2D",
    "facebook": "#1877F2",
}

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🦀 KetamPandai")
    st.markdown("Market Intelligence")
    st.divider()

    page = st.radio(
        "Menu",
        ["📊 Dashboard", "🔍 Trend Analyzer", "💼 Lead Generator", "⚙️ Settings"]
    )

    st.divider()
    
    # Source legend
    st.markdown("### Data Sources")
    for name, color in COLORS.items():
        st.markdown(f"<span style='color:{color}'>⬤</span> {name.title()}", unsafe_allow_html=True)

    st.divider()
    st.caption("Built with Streamlit · Gemini · Supabase")

# ================================================================
# DASHBOARD PAGE
# ================================================================
if page == "📊 Dashboard":
    st.title("📊 Market Intelligence Dashboard")
    
    # Row 1: KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sources Active", "2/6", "Reddit, Etsy")
    with col2:
        st.metric("Trends Tracked", "5", "+3 today")
    with col3:
        st.metric("Leads Collected", "0", "Run Lead Gen")
    with col4:
        st.metric("API Budget", "Free ✅", "Gemini Flash Lite")

    # Row 2: Two charts side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📡 Data Distribution")
        # Sample pie chart for demo
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Reddit", "Etsy", "Instagram", "TikTok", "Shopee"],
            values=[100, 45, 30, 20, 10],
            marker=dict(colors=[COLORS[s] for s in ["reddit","etsy","instagram","tiktok","shopee"]]),
            hole=0.4,
            textinfo="label+percent",
        )])
        fig_pie.update_layout(height=300, margin=dict(t=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("🏆 Top Trending Themes")
        sample_df = pd.DataFrame({
            "Theme": ["Cyberpunk Neon", "Kawaii Aesthetic", "Minimalist Line Art",
                     "Y2K Revival", "Dark Academia"],
            "Score": [92, 88, 76, 71, 65],
            "Source": ["Reddit/Etsy", "Instagram/TikTok", "Etsy", "TikTok", "Reddit"],
        })
        fig_bar = px.bar(
            sample_df, x="Score", y="Theme",
            orientation="h", color="Score",
            color_continuous_scale="viridis",
            text="Score",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(height=300, margin=dict(t=0, b=0), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Row 3: Recent trends
    st.divider()
    st.subheader("📋 Recent Trend Analyses")
    if st.session_state.supabase_url and st.session_state.supabase_key:
        try:
            from utils.supabase_client import Database
            db = Database(st.session_state.supabase_url, st.session_state.supabase_key)
            recent = db.get_trends(limit=10)
            if recent:
                df = pd.DataFrame(recent)
                st.dataframe(
                    df[["theme", "niche", "score", "created_at"]].rename(
                        columns={"theme": "Theme", "niche": "Niche",
                                 "score": "Score", "created_at": "Date"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No data yet. Run Trend Analyzer first!")
        except Exception as e:
            st.info(f"Connect Supabase in Settings to see history. ({e})")
    else:
        st.info("Connect Supabase in Settings to see saved data.")

# ================================================================
# TREND ANALYZER
# ================================================================
elif page == "🔍 Trend Analyzer":
    st.title("🔍 Trend Analyzer")
    st.caption("Scrape, analyze, and visualize design trends from across the web.")

    # --- API Check ---
    if not st.session_state.gemini_key:
        st.warning("⚠️ Set your Gemini API key in Settings first.")
    
    # --- Input Row ---
    col1, col2, col3 = st.columns(3)
    with col1:
        niche = st.selectbox(
            "What are you designing?",
            ["Stickers / Decals", "Enamel Pins", "Art Prints", "T-shirt / Apparel",
             "Phone Cases", "Jewelry", "Other"]
        )
        custom_niche = st.text_input("Custom niche") if niche == "Other" else None
    with col2:
        timeframe = st.select_slider(
            "Time range", options=["7 days", "30 days", "90 days"], value="30 days"
        )
    with col3:
        max_themes = st.slider("Max themes", 3, 15, 8)

    # --- Source Selectors ---
    st.divider()
    st.markdown("### 🌐 Select Data Sources")

    src_cols = st.columns(6)
    with src_cols[0]:
        src_reddit = st.checkbox("Reddit", value=True)
    with src_cols[1]:
        src_etsy = st.checkbox("Etsy", value=False)
    with src_cols[2]:
        src_instagram = st.checkbox("Instagram", value=False)
    with src_cols[3]:
        src_tiktok = st.checkbox("TikTok", value=False)
    with src_cols[4]:
        src_shopee = st.checkbox("Shopee", value=False)
    with src_cols[5]:
        src_facebook = st.checkbox("Facebook", value=False)

    # --- Run Button ---
    st.divider()
    run = st.button("🚀 RUN ANALYSIS", type="primary", use_container_width=True)

    if run:
        if not st.session_state.gemini_key:
            st.error("Set your Gemini API key first!")
        else:
            active_niche = custom_niche if niche == "Other" else niche
            tf_map = {"7 days": "week", "30 days": "month", "90 days": "all"}

            with st.spinner(f"🕷️ Scraping {active_niche} trends..."):
                try:
                    from utils.trend_pipeline import TrendPipeline
                    pipeline = TrendPipeline(
                        gemini_key=st.session_state.gemini_key,
                        supabase_url=st.session_state.supabase_url,
                        supabase_key=st.session_state.supabase_key,
                    )

                    results = pipeline.run(
                        niche=active_niche,
                        use_reddit=src_reddit,
                        use_etsy=src_etsy,
                        use_instagram=src_instagram,
                        use_tiktok=src_tiktok,
                        use_shopee=src_shopee,
                        timeframe=tf_map.get(timeframe, "month"),
                        max_themes=max_themes,
                    )
                    st.session_state.results = results
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ {e}")

    # --- Results Display ---
    if st.session_state.results:
        res = st.session_state.results
        themes = res.get("themes", [])
        keywords = res.get("keywords", [])
        stats = res.get("source_stats", {})

        st.divider()
        st.markdown(f"### 📊 Results for: {res.get('niche', 'N/A')}")

        # Row: KPI cards
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Texts Analyzed", res.get("total_texts_analyzed", 0))
        with k2:
            st.metric("Sources Scraped", sum(1 for v in stats.values() if v > 0))
        with k3:
            st.metric("Themes Found", len(themes))
        with k4:
            st.metric("Saved to DB", res.get("saved_to_db", 0))

        # Row: Charts
        col1, col2 = st.columns(2)

        with col1:
            # Source pie
            if stats:
                src_labels = [k.title() for k, v in stats.items() if v > 0]
                src_values = [v for v in stats.values() if v > 0]
                src_colors_list = [COLORS.get(k, "#666") for k, v in stats.items() if v > 0]
                
                fig = go.Figure(data=[go.Pie(
                    labels=src_labels, values=src_values,
                    marker=dict(colors=src_colors_list),
                    hole=0.4, textinfo="label+value",
                )])
                fig.update_layout(title="Data by Source", height=300)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Themes bar chart
            if themes and themes[0].get("theme") not in ["No data", "Error"]:
                df = pd.DataFrame(themes).sort_values("score")
                fig = px.bar(
                    df, x="score", y="theme",
                    orientation="h", color="score",
                    color_continuous_scale="viridis",
                    text="score",
                    labels={"score": "Trend Score", "theme": ""},
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(title="Trend Scores", height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        # Theme cards
        st.divider()
        st.subheader("🏆 Trending Themes")

        if themes and themes[0].get("theme") not in ["No data", "Error", "Parse Error"]:
            for i, t in enumerate(themes, 1):
                score = t.get("score", 0)
                if score >= 70:
                    badge = "🟢 HOT"
                elif score >= 40:
                    badge = "🟡 WARM"
                else:
                    badge = "🔴 NICHE"

                with st.container(border=True):
                    cols = st.columns([1, 5, 1, 1])
                    with cols[0]:
                        st.markdown(f"### {i}")
                    with cols[1]:
                        st.markdown(f"**{t.get('theme', '')}**")
                        st.caption(t.get("description", "")[:150])
                    with cols[2]:
                        st.markdown(f"### {score}")
                        st.caption("/100")
                    with cols[3]:
                        st.markdown(f"`{badge}`")

                    kw = t.get("keywords", [])
                    if kw:
                        st.markdown(" ".join([f"`{k}`" for k in kw]))
        else:
            st.info("No trends found. Try enabling more sources or a different niche.")

        # Keyword cloud
        if keywords:
            st.divider()
            st.subheader("☁️ Keyword Cloud")
            kw_df = pd.DataFrame({"keyword": keywords, "freq": [len(k) for k in keywords]})
            fig = px.treemap(kw_df, path=["keyword"], values="freq", title="Trending Keywords")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Run an analysis to see results here. Charts and graphs will appear automatically.")

# ================================================================
# LEAD GENERATOR (placeholder)
# ================================================================
elif page == "💼 Lead Generator":
    st.title("💼 B2B Lead Generator")
    st.info("🚧 Lead Generator module coming in Phase 3 — after UI revamp is approved.")

# ================================================================
# SETTINGS
# ================================================================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    with st.form("settings"):
        st.subheader("🔑 API Keys")
        gemini = st.text_input("Gemini API Key", type="password", value=st.session_state.gemini_key)

        st.subheader("🗄️ Supabase")
        su_url = st.text_input("Project URL", value=st.session_state.supabase_url)
        su_key = st.text_input("Anon Key", type="password", value=st.session_state.supabase_key)

        if st.form_submit_button("💾 Save", type="primary"):
            st.session_state.gemini_key = gemini
            st.session_state.supabase_url = su_url
            st.session_state.supabase_key = su_key
            st.success("Saved!")

    st.divider()
    if st.button("🔌 Test Supabase"):
        try:
            from supabase import create_client
            c = create_client(st.session_state.supabase_url, st.session_state.supabase_key)
            c.table("_dummy").select("*").limit(1).execute()
            st.success("✅ Connected!")
        except Exception as e:
            st.error(f"❌ {e}")
