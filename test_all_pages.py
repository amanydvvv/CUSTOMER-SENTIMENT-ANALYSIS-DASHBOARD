"""
test_all_pages.py
─────────────────
Comprehensive integration testing for all Streamlit page render modules.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from frontend.pages import overview, product_intelligence, live_prediction, keyword_insights, model_comparison


class TestPageExecution(unittest.TestCase):
    @patch("streamlit.plotly_chart")
    @patch("streamlit.selectbox")
    @patch("streamlit.multiselect")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    def test_product_intelligence_render(self, mock_cb, mock_radio, mock_multi, mock_sel, mock_plotly):
        mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else "B007IAE5WY"
        mock_multi.side_effect = lambda label, options, default=None, **kwargs: default if default is not None else options[:2]
        mock_radio.side_effect = lambda label, options, **kwargs: options[0] if options else ""
        mock_cb.return_value = False

        # Execute render function
        product_intelligence.render()
        self.assertTrue(mock_sel.called)

    @patch("streamlit.plotly_chart")
    @patch("streamlit.selectbox")
    @patch("streamlit.multiselect")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    def test_overview_render(self, mock_cb, mock_radio, mock_multi, mock_sel, mock_plotly):
        mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else "All"
        mock_multi.side_effect = lambda label, options, default=None, **kwargs: default if default is not None else ["All"]
        mock_radio.side_effect = lambda label, options, **kwargs: options[0] if options else ""
        mock_cb.return_value = False

        overview.render()

    @patch("streamlit.plotly_chart")
    @patch("streamlit.selectbox")
    @patch("streamlit.text_area")
    @patch("streamlit.button")
    def test_live_prediction_render(self, mock_btn, mock_ta, mock_sel, mock_plotly):
        mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else ""
        mock_ta.return_value = "Great hydrating formula, really loved the scent!"
        mock_btn.return_value = False

        live_prediction.render()

    @patch("streamlit.plotly_chart")
    @patch("streamlit.selectbox")
    def test_keyword_insights_render(self, mock_sel, mock_plotly):
        mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else "All"
        keyword_insights.render()

    @patch("streamlit.plotly_chart")
    @patch("streamlit.selectbox")
    def test_model_comparison_render(self, mock_sel, mock_plotly):
        mock_sel.side_effect = lambda label, options, **kwargs: options[0] if options else "All"
        model_comparison.render()


if __name__ == "__main__":
    unittest.main()
