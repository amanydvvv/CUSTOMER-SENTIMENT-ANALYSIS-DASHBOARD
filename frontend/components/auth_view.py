import streamlit as st
from typing import Optional, Dict, Any
from frontend.utils.api_client import api_client

DEMO_ACCOUNTS = [
    ("👑 Admin", "admin@sentiment.io", "admin123", "Full Read/Write/Delete/Benchmark Controls"),
    ("📊 Analyst", "analyst@sentiment.io", "analyst123", "Analytics, Ingestion & Evaluation"),
    ("👀 Viewer", "viewer@sentiment.io", "viewer123", "Read-only Dashboard & Reports"),
]


def render_auth_sidebar() -> Optional[Dict[str, Any]]:
    """Render authentication state, user badge, and quick demo switcher in the sidebar."""
    st.sidebar.markdown("### 🔐 Security & RBAC Auth")

    current_token = st.session_state.get("auth_token")
    current_user = st.session_state.get("auth_user")

    if current_token and current_user:
        role = current_user.get("role", "viewer").upper()
        role_color = "#F59E0B" if role == "ADMIN" else ("#38BDF8" if role == "ANALYST" else "#10B981")

        st.sidebar.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 700; color: #F1F5F9;">{current_user.get('full_name', 'User')}</div>
                <div style="font-size: 12px; color: #94A3B8;">{current_user.get('email')}</div>
                <div style="margin-top: 8px;">
                    <span style="background: rgba(255,255,255,0.1); color: {role_color}; border: 1px solid {role_color}; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">
                        ROLE: {role}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state["auth_token"] = None
            st.session_state["auth_user"] = None
            st.rerun()

        return current_user

    # Not logged in: Show Demo Quick Login & Custom Form
    st.sidebar.markdown("**⚡ Quick Demo Login:**")
    for label, email, pwd, desc in DEMO_ACCOUNTS:
        if st.sidebar.button(f"{label} ({email.split('@')[0]})", key=f"demo_btn_{email}", use_container_width=True):
            try:
                res = api_client.login(email, pwd)
                st.session_state["auth_token"] = res["access_token"]
                st.session_state["auth_user"] = res["user"]
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Login failed: {e}")

    with st.sidebar.expander("Custom Login Credentials"):
        username_input = st.text_input("Username or Email", key="custom_auth_user")
        pwd_input = st.text_input("Password", type="password", key="custom_auth_pwd")
        if st.button("Sign In", type="primary", use_container_width=True):
            try:
                res = api_client.login(username_input, pwd_input)
                st.session_state["auth_token"] = res["access_token"]
                st.session_state["auth_user"] = res["user"]
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Login failed: {e}")

    return None
