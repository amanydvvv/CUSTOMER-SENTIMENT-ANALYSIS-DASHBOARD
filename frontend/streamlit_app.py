import streamlit as st
from frontend.ui_utils import render_html
from frontend.pages import overview, product_intelligence, live_prediction, keyword_insights, model_comparison

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
        --bg-card: #11151D;
        --bg-card-hover: #171C26;
        --bg-input: #151A24;
        --border-subtle: #1E2533;
        --border-card: #242A35;
        --border-active: #7C5CFF;
        
        --accent-primary: #7C5CFF;
        --accent-primary-hover: #9074FF;
        --accent-primary-muted: rgba(124, 92, 255, 0.12);
        --accent-secondary: #22D3EE;
        
        --sentiment-pos: #22C55E;
        --sentiment-neg: #EF4444;
        --sentiment-neu: #F59E0B;
        
        --text-primary: #F5F7FA;
        --text-secondary: #98A2B3;
        --text-muted: #667085;
    }

    /* Prevent all horizontal overflow across viewports */
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stMainBlockContainer"], .block-container {
        overflow-x: hidden !important;
        max-width: 100% !important;
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
    }

    /* Target text typography without breaking Material Icon ligatures */
    body, p, h1, h2, h3, h4, h5, h6, label, input, select, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        box-sizing: border-box !important;
    }

    /* Preserve Icon Fonts and prevent raw ligature text leaks */
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

    /* Clean styling for sidebar collapse button */
    [data-testid="stSidebarCollapseButton"] {
        color: #98A2B3 !important;
        overflow: hidden !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        word-break: break-word !important;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Hide default multi-page nav links only (not the sidebar container) */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    nav[data-testid="stSidebarNav"] {
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Completely remove Streamlit Header Chrome & Unused Top Space */
    header[data-testid="stHeader"],
    [data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .stDeployButton,
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* FORCE sidebar visible — override ALL Streamlit collapse states */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 250px !important;
        min-width: 240px !important;
        max-width: 265px !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        z-index: 999 !important;
        position: relative !important;
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-card) !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-expanded="true"] {
        display: flex !important;
        visibility: visible !important;
        width: 250px !important;
        min-width: 240px !important;
        max-width: 265px !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
    }

    /* Remove excessive top gap in sidebar content */
    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        width: 100% !important;
    }

    /* Hide the collapse button since sidebar is locked */
    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Maximize main content space utilization with clean edge padding */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .block-container {
        padding-top: 0.65rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
    }

    /* Tighten vertical block spacing */
    [data-testid="stVerticalBlock"] {
        gap: 0.65rem !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary);
    }

    .sidebar-brand {
        padding: 0.25rem 0.25rem 0.85rem;
        border-bottom: 1px solid var(--border-subtle);
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
        color: var(--text-muted);
        letter-spacing: 0.02em;
        margin-top: 0.2rem;
    }

    .nav-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        padding: 0 0.25rem;
        margin: 1rem 0 0.35rem;
    }

    /* Custom Navigation Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.45rem 0.75rem !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: var(--accent-primary-muted) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--accent-primary) !important;
        font-weight: 600 !important;
        box-shadow: 0 0 8px rgba(124, 92, 255, 0.2) !important;
    }

    /* Sidebar Footer Metadata Card */
    .sidebar-meta-card {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 1.5rem;
        font-size: 0.72rem;
    }

    .sidebar-meta-title {
        font-size: 0.62rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.15rem;
    }

    .sidebar-meta-val {
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 0.5rem;
        line-height: 1.35;
    }

    .sidebar-meta-val:last-child {
        margin-bottom: 0;
    }

    /* Dark Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-card);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid var(--border-card);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 6px !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.4rem 0.9rem !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background-color: var(--bg-card-hover) !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--accent-primary) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(124, 92, 255, 0.4) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Dark Input Controls */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
        background-color: var(--bg-input) !important;
        border: 1px solid var(--border-card) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox > div > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 1px var(--accent-primary) !important;
    }

    [data-baseweb="tag"] {
        background-color: var(--accent-primary-muted) !important;
        border: 1px solid var(--accent-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--bg-card);
        border: 1px solid var(--border-card);
        color: var(--text-primary);
        font-weight: 600;
        border-radius: 6px;
        padding: 0.45rem 1rem;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background-color: var(--bg-card-hover);
        border-color: var(--accent-primary);
        color: #ffffff;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C5CFF 0%, #6342E8 100%) !important;
        border: 1px solid #7C5CFF !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(124, 92, 255, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #9074FF 0%, #7C5CFF 100%) !important;
        box-shadow: 0 4px 12px rgba(124, 92, 255, 0.45) !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }

    /* Dark Expanders */
    .streamlit-expanderHeader {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-card) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
    }

    .streamlit-expanderContent {
        background-color: var(--bg-app) !important;
        border: 1px solid var(--border-card) !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-app);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-card);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
"""

render_html(DARK_THEME_CSS)

PAGES = {
    "Overall Analysis": overview,
    "Product Intelligence": product_intelligence,
    "Live Review Intelligence": live_prediction,
    "Aspect & Keyword Explorer": keyword_insights,
    "Model Benchmark": model_comparison,
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
            <div class="sidebar-brand-sub">AI Review Analytics</div>
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
            <div class="sidebar-meta-title">DATA</div>
            <div class="sidebar-meta-val">
                Amazon Reviews 2023<br>
                <span style="color:#667085;font-size:0.68rem;">81.7K unique reviews</span>
            </div>
            <div class="sidebar-meta-title">MODEL</div>
            <div class="sidebar-meta-val">TF-IDF + Linear Models</div>
            <div class="sidebar-meta-title">INFERENCE</div>
            <div class="sidebar-meta-val" style="color:#22C55E;display:flex;align-items:center;gap:5px;font-weight:700;font-size:0.75rem;">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#22C55E;"></span>
                LOCAL
            </div>
        </div>
        """)


def main():
    # Backwards compatibility for session state
    if st.session_state.get("current_page") == "Overview":
        st.session_state["current_page"] = "Overall Analysis"
    elif st.session_state.get("current_page") not in PAGES:
        st.session_state["current_page"] = "Overall Analysis"

    render_sidebar()

    page_module = PAGES[st.session_state["current_page"]]
    page_module.render()


if __name__ == "__main__":
    main()