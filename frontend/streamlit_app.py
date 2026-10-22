import streamlit as st
from frontend.ui_utils import render_html
from frontend.pages import about, overview, product_intelligence, live_prediction, keyword_insights, model_comparison

st.set_page_config(
    page_title="Customer Feedback Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="locked",
)

DARK_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-app: #090B10;
        --bg-sidebar: #0D1017;
        --bg-card: rgba(17, 21, 29, 0.65);
        --bg-card-solid: #11151D;
        --bg-card-hover: rgba(23, 28, 38, 0.8);
        --bg-input: #151A24;
        --border-subtle: rgba(30, 37, 51, 0.6);
        --border-card: rgba(36, 42, 53, 0.5);
        --border-active: #7C5CFF;
        --border-glow: rgba(124, 92, 255, 0.12);

        --accent-primary: #7C5CFF;
        --accent-primary-hover: #9074FF;
        --accent-primary-muted: rgba(124, 92, 255, 0.12);
        --accent-secondary: #22D3EE;
        --accent-gradient: linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%);

        --sentiment-pos: #22C55E;
        --sentiment-neg: #EF4444;
        --sentiment-neu: #F59E0B;

        --text-primary: #F5F7FA;
        --text-secondary: #98A2B3;
        --text-muted: #667085;

        --glass-blur: blur(16px);
        --card-radius: 12px;
        --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ── Keyframe Animations ──────────────────────────────────────────── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 8px rgba(124, 92, 255, 0.15); }
        50%      { box-shadow: 0 0 20px rgba(124, 92, 255, 0.3); }
    }

    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    @keyframes gradient-shift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes live-pulse {
        0%, 100% { opacity: 1; }
        50%      { opacity: 0.4; }
    }

    /* ── Base Layout ──────────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stMainBlockContainer"], .block-container {
        overflow-x: hidden !important;
        max-width: 100% !important;
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
    }

    /* Subtle radial gradient background for depth */
    [data-testid="stAppViewContainer"] > .main {
        background: radial-gradient(ellipse at 20% 0%, rgba(124, 92, 255, 0.04) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 100%, rgba(34, 211, 238, 0.03) 0%, transparent 50%),
                    var(--bg-app) !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Typography — preserve material icon fonts */
    body, p, h1, h2, h3, h4, h5, h6, label, input, select, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        box-sizing: border-box !important;
    }

    [data-testid*="stIcon"],
    [data-testid="stIconMaterial"],
    [class*="material-symbols"],
    [class*="material-icons"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] svg {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        word-break: break-word !important;
    }

    /* ── Hide Streamlit Chrome ────────────────────────────────────────── */
    #MainMenu, footer { display: none !important; visibility: hidden !important; height: 0 !important; }

    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    nav[data-testid="stSidebarNav"] {
        display: none !important; height: 0 !important; overflow: hidden !important;
    }

    header[data-testid="stHeader"], [data-testid="stHeader"] {
        display: none !important; height: 0 !important; min-height: 0 !important;
        max-height: 0 !important; padding: 0 !important; margin: 0 !important;
        visibility: hidden !important;
    }

    .stDeployButton, [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ── Sidebar: Premium Dark Panel ─────────────────────────────────── */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 260px !important;
        min-width: 250px !important;
        max-width: 275px !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        z-index: 999 !important;
        position: relative !important;
        background: linear-gradient(180deg, #0D1017 0%, #0A0D14 100%) !important;
        border-right: 1px solid rgba(124, 92, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: flex !important; visibility: visible !important;
        width: 260px !important; min-width: 250px !important; max-width: 275px !important;
        transform: none !important; margin-left: 0 !important; left: 0 !important;
    }

    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        width: 100% !important;
    }

    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    [data-testid="stSidebar"] * { color: var(--text-primary); }

    /* Sidebar branding */
    .sidebar-brand {
        padding: 0.35rem 0.25rem 0.95rem;
        border-bottom: 1px solid rgba(124, 92, 255, 0.12);
        margin-bottom: 0.85rem;
    }

    .sidebar-brand-title {
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin: 0;
        line-height: 1.2;
    }

    .sidebar-brand-sub {
        font-size: 0.72rem;
        font-weight: 500;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.02em;
        margin-top: 0.25rem;
    }

    .nav-label {
        font-size: 0.62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        padding: 0 0.25rem;
        margin: 1rem 0 0.4rem;
    }

    /* Navigation Buttons — with active glow bar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-left: 3px solid transparent !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.5rem 0.75rem 0.5rem 0.85rem !important;
        border-radius: 0 8px 8px 0 !important;
        transition: var(--transition-smooth) !important;
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(124, 92, 255, 0.06) !important;
        color: var(--text-primary) !important;
        border-left-color: rgba(124, 92, 255, 0.3) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, rgba(124, 92, 255, 0.1) 0%, transparent 100%) !important;
        color: var(--text-primary) !important;
        border: 1px solid transparent !important;
        border-left: 3px solid var(--accent-primary) !important;
        font-weight: 700 !important;
        box-shadow: inset 0 0 20px rgba(124, 92, 255, 0.06), 0 0 12px rgba(124, 92, 255, 0.08) !important;
    }

    /* Sidebar Metadata Card */
    .sidebar-meta-card {
        background: var(--bg-card);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-glow);
        border-radius: 10px;
        padding: 0.85rem;
        margin-top: 1.5rem;
    }

    .sidebar-meta-title {
        font-size: 0.6rem; font-weight: 700; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.15rem;
    }

    .sidebar-meta-val {
        color: var(--text-secondary); font-weight: 500; margin-bottom: 0.55rem; line-height: 1.35;
    }

    .sidebar-meta-val:last-child { margin-bottom: 0; }

    /* ── Main Content Space ───────────────────────────────────────────── */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .block-container {
        padding-top: 0.65rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.7rem !important;
    }

    /* ── Glassmorphic Cards (Global) ─────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-card) !important;
        border-top: 2px solid rgba(124, 92, 255, 0.2) !important;
        border-radius: var(--card-radius) !important;
        padding: 0.85rem 1rem !important;
        transition: var(--transition-smooth) !important;
        animation: fadeInUp 0.5s ease-out both;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(124, 92, 255, 0.12);
        border-top-color: rgba(124, 92, 255, 0.4) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
    }

    /* ── Dark Tabs ────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        backdrop-filter: var(--glass-blur);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid var(--border-card);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 1rem !important;
        border: none !important;
        transition: var(--transition-smooth) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background-color: rgba(124, 92, 255, 0.08) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7C5CFF 0%, #6342E8 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(124, 92, 255, 0.35) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

    /* ── Input Controls ───────────────────────────────────────────────── */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
        background-color: var(--bg-input) !important;
        border: 1px solid var(--border-card) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        transition: var(--transition-smooth) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox > div > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.15) !important;
    }

    [data-baseweb="tag"] {
        background-color: var(--accent-primary-muted) !important;
        border: 1px solid rgba(124, 92, 255, 0.3) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
    }

    /* ── Buttons ──────────────────────────────────────────────────────── */
    .stButton > button {
        background: var(--bg-card-solid);
        border: 1px solid var(--border-card);
        color: var(--text-primary);
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.15rem;
        transition: var(--transition-smooth);
    }

    .stButton > button:hover {
        background-color: var(--bg-card-hover);
        border-color: var(--accent-primary);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 92, 255, 0.2);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C5CFF 0%, #6342E8 100%) !important;
        border: 1px solid rgba(124, 92, 255, 0.5) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(124, 92, 255, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #9074FF 0%, #7C5CFF 100%) !important;
        box-shadow: 0 6px 24px rgba(124, 92, 255, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Dark Expanders ───────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-card) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        transition: var(--transition-smooth) !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: rgba(124, 92, 255, 0.2) !important;
    }

    .streamlit-expanderContent {
        background-color: var(--bg-app) !important;
        border: 1px solid var(--border-card) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* ── Scrollbar ────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(124, 92, 255, 0.2); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(124, 92, 255, 0.4); }

    /* ── Utility Classes for Page Components ──────────────────────────── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-card);
        border-radius: var(--card-radius);
        padding: 1.1rem 1.25rem;
        transition: var(--transition-smooth);
        animation: fadeInUp 0.4s ease-out both;
    }

    .glass-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 0 20px rgba(124, 92, 255, 0.06);
    }

    .glass-card-accent {
        background: var(--bg-card);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--border-card);
        border-top: 2px solid;
        border-image: linear-gradient(90deg, #7C5CFF, #22D3EE) 1;
        border-image-slice: 1 1 0 1;
        border-radius: var(--card-radius);
        padding: 1.1rem 1.25rem;
        transition: var(--transition-smooth);
        animation: fadeInUp 0.4s ease-out both;
    }

    .gradient-text {
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .live-dot {
        display: inline-block;
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #22C55E;
        animation: live-pulse 2s ease-in-out infinite;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
    }

    .section-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--accent-primary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }

    .stat-big {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
    }
</style>
"""

render_html(DARK_THEME_CSS)

PAGES = {
    "ℹ️  Executive Overview": about,
    "📊  Overall Analysis": overview,
    "🔬  Product Intelligence": product_intelligence,
    "⚡  Live Review Intelligence": live_prediction,
    "🔑  Aspect & Keyword Explorer": keyword_insights,
    "📈  Model Benchmark": model_comparison,
}


def render_sidebar():
    with st.sidebar:
        render_html("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7C5CFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
                <span>CUSTOMER FEEDBACK</span>
            </div>
            <div class="sidebar-brand-sub">AI-Powered Sentiment Intelligence</div>
        </div>
        """)

        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

        for page_name in PAGES.keys():
            is_active = st.session_state.get("current_page") == page_name
            if st.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["current_page"] = page_name
                st.rerun()

        render_html("""
        <div class="sidebar-meta-card">
            <div class="sidebar-meta-title">DATA SOURCE</div>
            <div class="sidebar-meta-val">
                Amazon Reviews 2023<br>
                <span style="color:#667085;font-size:0.68rem;">81.7K unique reviews · All Beauty</span>
            </div>
            <div class="sidebar-meta-title">ML MODELS</div>
            <div class="sidebar-meta-val" style="font-size:0.72rem;">
                DistilBERT · Balanced LR · LinearSVC
            </div>
            <div class="sidebar-meta-title">INFERENCE</div>
            <div class="sidebar-meta-val" style="display:flex;align-items:center;gap:6px;font-weight:700;font-size:0.75rem;color:#22C55E;">
                <span class="live-dot"></span>
                LOCAL · REAL-TIME
            </div>
        </div>
        """)


def main():
    # Backwards compatibility for session state
    current = st.session_state.get("current_page", "")
    if current not in PAGES:
        # Map old names (without emoji) to new names
        for page_key in PAGES:
            if current in page_key:
                st.session_state["current_page"] = page_key
                break
        else:
            st.session_state["current_page"] = list(PAGES.keys())[0]

    render_sidebar()

    page_module = PAGES[st.session_state["current_page"]]
    page_module.render()


if __name__ == "__main__":
    main()