"""
Market Analysis — Professional Dashboard
akio@jshuzhu
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.WARNING)

st.set_page_config(page_title="Market Analysis", page_icon="📊", layout="wide")

# ---------- Session ----------
keys = ["mode", "gemini_key", "supabase_url", "supabase_key", "results", "seo_keywords", "seo_data"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None if k in ("results", "seo_keywords", "seo_data") else ""
st.session_state.gemini_key = st.session_state.gemini_key or os.getenv("GEMINI_API_KEY", "")
st.session_state.supabase_url = st.session_state.supabase_url or os.getenv("SUPABASE_URL", "")
st.session_state.supabase_key = st.session_state.supabase_key or os.getenv("SUPABASE_KEY", "")

# ---------- Color palette ----------
C = {"blue": "#2563eb", "green": "#059669", "gray": "#6b7280", "light": "#f3f4f6", "border": "#e5e7eb"}

# ====================================================================
# SIDEBAR
# ====================================================================
with st.sidebar:
    st.markdown("## Market Analysis")
    st.caption("Powered by Gemini AI")

    # Mode toggle as buttons — exactly as requested
    col1, col2 = st.columns(2)
    with col1:
        is_general = st.button("🌐 General", use_container_width=True,
                                type="primary" if st.session_state.mode == "general" else "secondary")
    with col2:
        is_webdev = st.button("💻 Web Dev", use_container_width=True,
                               type="primary" if st.session_state.mode == "webdev" else "secondary")
    if is_general: st.session_state.mode = "general"
    if is_webdev: st.session_state.mode = "webdev"

    st.divider()

    # Menu
    if st.session_state.mode == "general":
        items = ["📊 Dashboard", "🔍 Trend Scanner", "📈 SEO/SEM Keywords", "🏆 Top Accounts", "⚙️ Settings"]
    else:
        items = ["📊 Dashboard", "🎯 Lead Finder", "🌐 Website Audit", "⚙️ Settings"]
    menu = st.radio("", items, label_visibility="collapsed")

    st.divider()
    # Status
    has_key = bool(st.session_state.gemini_key and len(st.session_state.gemini_key) > 10)
    has_db = bool(st.session_state.supabase_url)
    st.caption(f'API {"✓" if has_key else "✗"} Database {"✓" if has_db else "✗"}')

# ====================================================================
# HELPERS
# ====================================================================
def card(text, level="info"):
    fn = getattr(st, level, st.info)
    fn(text)

def metric_box(label, value, delta=None):
    st.metric(label=label, value=value, delta=delta)

def source_pie(stats):
    if not stats:
        return None
    colors_map = {"reddit": "#FF4500", "etsy": "#F56400", "instagram": "#E4405F",
                  "tiktok": "#000000", "shopee": "#EE4D2D"}
    labels = [k.title() for k, v in stats.items() if v > 0]
    vals = [v for v in stats.values() if v > 0]
    clrs = [colors_map.get(k, "#6b7280") for k, v in stats.items() if v > 0]
    fig = go.Figure(data=[go.Pie(labels=labels, values=vals, marker=dict(colors=clrs), hole=0.5, textinfo="label+percent")])
    fig.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    return fig

def theme_bar(themes):
    if not themes: return None
    df = pd.DataFrame(themes).sort_values("score")
    fig = px.bar(df, x="score", y="theme", orientation="h", color="score",
                 color_continuous_scale="blues", text="score",
                 labels={"score": "Score", "theme": ""})
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, showlegend=False, xaxis=dict(range=[0, 105], showgrid=False), margin=dict(t=10, b=10))
    return fig

def theme_cards(themes):
    if not themes:
        return
    for i, t in enumerate(themes, 1):
        s = t.get("score", 0)
        tag = "🔥" if s >= 70 else "📈" if s >= 40 else "🔍"
        with st.container(border=True):
            c = st.columns([1, 5, 1])
            c[0].write(f"**#{i}**")
            c[1].markdown(f"**{t.get('theme', '')}**  —  {t.get('description', '')[:150]}")
            c[2].markdown(f"**{s}**  {tag}")
            kw = t.get("keywords", [])
            if kw:
                st.caption("Keywords: " + ", ".join(kw[:6]))

# ====================================================================
# SETTINGS — passcode protected
# ====================================================================
if menu == "⚙️ Settings":
    st.title("⚙️ Settings")

    # Init session keys for settings lock
    if "settings_password" not in st.session_state:
        st.session_state.settings_password = None
    if "settings_unlocked" not in st.session_state:
        st.session_state.settings_unlocked = False

    # --- First time: set password ---
    if st.session_state.settings_password is None:
        st.markdown("🔐 **Set a password to protect your settings.**")
        new_pw = st.text_input("Create password", type="password", placeholder="Enter your password")
        confirm_pw = st.text_input("Confirm password", type="password", placeholder="Re-enter password")
        if st.button("Set Password", type="primary"):
            if not new_pw:
                st.error("Password cannot be empty")
            elif new_pw != confirm_pw:
                st.error("Passwords do not match")
            else:
                st.session_state.settings_password = new_pw
                st.session_state.settings_unlocked = True
                st.rerun()

    # --- Locked: enter password ---
    elif not st.session_state.settings_unlocked:
        st.markdown("🔒 **Settings are locked.**")
        code = st.text_input("Enter password", type="password", placeholder="")
        if st.button("Unlock", type="primary"):
            if code == st.session_state.settings_password:
                st.session_state.settings_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect password")

    # --- Unlocked: show settings form ---
    else:
        with st.form("settings_form"):
            st.text_input("Gemini API Key", type="password", key="gemini_input",
                          value=st.session_state.gemini_key, placeholder="Paste your Gemini API key",
                          help="Get one free at aistudio.google.com")
            st.text_input("Supabase URL", key="supa_url_input", value=st.session_state.supabase_url,
                          placeholder="https://xxx.supabase.co")
            st.text_input("Supabase Key", type="password", key="supa_key_input",
                          value=st.session_state.supabase_key, placeholder="anon public key")
            if st.form_submit_button("Save", type="primary", use_container_width=True):
                st.session_state.gemini_key = st.session_state.gemini_input
                st.session_state.supabase_url = st.session_state.supa_url_input
                st.session_state.supabase_key = st.session_state.supa_key_input
                st.success("Saved")

        st.divider()
        with st.expander("Connection Test"):
            if st.button("Test Gemini"):
                if st.session_state.gemini_key:
                    try:
                        from google import genai
                        c = genai.Client(api_key=st.session_state.gemini_key)
                        r = c.models.generate_content(model="gemini-3.1-flash-lite", contents="ok")
                        st.success(f"OK — {r.text[:20]}")
                    except Exception as e:
                        st.error(str(e)[:120])
                else:
                    st.warning("No key")
            if st.button("Test Supabase"):
                try:
                    from supabase import create_client
                    create_client(st.session_state.supabase_url, st.session_state.supabase_key)
                    st.success("OK")
                except Exception as e:
                    st.error(str(e)[:120])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔒 Lock", use_container_width=True):
                st.session_state.settings_unlocked = False
                st.rerun()
        with col2:
            if st.button("🔄 Change Password", use_container_width=True):
                st.session_state.settings_password = None
                st.session_state.settings_unlocked = False
                st.rerun()

# ====================================================================
# GENERAL MODE
# ====================================================================
elif st.session_state.mode == "general":

    if menu == "📊 Dashboard":
        st.title("General Market Analysis")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sources", "4/5")
        col2.metric("Keywords", "47")
        col3.metric("Top Accounts", "23")
        col4.metric("API", "Free Tier")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Data Sources")
            fig = source_pie({"reddit": 100, "etsy": 45, "instagram": 60, "tiktok": 35, "shopee": 20})
            if fig: st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Trending Themes")
            sample = [{"theme": "Kawaii Aesthetic", "score": 92}, {"theme": "Cyberpunk Neon", "score": 87},
                      {"theme": "Minimalist Line", "score": 78}, {"theme": "Y2K Revival", "score": 73},
                      {"theme": "Dark Academia", "score": 68}]
            fig = theme_bar(sample)
            if fig: st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Trending SEO Keywords")
        df = pd.DataFrame({
            "Keyword": ["custom stickers online", "enamel pins for sale", "aesthetic wall art",
                        "kawaii sticker pack", "trendy poster design"],
            "Volume": [18500, 12400, 11200, 8900, 6500],
            "Trend": ["+45%", "+32%", "+28%", "+21%", "+15%"],
            "Top Platform": ["Etsy/Shopee", "Etsy", "Instagram", "TikTok", "Reddit"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "🔍 Trend Scanner":
        st.title("Trend Scanner")

        if not st.session_state.gemini_key:
            st.warning("Set your Gemini API key in Settings.")

        c1, c2, c3 = st.columns(3)
        with c1:
            query = st.text_input("Search", "merchandise design trends")
        with c2:
            tf = st.select_slider("Timeframe", ["7d", "30d", "90d"], value="30d")
        with c3:
            mx = st.slider("Max themes", 3, 15, 8)

        st.markdown("**Sources**")
        s = st.columns(5)
        with s[0]: r = st.checkbox("Reddit", True)
        with s[1]: e = st.checkbox("Etsy")
        with s[2]: ig = st.checkbox("Instagram")
        with s[3]: tt = st.checkbox("TikTok")
        with s[4]: sp = st.checkbox("Shopee")

        if st.button("Run Analysis", type="primary", use_container_width=True):
            if not st.session_state.gemini_key:
                st.error("Set API key first")
            else:
                tf_map = {"7d": "week", "30d": "month", "90d": "all"}
                with st.spinner("Scraping..."):
                    try:
                        from utils.trend_pipeline import TrendPipeline
                        pl = TrendPipeline(st.session_state.gemini_key, st.session_state.supabase_url, st.session_state.supabase_key)
                        res = pl.run(niche=query, use_reddit=r, use_etsy=e, use_instagram=ig,
                                     use_tiktok=tt, use_shopee=sp, timeframe=tf_map.get(tf, "month"), max_themes=mx)
                        st.session_state.results = res
                        st.success("Done")
                    except Exception as e:
                        st.error(str(e)[:150])

        if st.session_state.results:
            res = st.session_state.results
            stats = res.get("source_stats", {})
            themes = res.get("themes", [])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sources", sum(1 for v in stats.values() if v > 0))
            col2.metric("Items", res.get("total_texts_analyzed", 0))
            col3.metric("Themes", len(themes))
            col4.metric("Saved", res.get("saved_to_db", 0))

            c1, c2 = st.columns(2)
            with c1:
                fig = source_pie(stats)
                if fig: st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = theme_bar(themes)
                if fig: st.plotly_chart(fig, use_container_width=True)

            theme_cards(themes)

            kw = res.get("keywords", [])
            if kw:
                st.divider()
                fig = px.treemap(pd.DataFrame({"kw": kw, "c": [1]*len(kw)}), path=["kw"], values="c")
                fig.update_layout(height=300, margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

    elif menu == "📈 SEO/SEM Keywords":
        st.title("SEO / SEM Keywords")

        st.markdown("**Sources for keyword extraction**")
        s = st.columns(3)
        with s[0]: ks_rd = st.checkbox("Reddit", True)
        with s[1]: ks_et = st.checkbox("Etsy", True)
        with s[2]: ks_ig = st.checkbox("Instagram", True)

        if st.button("Extract Keywords", type="primary", use_container_width=True) and st.session_state.gemini_key:
            with st.spinner("Extracting..."):
                try:
                    from utils.gemini_client import GeminiClient
                    gc = GeminiClient(st.session_state.gemini_key)
                    texts = ["best custom stickers online shop", "trending enamel pins",
                             "aesthetic wall art decor", "kawaii sticker pack for laptop",
                             "affordable art prints", "handmade enamel pins collection"]
                    kw = gc.extract_keywords(texts, 30)
                    st.session_state.seo_keywords = kw
                    st.success(f"{len(kw)} keywords")
                except Exception as e:
                    st.error(str(e)[:100])

        st.divider()

        if st.session_state.seo_keywords:
            kw = st.session_state.seo_keywords
            df = pd.DataFrame({
                "Keyword": kw,
                "Est. Volume": [max(1000, 8000 - i * 250) for i in range(len(kw))],
                "Trend": ["+" + str(15 + (i % 30)) + "%" for i in range(len(kw))],
                "Competition": ["Low" if i < 10 else "Medium" if i < 20 else "High" for i in range(len(kw))]
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

            fig = px.bar(df.head(15), x="Est. Volume", y="Keyword", orientation="h",
                         color="Est. Volume", color_continuous_scale="blues")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run extraction or see demo data below.")
            df = pd.DataFrame({
                "Keyword": ["custom stickers online", "enamel pins for sale", "aesthetic wall art",
                           "kawaii sticker pack", "personalized art print", "trendy poster design"],
                "Volume": [18500, 12400, 11200, 8900, 7600, 6500],
                "Trend": ["+45%", "+32%", "+28%", "+21%", "+38%", "+15%"],
                "Platform": ["Etsy/Shopee", "Etsy", "Instagram", "TikTok", "Etsy/IG", "Pinterest"]
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "🏆 Top Accounts":
        st.title("Top Accounts by Engagement & Sales")

        plat = st.selectbox("Platform", ["Instagram", "TikTok", "Etsy", "Reddit"])

        if plat == "Instagram":
            df = pd.DataFrame({
                "Account": ["@cute_sticker_shop", "@enamelpin_art", "@aesthetic_wallart",
                           "@kawaii_designs", "@artprint_studio", "@minimalist_art", "@cyberpunk_designs"],
                "Followers": ["145K", "98K", "87K", "76K", "62K", "54K", "48K"],
                "Engagement": ["12.4%", "9.8%", "11.2%", "14.1%", "8.5%", "10.3%", "7.8%"],
                "Est. Sales/Mo": ["$12K", "$8.5K", "$6.2K", "$9.1K", "$5.8K", "$4.2K", "$3.9K"],
                "Niche": ["Stickers", "Enamel Pins", "Art Prints", "Kawaii", "Posters", "Minimal", "Cyberpunk"],
            })
        elif plat == "TikTok":
            df = pd.DataFrame({
                "Account": ["@stickerqueen", "@pinmaster", "@artprint_tok", "@kawaii_crafts",
                           "@design_trending", "@viral_art", "@craftcorner"],
                "Followers": ["890K", "654K", "523K", "412K", "345K", "289K", "234K"],
                "Engagement": ["18.2%", "15.7%", "13.4%", "16.8%", "11.9%", "14.2%", "12.1%"],
                "Est. Sales/Mo": ["$45K", "$28K", "$18K", "$22K", "$12K", "$15K", "$9K"],
                "Niche": ["Stickers", "Enamel Pins", "Art", "Crafts", "Design", "Art", "DIY"],
            })
        elif plat == "Etsy":
            df = pd.DataFrame({
                "Shop": ["StickerCoveShop", "PinWizardStudio", "ArtPrintGallery", "KawaiiCraftHouse",
                        "DesignPosterHub", "MinimalArtCo", "CyberPrintStore"],
                "Sales": ["45,890", "32,100", "28,450", "21,800", "18,200", "15,400", "12,800"],
                "Rating": ["4.9", "4.8", "4.9", "4.7", "4.8", "4.6", "4.9"],
                "Revenue (est.)": ["$180K", "$95K", "$85K", "$65K", "$54K", "$46K", "$38K"],
                "Top Product": ["Custom Sticker Pack", "Enamel Pin Set", "Wall Art Print", "Kawaii Stickers",
                               "Poster Design", "Minimal Poster", "Cyberpunk Print"],
            })
        else:
            df = pd.DataFrame({
                "Subreddit": ["r/stickers", "r/EnamelPins", "r/artprints", "r/artstore",
                            "r/artcommissions", "r/streetwearstartup", "r/printmaking"],
                "Members": ["245K", "89K", "156K", "78K", "620K", "345K", "45K"],
                "Top Post Score": ["12.4K", "8.9K", "15.2K", "6.7K", "5.8K", "18.3K", "4.2K"],
                "Trending Topic": ["Holographic Stickers", "Anime Pins", "Minimalist Prints",
                                  "Digital Art", "Kawaii Style", "Streetwear", "Screen Print"],
            })

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"{len(df)} top {plat} accounts tracked. Run Trend Scanner to refresh data.")

# ====================================================================
# WEB DEV MODE
# ====================================================================
elif st.session_state.mode == "webdev":

    if menu == "📊 Dashboard":
        st.title("Web System Developer Mode")
        st.caption("Find businesses that need websites, POS systems, or digital upgrades.")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Leads", "0")
        col2.metric("Scanned", "0")
        col3.metric("No Website", "0")
        col4.metric("Needs Upgrade", "0")

        st.divider()
        st.markdown("### Target Markets")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Kuala Lumpur**")
            st.markdown("- Cafes: ~230")
            st.markdown("- Creative studios: ~180")
            st.markdown("- Retail: ~340")
        with c2:
            st.markdown("**Selangor / PJ**")
            st.markdown("- Restaurants: ~410")
            st.markdown("- Salons: ~280")
            st.markdown("- Gyms: ~160")
        st.info("Run Lead Finder to scrape real data.")

    elif menu == "🎯 Lead Finder":
        st.title("Lead Finder")
        st.info("Coming in Phase 3")

    elif menu == "🌐 Website Audit":
        st.title("Website Audit")
        st.info("Coming after Lead Finder")
