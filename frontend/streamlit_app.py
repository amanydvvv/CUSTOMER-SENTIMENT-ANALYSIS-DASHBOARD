import streamlit as st
from frontend.ui_utils import render_html
from frontend.pages import about, overview, product_intelligence, live_prediction, model_comparison

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

    /* Force Streamlit sidebar container to use full viewport height flexbox */
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-child {
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        height: 100vh !important;
        max-height: 100vh !important;
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        box-sizing: border-box !important;
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

    /* Top navigation block */
    .sidebar-top-section {
        display: flex;
        flex-direction: column;
        gap: 6px;
        width: 100%;
    }

    /* Pushes telemetry to absolute bottom, keeping blank space in the middle */
    .sidebar-middle-spacer {
        flex-grow: 1 !important;
        min-height: 20px;
    }

    /* Bottom Telemetry Dock - Zero Horizontal Clipping */
    .telemetry-bottom-dock {
        width: 100%;
        margin-top: auto;
        padding: 12px 14px;
        background: #111217;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        box-sizing: border-box;
    }

    .telemetry-status-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 11.5px;
        font-weight: 600;
        color: #00e599;
        margin-bottom: 10px;
        white-space: nowrap;
        letter-spacing: 0.2px;
    }

    .telemetry-status-dot {
        width: 7px;
        height: 7px;
        background-color: #00e599;
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(0, 229, 153, 0.7);
        flex-shrink: 0;
    }

    .telemetry-table-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 3.5px 0;
        font-size: 11px;
        white-space: nowrap;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }

    .telemetry-table-row:last-child {
        border-bottom: none;
    }

    .telemetry-col-label {
        color: #71717a;
        font-weight: 500;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .telemetry-col-value {
        color: #e4e4e7;
        font-weight: 600;
        font-family: monospace;
        text-align: right;
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
    "Historical Pulse": overview,
    "Live Inference": live_prediction,
    "Benchmark Zoo": model_comparison,
    "Product Insights": product_intelligence,
    "System Overview": about,
}


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-top-section">', unsafe_allow_html=True)
        st.markdown(
            "<span style='font-size:10px; font-weight:700; color:#52525b; letter-spacing:1px; margin-bottom:8px; display:block;'>NAVIGATION</span>",
            unsafe_allow_html=True,
        )

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

        st.markdown("</div>", unsafe_allow_html=True)

        # 3. Middle Empty Space (Maintains flexible gap between nav and bottom telemetry)
        st.markdown('<div class="sidebar-middle-spacer"></div>', unsafe_allow_html=True)

        # 4. Render Bottom Telemetry Dock (No Text Wrapping, Clean Monospace Values)
        st.markdown(
            """
            <div class="telemetry-bottom-dock">
                <div class="telemetry-status-header">
                    <span class="telemetry-status-dot"></span>
                    <span>FastAPI: Connected (Port 8000)</span>
                </div>
                <div class="telemetry-table-row">
                    <span class="telemetry-col-label">Corpus</span>
                    <span class="telemetry-col-value">81,700 Reviews</span>
                </div>
                <div class="telemetry-table-row">
                    <span class="telemetry-col-label">Split</span>
                    <span class="telemetry-col-value">80 / 20 Stratified</span>
                </div>
                <div class="telemetry-table-row">
                    <span class="telemetry-col-label">Model</span>
                    <span class="telemetry-col-value">Balanced LR</span>
                </div>
                <div class="telemetry-table-row">
                    <span class="telemetry-col-label">Metric</span>
                    <span class="telemetry-col-value" style="color:#00e599;">70.84% Macro Recall</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Historical Pulse"

    # Backwards compatibility for session state
    current = st.session_state.get("current_page", "")
    if current not in PAGES:
        old_mapping = {
            "01 · Historical Pulse": "Historical Pulse",
            "Overall Analysis": "Historical Pulse",
            "Historical Pulse": "Historical Pulse",
            "Historical": "Historical Pulse",
            "02 · Live Inference": "Live Inference",
            "Live Inference": "Live Inference",
            "Live": "Live Inference",
            "Inference": "Live Inference",
            "03 · Benchmark Zoo": "Benchmark Zoo",
            "04 · Benchmark Zoo": "Benchmark Zoo",
            "Benchmark Zoo": "Benchmark Zoo",
            "Model Comparison": "Benchmark Zoo",
            "Benchmark": "Benchmark Zoo",
            "04 · Product Insights": "Product Insights",
            "05 · Product Insights": "Product Insights",
            "Product Insights": "Product Insights",
            "Product Intelligence": "Product Insights",
            "Product": "Product Insights",
            "05 · System Overview": "System Overview",
            "06 · System Overview": "System Overview",
            "Executive Overview": "System Overview",
            "System Overview": "System Overview",
            "About": "System Overview",
            "Aspect Explorer": "Historical Pulse",
            "Keyword Insights": "Historical Pulse",
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
                st.session_state["current_page"] = "Historical Pulse"

    render_sidebar()

    page_module = PAGES[st.session_state["current_page"]]
    page_module.render()


if __name__ == "__main__":
    main()