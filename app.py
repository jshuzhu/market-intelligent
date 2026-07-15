"""
Market Intelligence & B2B Lead Scraper
Streamlit Dashboard - Main Application
"""
import streamlit as st
from dotenv import load_dotenv
import os

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

    if run_btn:
        if not st.session_state.gemini_key:
            st.error("Set your Gemini API key in Settings first!")
        else:
            with st.spinner("Scraping sources & analyzing trends..."):
                # TODO: Phase 2 - Implement scraping + Gemini pipeline
                st.info("Analysis engine coming in Phase 2 🛠️")

    # --- Results Placeholder ---
    st.markdown("### 📊 Results")
    result_tab1, result_tab2, result_tab3 = st.tabs(["Trending Themes", "Keyword Cloud", "Raw Data"])
    with result_tab1:
        st.info("Run analysis to see trending themes here.")
    with result_tab2:
        st.info("Keyword visualization will appear here.")
    with result_tab3:
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
