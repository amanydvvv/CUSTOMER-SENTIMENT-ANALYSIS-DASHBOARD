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

    /* ── Sidebar: Modern Dark Console ────────────────────────────────────── */
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
        background: #0b0b0f !important;
        border-right: 1px solid #1f1f26 !important;
        box-shadow: none !important;
        animation: none !important;
        overflow-x: hidden !important;
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
    [data-testid="stSidebar"] .block-container {
        display: flex !important;
        flex-direction: column !important;
        height: 100vh !important;
        max-height: 100vh !important;
        padding-top: 14px !important;
        padding-bottom: 14px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        box-sizing: border-box !important;
        overflow-y: hidden !important;
        overflow-x: hidden !important;
    }

    /* Main vertical container inside sidebar: tight 6px gap, flex column */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-child {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        max-height: calc(100vh - 28px) !important;
        gap: 6px !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    [data-testid="stSidebar"] * {
        box-sizing: border-box;
    }

    /* ── Hide inner scrollbars cleanly (Firefox, Chrome, Safari, Edge) ───── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] {
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebarUserContent"]::-webkit-scrollbar,
    [data-testid="stSidebar"] .block-container::-webkit-scrollbar {
        display: none !important;
        width: 0px !important;
        height: 0px !important;
    }

    /* ── Brand Logo Header ───────────────────────────────────────────────── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 6px 12px 6px;
        margin-bottom: 4px;
        border-bottom: 1px solid #1f1f26;
        width: 100%;
    }

    .brand-badge {
        width: 28px;
        height: 28px;
        border-radius: 7px;
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4);
    }

    .brand-text {
        display: flex;
        flex-direction: column;
    }

    .brand-title {
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.02em;
        line-height: 1.2;
    }

    .brand-subtitle {
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 9.5px;
        font-weight: 500;
        color: #71717a;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* ── Navigation Section Label ────────────────────────────────────────── */
    .nav-label {
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #52525b;
        padding: 2px 8px 4px 8px;
        margin: 0;
    }

    /* ── Sidebar Nav Buttons: Compact 42px, 6px Gap, Smooth Hover ────────── */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div:has(.stButton) {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] .stButton {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 0 14px !important;
        border-radius: 6px !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
        border: 1px solid transparent !important;
        border-left: 3px solid transparent !important;
        background: transparent !important;
        color: #9ca3af !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] .stButton > button * {
        color: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        text-align: left !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.035) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.06) !important;
        border-left-color: rgba(124, 58, 237, 0.45) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(124, 58, 237, 0.12) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: 1px solid rgba(124, 58, 237, 0.25) !important;
        border-left: 3px solid #7c3aed !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(124, 58, 237, 0.18) !important;
        color: #ffffff !important;
        border-left: 3px solid #7c3aed !important;
    }

    /* ── Flexible Middle Spacer ──────────────────────────────────────────── */
    .sidebar-spacer {
        flex: 1 1 auto !important;
        min-height: 12px !important;
    }

    /* ── Bottom Telemetry Dock Card: Two-Column Aligned, No Collisions ──── */
    .telemetry-card {
        margin-top: auto !important;
        flex-shrink: 0 !important;
        background: #0f1015;
        border: 1px solid #1f1f26;
        border-radius: 8px;
        padding: 12px;
        width: 100%;
        box-sizing: border-box;
    }

    .telemetry-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 11.5px;
        font-weight: 600;
        color: #e4e4e7;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1f1f26;
        white-space: nowrap;
    }

    .telemetry-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .telemetry-dot.connected {
        background-color: #10b981;
        box-shadow: 0 0 6px rgba(16, 185, 129, 0.7);
        animation: live-pulse 2s infinite ease-in-out;
    }

    .telemetry-dot.disconnected {
        background-color: #ef4444;
        box-shadow: 0 0 6px rgba(239, 68, 68, 0.7);
    }

    .telemetry-grid {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .telemetry-row {
        display: grid;
        grid-template-columns: 55px 1fr;
        align-items: center;
        gap: 8px;
        font-size: 11px;
        line-height: 1.35;
    }

    .telemetry-label {
        color: #71717a;
        font-weight: 500;
        font-family: 'Inter', -apple-system, sans-serif;
        white-space: nowrap;
    }

    .telemetry-value {
        color: #d1d5db;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
        text-align: right;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .telemetry-value.metric-highlight {
        color: #10b981;
        font-weight: 600;
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


PAGE_ICONS = {
    "Historical Pulse": "📈",
    "Live Inference": "⚡",
    "Benchmark Zoo": "🔬",
    "Product Insights": "🛍️",
    "System Overview": "⚙️",
}


def _check_backend_status() -> bool:
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:8000/health", headers={"User-Agent": "Streamlit"})
        with urllib.request.urlopen(req, timeout=0.4) as res:
            return res.status == 200
    except Exception:
        return False


def render_sidebar():
    with st.sidebar:
        # 1. Brand Logo Header
        render_html("""
        <div class="sidebar-brand">
            <div class="brand-badge">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
            </div>
            <div class="brand-text">
                <span class="brand-title">Sentiment Core</span>
                <span class="brand-subtitle">Intelligence Engine</span>
            </div>
        </div>
        <div class="nav-label">Navigation</div>
        """)

        # 2. Navigation Items (Compact ~42px, 6px gap, left icon, clear active state)
        for page_name in PAGES.keys():
            is_active = st.session_state.get("current_page") == page_name
            icon = PAGE_ICONS.get(page_name, "●")
            if st.button(
                f"{icon}  {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["current_page"] = page_name
                st.rerun()

        # 3. Flexible Middle Spacer (absorbs vacant space, pushing dock to bottom)
        render_html('<div class="sidebar-spacer"></div>')

        # 4. Status Panel (Bottom-docked, 2-column layout, zero overflow, live dot)
        is_connected = _check_backend_status()
        dot_class = "connected" if is_connected else "disconnected"
        status_text = "FastAPI: Connected (Port 8000)" if is_connected else "FastAPI: Disconnected"

        render_html(f"""
        <div class="telemetry-card">
            <div class="telemetry-header">
                <span class="telemetry-dot {dot_class}"></span>
                <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{status_text}</span>
            </div>
            <div class="telemetry-grid">
                <div class="telemetry-row">
                    <span class="telemetry-label">Corpus</span>
                    <span class="telemetry-value" title="81,700 Reviews">81,700 Reviews</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Split</span>
                    <span class="telemetry-value" title="80 / 20 Stratified">80 / 20 Stratified</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Model</span>
                    <span class="telemetry-value" title="Balanced LR">Balanced LR</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-label">Metric</span>
                    <span class="telemetry-value metric-highlight" title="70.84% Macro Recall">70.84% Macro Recall</span>
                </div>
            </div>
        </div>
        """)


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