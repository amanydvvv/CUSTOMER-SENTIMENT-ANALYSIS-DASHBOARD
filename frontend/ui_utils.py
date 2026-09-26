"""
ui_utils.py
───────────
Utility functions for safe, bulletproof HTML rendering in Streamlit.
Strips all leading/trailing whitespace from every line to ensure Markdown parsers
NEVER interpret 4+ space indentations as code blocks (<pre><code>).
"""

import streamlit as st


def clean_html(html_str: str) -> str:
    """
    Strips leading and trailing whitespace from every line and joins them.
    Guarantees that no line has >= 4 spaces of indentation.
    """
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    return "".join(lines)


def render_html(html_str: str):
    """
    Safely renders custom HTML in Streamlit with zero risk of markdown code block escaping.
    """
    st.markdown(clean_html(html_str), unsafe_allow_html=True)
