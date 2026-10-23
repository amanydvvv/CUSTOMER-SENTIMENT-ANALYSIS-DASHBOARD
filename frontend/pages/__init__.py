"""
Export numbered page modules with clean python attribute aliases.
"""
import importlib

about = importlib.import_module("frontend.pages.0_about")
overview = importlib.import_module("frontend.pages.1_overview")
product_intelligence = importlib.import_module("frontend.pages.5_product_intelligence")
live_prediction = importlib.import_module("frontend.pages.2_live_prediction")
model_comparison = importlib.import_module("frontend.pages.4_model_comparison")

__all__ = ["about", "overview", "product_intelligence", "live_prediction", "model_comparison"]

