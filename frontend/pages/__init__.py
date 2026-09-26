"""
Export numbered page modules with clean python attribute aliases.
"""
import importlib

overview = importlib.import_module("frontend.pages.1_overview")
product_intelligence = importlib.import_module("frontend.pages.5_product_intelligence")
live_prediction = importlib.import_module("frontend.pages.2_live_prediction")
keyword_insights = importlib.import_module("frontend.pages.3_keyword_insights")
model_comparison = importlib.import_module("frontend.pages.4_model_comparison")

__all__ = ["overview", "product_intelligence", "live_prediction", "keyword_insights", "model_comparison"]

