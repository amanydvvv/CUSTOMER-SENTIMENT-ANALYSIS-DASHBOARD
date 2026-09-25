import streamlit as st
from frontend.pages import overview, live_prediction, keyword_insights, model_comparison

st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #2563eb;
        --primary-hover: #1d4ed8;
        --primary-light: #dbeafe;
        --secondary: #64748b;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --border: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --radius-sm: 6px;
        --radius: 8px;
        --radius-lg: 12px;
        --transition: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background: var(--bg-secondary);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .stSidebar {
        background: var(--bg-primary);
        border-right: 1px solid var(--border);
    }

    .stSidebar .stMarkdown {
        padding: 0;
    }

    .sidebar-brand {
        padding: 1.5rem 1rem 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    .sidebar-brand h1 {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .sidebar-brand svg {
        color: var(--primary);
    }

    .nav-section {
        padding: 0 0.75rem;
    }

    .nav-section-title {
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin: 1.5rem 0 0.5rem;
        padding-left: 0.5rem;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.625rem 0.875rem;
        border-radius: var(--radius);
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--transition);
        border: 1px solid transparent;
        margin-bottom: 0.25rem;
    }

    .nav-item:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .nav-item.active {
        background: var(--primary-light);
        color: var(--primary);
        border-color: var(--primary);
    }

    .nav-item svg {
        width: 18px;
        height: 18px;
        flex-shrink: 0;
    }

    .stButton > button {
        width: 100%;
        justify-content: flex-start;
        background: transparent;
        border: none;
        padding: 0.625rem 0.875rem;
        border-radius: var(--radius);
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        text-align: left;
        transition: all var(--transition);
    }

    .stButton > button:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 2px var(--primary-light);
    }

    .page-header {
        margin-bottom: 2rem;
    }

    .page-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.5rem;
        letter-spacing: -0.02em;
    }

    .page-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
        font-weight: 400;
    }

    .metric-card {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        transition: all var(--transition);
        box-shadow: var(--shadow-sm);
    }

    .metric-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--primary-light);
    }

    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.75rem;
    }

    .metric-icon svg {
        width: 20px;
        height: 20px;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
        margin: 0 0 0.25rem;
    }

    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin: 0;
    }

    .metric-trend {
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .trend-positive { color: var(--success); }
    .trend-negative { color: var(--danger); }
    .trend-neutral { color: var(--warning); }

    .chart-container {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
    }

    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 1rem;
    }

    .data-table {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    .stDataFrame {
        border: none !important;
    }

    .stDataFrame [data-testid="stTable"] {
        border-radius: var(--radius-lg);
    }

    .prediction-card {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .sentiment-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .sentiment-positive { background: #dcfce7; color: #166534; }
    .sentiment-negative { background: #fee2e2; color: #991b1b; }
    .sentiment-neutral { background: #fef3c7; color: #92400e; }

    .confidence-bar {
        height: 8px;
        background: var(--bg-tertiary);
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 0.75rem;
    }

    .confidence-fill {
        height: 100%;
        border-radius: 9999px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .confidence-positive { background: linear-gradient(90deg, #22c55e, #16a34a); }
    .confidence-negative { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .confidence-neutral { background: linear-gradient(90deg, #f59e0b, #d97706); }

    .keyword-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        background: var(--bg-tertiary);
        border-radius: var(--radius);
        font-size: 0.8125rem;
        font-weight: 500;
        color: var(--text-primary);
        transition: all var(--transition);
    }

    .keyword-chip:hover {
        background: var(--primary-light);
        color: var(--primary);
    }

    .keyword-chip .score {
        font-size: 0.6875rem;
        color: var(--text-muted);
        background: var(--bg-primary);
        padding: 0.125rem 0.375rem;
        border-radius: 9999px;
        font-weight: 600;
    }

    .model-card {
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        transition: all var(--transition);
    }

    .model-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--primary-light);
    }

    .model-card.best {
        border-color: var(--success);
        box-shadow: 0 0 0 1px var(--success);
    }

    .model-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 0.5rem;
    }

    .model-metric {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
    }

    .model-metric:last-child {
        border-bottom: none;
    }

    .model-metric-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .model-metric-value {
        font-weight: 600;
        color: var(--text-primary);
    }

    .best-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        background: #dcfce7;
        color: #166534;
        border-radius: var(--radius-sm);
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .stTextArea textarea {
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
        font-family: 'Inter', monospace !important;
        font-size: 0.875rem !important;
        padding: 0.875rem !important;
        transition: all var(--transition) !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-light) !important;
    }

    .stSelectbox [data-baseweb="select"] {
        border-radius: var(--radius) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        border: 1px solid var(--border) !important;
    }

    .stSelectbox [data-baseweb="select"]:focus-within > div {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-light) !important;
    }

    .stSlider [data-baseweb="slider"] {
        margin-top: 0.5rem;
    }

    .stSlider [role="slider"] {
        background: var(--primary) !important;
    }

    .stSlider [data-baseweb="slider"] [aria-valuenow] {
        background: var(--primary) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: var(--bg-tertiary);
        padding: 0.25rem;
        border-radius: var(--radius);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 1rem !important;
        transition: all var(--transition) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-primary) !important;
        color: var(--primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stExpander {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--bg-primary) !important;
    }

    .stExpander summary {
        font-weight: 500 !important;
        color: var(--text-primary) !important;
    }

    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8125rem;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .page-title {
            font-size: 1.5rem;
        }
        .metric-value {
            font-size: 1.5rem;
        }
    }

    .stAlert {
        border-radius: var(--radius) !important;
        border: none !important;
    }

    [data-testid="stNotification"] {
        border-radius: var(--radius) !important;
    }

    .stProgress > div > div > div {
        background: var(--primary) !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PAGES = {
    "Overview": overview,
    "Live Prediction": live_prediction,
    "Keyword Insights": keyword_insights,
    "Model Comparison": model_comparison,
}

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <h1>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                Sentiment AI
            </h1>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section-title">Dashboard</div>', unsafe_allow_html=True)
        
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

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="nav-section">', unsafe_allow_html=True)
        st.markdown('<div class="nav-section-title">Settings</div>', unsafe_allow_html=True)
        
        st.selectbox(
            "Model",
            ["Balanced Logistic Regression", "Logistic Regression", "LinearSVC"],
            key="selected_model",
            index=0,
        )
        
        st.slider(
            "Confidence Threshold",
            0.0, 1.0, 0.5, 0.05,
            key="confidence_threshold",
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="footer">
            Sentiment Analysis Dashboard v1.0<br>
            Built with Streamlit & FastAPI
        </div>
        """, unsafe_allow_html=True)

def main():
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Overview"

    render_sidebar()

    page_module = PAGES[st.session_state["current_page"]]
    page_module.render()

if __name__ == "__main__":
    main()