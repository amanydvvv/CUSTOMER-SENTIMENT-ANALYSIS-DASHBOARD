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

        --accent-pos:      #00e599;
        --accent-pos-soft: #00e599;
        --accent-warn:     #fca311;
        --accent-crit:     #ff385c;
        --accent-toptier:  #00e599;

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


def _check_backend_status() -> bool:
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:8000/health", headers={"User-Agent": "Streamlit"})
        with urllib.request.urlopen(req, timeout=0.4) as res:
            return res.status == 200
    except Exception:
        return False


# -------------------------------------------------------------------------
# SIDEBAR: TOP-ALIGNED NAVIGATION + VIEWPORT-PINNED BOTTOM DOCK
# -------------------------------------------------------------------------

def render_sidebar():
    st.markdown(
        """
        <style>
        /* 1. Force sidebar viewport container to full height flexbox */
        section[data-testid="stSidebar"] {
            height: 100vh !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-child {
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
            min-height: calc(100vh - 2.5rem) !important;
            justify-content: flex-start !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            box-sizing: border-box !important;
            gap: 6px !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding-bottom: 2.5rem !important;
            min-height: calc(100vh - 2.5rem) !important;
        }

        /* 2. Top Navigation Section */
        .sidebar-top-wrapper {
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 100%;
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        .nav-header-label {
            font-size: 10px;
            font-weight: 700;
            color: #52525b;
            letter-spacing: 1.2px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        /* Streamlit button style overrides for navigation */
        .stButton > button {
            width: 100% !important;
            text-align: left !important;
            justify-content: flex-start !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            font-size: 13.5px !important;
            padding: 9px 12px !important;
            margin: 0 !important;
            background: transparent !important;
            color: #a1a1aa !important;
            border: 1px solid transparent !important;
            border-left: 3px solid transparent !important;
            transition: all 0.15s ease !important;
            box-shadow: none !important;
        }

        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.04) !important;
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.06) !important;
        }

        .stButton > button[kind="primary"] {
            background: #18181b !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-left: 3px solid #00e599 !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="secondary"] {
            background: transparent !important;
            color: #a1a1aa !important;
            border: 1px solid transparent !important;
            border-left: 3px solid transparent !important;
            box-shadow: none !important;
        }

        /* 3. Middle Dynamic Space Filler */
        .sidebar-spacer {
            flex-grow: 1 !important;
            min-height: 40px !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(.sidebar-spacer) {
            flex-grow: 1 !important;
            display: flex !important;
        }

        /* 4. Bottom Pinned Telemetry Dock */
        .telemetry-bottom-dock {
            width: 100% !important;
            margin-top: auto !important;
            margin-bottom: 0 !important;
            padding: 12px 14px;
            background: #111217;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            box-sizing: border-box;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(.telemetry-bottom-dock) {
            margin-top: auto !important;
            width: 100% !important;
        }

        .telemetry-status-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #00e599;
            margin-bottom: 10px;
            white-space: nowrap;
        }

        .telemetry-status-dot {
            width: 7px;
            height: 7px;
            background-color: #00e599;
            border-radius: 50%;
            box-shadow: 0 0 6px rgba(0, 229, 153, 0.8);
            display: inline-block;
            flex-shrink: 0;
        }

        .telemetry-table-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 3.5px 0;
            font-size: 11px;
            font-family: monospace;
            white-space: nowrap;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .telemetry-table-row:last-child {
            border-bottom: none;
        }

        .telemetry-col-label {
            color: #71717a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .telemetry-col-value {
            color: #e4e4e7;
            font-weight: 600;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # --- TOP: NAVIGATION ---
        st.markdown(
            """
            <div class="sidebar-top-wrapper">
                <div class="nav-header-label">Navigation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for page_name in PAGES.keys():
            is_active = st.session_state.get("current_page") == page_name
            if st.button(
                page_name,
                key=f"nav_btn_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["current_page"] = page_name
                st.rerun()

        # --- MIDDLE: FLEX SPACER ---
        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)

        # --- BOTTOM: PINNED TELEMETRY STATUS DOCK ---
        is_connected = _check_backend_status()
        dot_color = "#00e599" if is_connected else "#ef4444"
        dot_shadow = "rgba(0, 229, 153, 0.8)" if is_connected else "rgba(239, 68, 68, 0.8)"
        status_text = "FastAPI: Connected (Port 8000)" if is_connected else "FastAPI: Disconnected"
        header_color = "#00e599" if is_connected else "#ef4444"

        st.markdown(
            f"""
            <div class="telemetry-bottom-dock">
                <div class="telemetry-status-header" style="color: {header_color};">
                    <span class="telemetry-status-dot" style="background-color: {dot_color}; box-shadow: 0 0 6px {dot_shadow};"></span>
                    <span>{status_text}</span>
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