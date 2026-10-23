import streamlit as st
from frontend.ui_utils import render_html
from frontend.pages import about, overview, product_intelligence, live_prediction, keyword_insights, model_comparison

st.set_page_config(
    page_title="Sentiment Core Intelligence",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="locked",
)

DARK_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Design Tokens: Linear / Vercel Minimalist Standard ──────────────── */
    :root {
        --bg-app:          #090a0d;
        --bg-sidebar:      #0c0d12;
        --bg-card:         #111317;
        --bg-hover:        #181b21;
        --border:          rgba(255, 255, 255, 0.07);
        --border-focus:    rgba(255, 255, 255, 0.16);

        --text-primary:    #ffffff;
        --text-value:      #d1d5db;
        --text-secondary:  #9ca3af;
        --text-muted:      #6b7280;
        --text-caption:    #4b5563;

        --accent-pos:      #10b981;
        --accent-pos-soft: #00e599;
        --accent-warn:     #f59e0b;
        --accent-crit:     #ef4444;
        --accent-toptier:  #b5179e;

        --radius-card:     8px;
        --radius-pill:     4px;
        --transition:      all 0.15s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes live-pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.3; }
    }

    /* ── Base ────────────────────────────────────────────────────────────── */
    html, body,
    [data-testid="stAppViewContainer"],
    .main,
    [data-testid="stMainBlockContainer"],
    .block-container {
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
        overflow-x: hidden !important;
        max-width: 100% !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: var(--bg-app) !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    body, p, h1, h2, h3, h4, h5, h6, label, input, select, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        box-sizing: border-box !important;
    }

    [data-testid*="stIcon"], [data-testid="stIconMaterial"],
    [class*="material-symbols"], [class*="material-icons"],
    .material-symbols-rounded, .material-symbols-outlined, .material-icons,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] svg {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        word-break: break-word !important;
    }

    /* ── Hide Streamlit Chrome ───────────────────────────────────────────── */
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

    /* ── Sidebar: Linear / Vercel Developer Console ─────────────────────── */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 256px !important;
        min-width: 256px !important;
        max-width: 256px !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        z-index: 999 !important;
        position: relative !important;
        background: #0c0d12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        box-shadow: none !important;
        animation: none !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: flex !important;
        visibility: visible !important;
        width: 256px !important;
        min-width: 256px !important;
        max-width: 256px !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
    }

    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .block-container {
        padding-top: 16px !important;
        padding-bottom: 24px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
        width: 100% !important;
    }

    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    [data-testid="stSidebar"] * {
        box-sizing: border-box;
    }

    .nav-label {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #4b5563;
        padding: 0 4px;
        margin: 0 0 8px 0;
    }

    /* ── Sidebar Nav Buttons ──────────────────────────────────────────────── */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 2px !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        color: #8b949e !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-left: 2px solid transparent !important;
        border-radius: 4px !important;
        padding: 8px 12px !important;
        transition: background 0.12s ease, color 0.12s ease, border-color 0.12s ease !important;
        width: 100% !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] .stButton > button * {
        color: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        text-align: left !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.02) !important;
        color: #d1d5db !important;
        border-color: transparent !important;
        border-left: 2px solid transparent !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        border: 1px solid transparent !important;
        border-left: 2px solid #10b981 !important;
        border-radius: 0 4px 4px 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-left: 2px solid #10b981 !important;
    }

    /* ── Pinned Bottom Telemetry Footer ──────────────────────────────────── */
    .sidebar-telemetry {
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 16px;
        margin-top: 32px;
    }

    .sidebar-engine-status {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 14px;
    }

    .sidebar-engine-text {
        font-size: 11px;
        font-weight: 500;
        color: #d1d5db;
        letter-spacing: 0.01em;
    }

    .sidebar-data-spec {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .sidebar-spec-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .sidebar-spec-label {
        font-family: 'JetBrains Mono', monospace;
        color: #6b7280;
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.05em;
    }

    .sidebar-spec-val {
        font-family: 'JetBrains Mono', monospace;
        color: #d1d5db;
        font-size: 11px;
        font-weight: 400;
    }

    /* ── Main content padding ────────────────────────────────────────────── */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }

    /* ── Metric cards ────────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-card) !important;
        padding: 0.85rem 1rem !important;
        transition: var(--transition) !important;
    }

    [data-testid="stMetric"]:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-focus) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.65rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.35rem !important;
        font-weight: 600 !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: var(--radius-card);
        padding: 3px;
        gap: 2px;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 6px !important;
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 0.4rem 0.9rem !important;
        border: none !important;
        transition: var(--transition) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background-color: var(--bg-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-focus) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

    /* ── Inputs ──────────────────────────────────────────────────────────── */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-card) !important;
        transition: var(--transition) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: none !important;
    }

    [data-baseweb="tag"] {
        background-color: var(--bg-hover) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-pill) !important;
    }

    /* ── Buttons ─────────────────────────────────────────────────────────── */
    .stButton > button {
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        font-weight: 500;
        border-radius: var(--radius-card);
        padding: 0.45rem 1.1rem;
        transition: var(--transition);
    }

    .stButton > button:hover {
        background: var(--bg-hover);
        border-color: var(--border-focus);
        color: var(--text-primary);
    }

    .stButton > button[kind="primary"] {
        background: var(--bg-hover) !important;
        border: 1px solid var(--border-focus) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ── Expanders ───────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-card) !important;
        color: var(--text-primary) !important;
        transition: var(--transition) !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-hover) !important;
        border-color: var(--border-focus) !important;
    }

    .streamlit-expanderContent {
        background-color: var(--bg-app) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-card) var(--radius-card) !important;
    }

    /* ── Scrollbar ───────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

    /* ── Utility ─────────────────────────────────────────────────────────── */
    .live-dot {
        display: inline-block;
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--accent-pos);
        animation: live-pulse 2.5s ease-in-out infinite;
    }

    .section-label {
        font-size: 0.62rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }
</style>
"""



render_html(DARK_THEME_CSS)

PAGES = {
    "01 · Historical Pulse": overview,
    "02 · Live Inference": live_prediction,
    "03 · Aspect Explorer": keyword_insights,
    "04 · Benchmark Zoo": model_comparison,
    "05 · Product Insights": product_intelligence,
    "06 · System Overview": about,
}


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

        for page_name in PAGES.keys():
            is_active = st.session_state.get("current_page") == page_name
            if st.button(
                page_name,
                key=f"nav_{page_name}",
                width='stretch',
                type="primary" if is_active else "secondary",
            ):
                st.session_state["current_page"] = page_name
                st.rerun()

        render_html("""
        <div class="sidebar-telemetry">
            <div class="sidebar-engine-status">
                <span class="live-dot"></span>
                <span class="sidebar-engine-text">FastAPI: Connected (Port 8000)</span>
            </div>
            <div class="sidebar-data-spec">
                <div class="sidebar-spec-row">
                    <span class="sidebar-spec-label">Corpus</span>
                    <span class="sidebar-spec-val">81,700 Reviews</span>
                </div>
                <div class="sidebar-spec-row">
                    <span class="sidebar-spec-label">Split</span>
                    <span class="sidebar-spec-val">80 / 20 Stratified</span>
                </div>
                <div class="sidebar-spec-row">
                    <span class="sidebar-spec-label">Model</span>
                    <span class="sidebar-spec-val">Balanced LR</span>
                </div>
                <div class="sidebar-spec-row">
                    <span class="sidebar-spec-label">Metric</span>
                    <span class="sidebar-spec-val">70.84% Macro Recall</span>
                </div>
            </div>
        </div>
        """)


def main():
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "01 · Historical Pulse"

    # Backwards compatibility for session state
    current = st.session_state.get("current_page", "")
    if current not in PAGES:
        old_mapping = {
            "Executive Overview": "06 · System Overview",
            "System Overview": "06 · System Overview",
            "Overview": "06 · System Overview",
            "About": "06 · System Overview",
            "Overall Analysis": "01 · Historical Pulse",
            "Historical Pulse": "01 · Historical Pulse",
            "Historical": "01 · Historical Pulse",
            "Live Inference": "02 · Live Inference",
            "Live": "02 · Live Inference",
            "Inference": "02 · Live Inference",
            "Aspect Explorer": "03 · Aspect Explorer",
            "Keyword Insights": "03 · Aspect Explorer",
            "Keyword": "03 · Aspect Explorer",
            "Aspect": "03 · Aspect Explorer",
            "Benchmark Zoo": "04 · Benchmark Zoo",
            "Model Comparison": "04 · Benchmark Zoo",
            "Benchmark": "04 · Benchmark Zoo",
            "Product Insights": "05 · Product Insights",
            "Product Intelligence": "05 · Product Insights",
            "Product": "05 · Product Insights",
        }
        for old_sub, new_key in old_mapping.items():
            if old_sub.lower() in current.lower():
                st.session_state["current_page"] = new_key
                break
        else:
            for page_key in PAGES:
                if current and current.lower() in page_key.lower():
                    st.session_state["current_page"] = page_key
                    break
            else:
                st.session_state["current_page"] = "01 · Historical Pulse"

    render_sidebar()

    page_module = PAGES[st.session_state["current_page"]]
    page_module.render()


if __name__ == "__main__":
    main()