"""
test_product_intelligence.py
────────────────────────────
Unit and integration tests for the Product Intelligence page module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from frontend.data_loader import load_historical_dataset
from frontend.pages import product_intelligence

_get_product_catalog = product_intelligence._get_product_catalog
_analyze_product_aspects = product_intelligence._analyze_product_aspects
_generate_dynamic_summary = product_intelligence._generate_dynamic_summary
_star_icons = product_intelligence._star_icons
from frontend.ui_utils import clean_html, render_html


def test_product_catalog_generation():
    df = load_historical_dataset(sample_limit=1000)
    assert not df.empty
    options, lookup = _get_product_catalog(df)
    assert len(options) > 0
    assert len(lookup) > 0
    first_opt = options[0]
    first_asin = lookup[first_opt]
    assert len(first_asin) > 0
    assert first_asin in df["product"].values


def test_star_icons():
    assert _star_icons(5.0) == "★★★★★"
    assert _star_icons(4.0) == "★★★★☆"
    assert _star_icons(3.0) == "★★★☆☆"
    assert _star_icons(1.0) == "★☆☆☆☆"
    assert _star_icons(0.0) == "★☆☆☆☆"
    assert _star_icons(5.5) == "★★★★★"


def test_analyze_product_aspects():
    mock_reviews = pd.DataFrame([
        {"text": "The delivery was delayed and late, took weeks.", "rating": 1.0, "sentiment": "negative"},
        {"text": "Bottle pump was broken and leaking everywhere.", "rating": 1.0, "sentiment": "negative"},
        {"text": "Gave me a severe allergic rash and burning.", "rating": 1.0, "sentiment": "negative"},
        {"text": "Overpriced and not worth the money.", "rating": 2.0, "sentiment": "negative"},
    ])
    summary, samples, high_pri = _analyze_product_aspects(mock_reviews)
    assert len(summary) > 0
    assert len(samples) > 0
    aspect_names = [item["aspect"] for item in summary]
    assert any(a in aspect_names for a in ["Delivery", "Packaging", "Product Quality", "Price & Value"])
    # Product quality with reaction should trigger HIGH priority
    assert high_pri >= 1


def test_generate_dynamic_summary():
    # Test positive dominant
    summary_pos = _generate_dynamic_summary(
        pos_pct=85.0, neu_pct=5.0, neg_pct=10.0, total=100, neg_count=10,
        aspect_summary=[{"aspect": "Delivery", "share_pct": 50.0, "issue": "Shipping Delay"}]
    )
    assert "85.0%" in summary_pos
    assert "Delivery" in summary_pos

    # Test negative dominant
    summary_neg = _generate_dynamic_summary(
        pos_pct=30.0, neu_pct=10.0, neg_pct=60.0, total=100, neg_count=60,
        aspect_summary=[{"aspect": "Product Quality", "share_pct": 70.0, "issue": "Adverse Reaction"}]
    )
    assert "60.0%" in summary_neg
    assert "Product Quality" in summary_neg

    # Test zero negative
    summary_zero = _generate_dynamic_summary(
        pos_pct=100.0, neu_pct=0.0, neg_pct=0.0, total=50, neg_count=0, aspect_summary=[]
    )
    assert "exclusively favorable" in summary_zero


def test_clean_html_strips_indentation():
    raw_html = """
        <div style="background:#111;">
            <span>Test Text</span>
        </div>
    """
    cleaned = clean_html(raw_html)
    assert cleaned.startswith("<div")
    assert not cleaned.startswith("    ")


@patch("streamlit.plotly_chart")
@patch("streamlit.selectbox")
@patch("streamlit.multiselect")
@patch("streamlit.radio")
@patch("streamlit.checkbox")
def test_full_render_cycle(mock_cb, mock_radio, mock_multi, mock_sel, mock_plotly):
    # Mock user choosing first product option
    mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else "B007IAE5WY"
    mock_multi.side_effect = lambda label, options, default=None, **kwargs: default if default is not None else options[:2]
    mock_radio.side_effect = lambda label, options, **kwargs: options[0] if options else ""
    mock_cb.return_value = False

    product_intelligence.render()
    assert mock_sel.called
    assert mock_plotly.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
