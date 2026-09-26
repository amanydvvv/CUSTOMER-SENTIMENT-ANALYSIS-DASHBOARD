"""
aspect_analyzer.py
──────────────────
Transparent, explainable rule-based aspect and pain-point intelligence engine.
Maps text tokens into key customer experience dimensions and derives actionable recommendations.
"""

from typing import Dict, Any, List

ASPECT_KEYWORDS = {
    "Product Quality": [
        "quality", "defect", "defective", "broke", "broken", "durability", "durable",
        "material", "cheaply", "smell", "scent", "fragrance", "texture", "formula",
        "allergic", "rash", "irritation", "burn", "reaction", "greasy", "sticky",
        "effective", "hydrat", "smooth", "soft", "shine", "moisture", "works well", "results"
    ],
    "Delivery": [
        "deliver", "delivery", "shipping", "shipped", "arrived", "late", "delay",
        "delayed", "carrier", "transit", "received", "days", "weeks", "lost", "missing package"
    ],
    "Packaging": [
        "packaging", "bottle", "pump", "cap", "seal", "unsealed", "leak", "leaking",
        "spill", "spray", "jar", "container", "crushed", "broken bottle", "dispenser"
    ],
    "Customer Service": [
        "customer service", "support", "refund", "return", "returned", "seller",
        "contact", "response", "reply", "replace", "replacement", "warranty", "policy"
    ],
    "Price & Value": [
        "price", "expensive", "overpriced", "cost", "cheap", "worth", "money",
        "value", "dollar", "affordable", "deal", "waste of money", "rip off", "bargain"
    ],
    "Usability & Application": [
        "easy to use", "hard to use", "difficult", "application", "apply", "instructions",
        "heavy", "absorb", "absorption", "messy", "clean"
    ],
    "Performance": [
        "perform", "performance", "long lasting", "hold", "coverage", "fade", "lifespan"
    ]
}

ISSUE_RULES = [
    # Delivery issues
    {"aspect": "Delivery", "issue": "Shipping Delay", "keywords": ["late", "delay", "delayed", "took weeks", "never arrived", "slow shipping"]},
    {"aspect": "Delivery", "issue": "Damaged in Transit", "keywords": ["damaged package", "crushed box", "battered", "transit damage"]},
    # Packaging issues
    {"aspect": "Packaging", "issue": "Defective Pump / Dispenser", "keywords": ["pump broke", "pump doesn't work", "cannot spray", "clogged pump", "dispenser"]},
    {"aspect": "Packaging", "issue": "Leaking / Broken Seal", "keywords": ["leaked", "leaking", "spilled", "seal broken", "unsealed", "open cap"]},
    # Quality issues
    {"aspect": "Product Quality", "issue": "Adverse Skin Reaction", "keywords": ["rash", "allergic", "reaction", "burn", "burning", "breakout", "itchy", "irritation"]},
    {"aspect": "Product Quality", "issue": "Poor Formula Quality", "keywords": ["cheap", "poor quality", "useless", "terrible", "waste of money", "did not work", "awful smell", "expired"]},
    {"aspect": "Product Quality", "issue": "High Quality & Efficacy", "keywords": ["great quality", "fantastic", "amazing results", "soft skin", "love the smell", "works wonders"]},
    # Service issues
    {"aspect": "Customer Service", "issue": "Unresponsive Support", "keywords": ["no response", "never replied", "ignored", "bad service", "rude"]},
    {"aspect": "Customer Service", "issue": "Return / Refund Friction", "keywords": ["refused refund", "cannot return", "return hassle", "no refund"]},
    # Price issues
    {"aspect": "Price & Value", "issue": "Overpriced / Low Value", "keywords": ["overpriced", "not worth the money", "too expensive", "waste of money"]},
    {"aspect": "Price & Value", "issue": "Great Value for Money", "keywords": ["great price", "great value", "worth every penny", "affordable", "bargain"]},
]


def extract_aspects_and_issues(text: str, sentiment: str = "neutral", rating: float = 3.0) -> Dict[str, Any]:
    """
    Analyzes review text to detect:
    - Primary and secondary aspects
    - Specific pain-point issue type
    - Priority (HIGH, MEDIUM, LOW)
    - Actionable business recommendation
    """
    text_lower = str(text).lower()

    # 1. Detect aspects by keyword presence
    detected_aspects = []
    for aspect, kws in ASPECT_KEYWORDS.items():
        if any(kw in text_lower for kw in kws):
            detected_aspects.append(aspect)

    primary_aspect = detected_aspects[0] if detected_aspects else "Product Quality"

    # 2. Detect specific issue
    detected_issue = "General Feedback"
    for rule in ISSUE_RULES:
        if any(kw in text_lower for kw in rule["keywords"]):
            detected_issue = rule["issue"]
            primary_aspect = rule["aspect"]
            if primary_aspect not in detected_aspects:
                detected_aspects.insert(0, primary_aspect)
            break

    # 3. Determine Priority
    is_negative = sentiment.lower() == "negative" or (rating is not None and rating <= 2.0)
    is_positive = sentiment.lower() == "positive" or (rating is not None and rating >= 4.0)

    if is_negative:
        if any(term in text_lower for term in ["rash", "allergic", "burn", "broken", "danger", "terrible", "leaked", "fraud", "never arrived"]):
            priority = "HIGH"
        else:
            priority = "MEDIUM"
    elif is_positive:
        priority = "LOW"
    else:
        priority = "LOW"

    # 4. Actionable Business Recommendations
    if is_negative:
        if primary_aspect == "Delivery":
            action = "Audit carrier logistics & fulfillment time to reduce transit delays."
        elif primary_aspect == "Packaging":
            action = "Inspect bottle cap sealing integrity and pump mechanism quality."
        elif primary_aspect == "Customer Service":
            action = "Streamline customer support response protocol and return processing."
        elif primary_aspect == "Price & Value":
            action = "Review pricing tier positioning and emphasize cost-benefit value propositions."
        elif "Reaction" in detected_issue or any(w in text_lower for w in ["rash", "burn", "allergic"]):
            action = "Escalate to QA team to audit batch formulation and allergen warnings."
        else:
            action = "Review recurring product quality complaints and conduct batch inspection."
    elif is_positive:
        if primary_aspect == "Product Quality":
            action = "Leverage high customer praise in brand testimonials and ad creatives."
        elif primary_aspect == "Price & Value":
            action = "Promote high-value bundles and customer loyalty rewards."
        else:
            action = "Maintain consistent quality standards and inventory fulfillment."
    else:
        action = "Monitor feedback trends for emerging customer sentiment shifts."

    return {
        "primary_aspect": primary_aspect,
        "all_aspects": detected_aspects if detected_aspects else ["General"],
        "issue": detected_issue,
        "priority": priority,
        "suggested_action": action
    }
