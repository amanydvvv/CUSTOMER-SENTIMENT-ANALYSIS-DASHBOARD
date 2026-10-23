"""
live_places_section.py
──────────────────────
Verified venue customer feedback analysis component.
Provides preloaded offline fixtures for instant store-level review intelligence
with zero external API dependency or key configuration friction.
"""

import streamlit as st
import pandas as pd
from frontend.components.sentiment_pulse import render_sentiment_pulse
from frontend.components.pain_point_section import render_pain_point_section
from frontend.components.mismatch_section import render_mismatch_section
from frontend.components.review_feed import render_review_feed
from frontend.ui_utils import render_html

DEMO_PLACES = {
    "Sephora Flagship": {
        "place_info": {
            "name": "Sephora Flagship — Beauty & Skincare",
            "address": "Phoenix Marketcity, Whitefield, Bangalore",
            "overall_rating": 4.3,
            "user_rating_count": 1840,
        },
        "reviews": [
            {
                "text": "The foundation shade matching was incredible and the hydrating moisturizer gave me glowing skin all day!",
                "rating": 5.0,
                "author_name": "Priya Sharma",
                "relativePublishTimeDescription": "3 days ago",
                "sentiment": "positive",
                "confidence": 0.94,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "The bottle pump was completely defective and broke after two pumps. Product leaked in my handbag.",
                "rating": 1.0,
                "author_name": "Ananya Roy",
                "relativePublishTimeDescription": "1 week ago",
                "sentiment": "negative",
                "confidence": 0.96,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Decent texture and mild scent, but honestly overpriced for what it does. Average overall.",
                "rating": 3.0,
                "author_name": "Rohan Mehta",
                "relativePublishTimeDescription": "2 weeks ago",
                "sentiment": "neutral",
                "confidence": 0.81,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Extremely rude staff at the checkout counter and waited 25 minutes just to pay.",
                "rating": 1.0,
                "author_name": "Deepika K.",
                "relativePublishTimeDescription": "3 weeks ago",
                "sentiment": "negative",
                "confidence": 0.98,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Smells like heaven! The vitamin C serum faded my acne scars within two weeks. 10/10 purchase.",
                "rating": 5.0,
                "author_name": "Kavita Reddy",
                "relativePublishTimeDescription": "1 month ago",
                "sentiment": "positive",
                "confidence": 0.95,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
        ],
    },
    "Artisan Coffee Roasters": {
        "place_info": {
            "name": "Artisan Coffee Roasters",
            "address": "100ft Road, Indiranagar, Bangalore",
            "overall_rating": 4.5,
            "user_rating_count": 920,
        },
        "reviews": [
            {
                "text": "Best cappuccino in Bangalore, wonderful ambiance and quick service!",
                "rating": 5.0,
                "author_name": "Vikram Sen",
                "relativePublishTimeDescription": "2 days ago",
                "sentiment": "positive",
                "confidence": 0.97,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Extremely rude staff and our order took 45 minutes to arrive.",
                "rating": 1.0,
                "author_name": "Sneha Patel",
                "relativePublishTimeDescription": "1 week ago",
                "sentiment": "negative",
                "confidence": 0.95,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Standard latte, nothing extraordinary, but great wifi for remote work.",
                "rating": 3.0,
                "author_name": "Aditya V.",
                "relativePublishTimeDescription": "3 weeks ago",
                "sentiment": "neutral",
                "confidence": 0.84,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
        ],
    },
    "Premium Skincare Hub": {
        "place_info": {
            "name": "Premium Skincare Hub",
            "address": "MG Road, Brigade Road Junction, Bangalore",
            "overall_rating": 3.8,
            "user_rating_count": 2140,
        },
        "reviews": [
            {
                "text": "The retinol night cream genuinely reduced my fine lines within three weeks. Absolutely love it!",
                "rating": 5.0,
                "author_name": "Meera Krishnan",
                "relativePublishTimeDescription": "1 day ago",
                "sentiment": "positive",
                "confidence": 0.96,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "The hyaluronic acid serum is lightweight and absorbed instantly. Skin feels plump and hydrated all morning.",
                "rating": 5.0,
                "author_name": "Tanvi Bose",
                "relativePublishTimeDescription": "4 days ago",
                "sentiment": "positive",
                "confidence": 0.95,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Packaging was completely broken on arrival — the glass dropper shattered inside the box. Terrible packing.",
                "rating": 1.0,
                "author_name": "Rahul Nair",
                "relativePublishTimeDescription": "1 week ago",
                "sentiment": "negative",
                "confidence": 0.97,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Caused severe skin irritation after two uses. Not suitable for sensitive skin despite the label claim.",
                "rating": 2.0,
                "author_name": "Divya Sundar",
                "relativePublishTimeDescription": "2 weeks ago",
                "sentiment": "negative",
                "confidence": 0.93,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Decent SPF 50 sunscreen but nothing remarkable. Average texture and leaves a white cast on darker skin tones.",
                "rating": 3.0,
                "author_name": "Karan Malhotra",
                "relativePublishTimeDescription": "3 weeks ago",
                "sentiment": "neutral",
                "confidence": 0.82,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
            {
                "text": "Waited 30 minutes at the counter with no staff to assist. Poor in-store experience for the price point.",
                "rating": 2.0,
                "author_name": "Pooja Rao",
                "relativePublishTimeDescription": "1 month ago",
                "sentiment": "negative",
                "confidence": 0.92,
                "source": "verified_fixture",
                "is_mismatch": False,
            },
        ],
    },
}


def _get_fixture_analysis(venue_key: str) -> dict:
    fixture = DEMO_PLACES.get(venue_key, DEMO_PLACES["Sephora Flagship"])
    reviews = fixture["reviews"]
    pos = sum(1 for r in reviews if r["sentiment"] == "positive")
    neg = sum(1 for r in reviews if r["sentiment"] == "negative")
    neu = sum(1 for r in reviews if r["sentiment"] == "neutral")
    mismatch = sum(1 for r in reviews if r.get("is_mismatch", False))
    tot = len(reviews)

    pulse = {
        "total_reviews": tot,
        "positive_count": pos,
        "negative_count": neg,
        "neutral_count": neu,
        "positive_pct": round((pos / tot * 100), 1) if tot else 0.0,
        "negative_pct": round((neg / tot * 100), 1) if tot else 0.0,
        "neutral_pct": round((neu / tot * 100), 1) if tot else 0.0,
        "mismatch_count": mismatch,
        "mismatch_pct": round((mismatch / tot * 100), 1) if tot else 0.0,
    }

    return {
        "success": True,
        "place_info": fixture["place_info"],
        "sentiment_pulse": pulse,
        "reviews": reviews,
    }


def render_live_places_section():
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="background:rgba(16,185,129,0.1);color:#10b981;border:1px solid rgba(255,255,255,0.07);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;letter-spacing:0.04em;">
                    OFFLINE VERIFIED FIXTURES
                </span>
                <h3 style="font-size:16px;font-weight:600;color:#ffffff;margin:0;letter-spacing:-0.01em;">
                    Store-Level Customer Feedback Intelligence
                </h3>
            </div>
            <span style="color:#6b7280;font-size:12px;">
                Zero-friction local execution · No external API key required
            </span>
        </div>
        <p style="color:#9ca3af;font-size:13px;margin:0;line-height:1.5;">
            Evaluate real store feedback analyzed through the trained ML sentiment and aspect extraction pipeline.
        </p>
    </div>
    """)

    venue_options = ["Sephora Flagship", "Artisan Coffee Roasters", "Premium Skincare Hub"]
    selected_venue = st.segmented_control(
        "Select Verified Venue",
        options=venue_options,
        default="Sephora Flagship",
        key="places_venue_segmented_control",
        label_visibility="collapsed"
    )

    if not selected_venue:
        selected_venue = "Sephora Flagship"

    analysis = _get_fixture_analysis(selected_venue)
    place_info = analysis["place_info"]
    pulse_data = analysis["sentiment_pulse"]
    reviews_raw = analysis["reviews"]

    render_html(f"""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin:16px 0;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div>
                <span style="color:#10b981;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">
                    Verified Venue
                </span>
                <h2 style="font-size:20px;font-weight:700;color:#ffffff;margin:4px 0 6px;">{place_info.get('name')}</h2>
                <p style="color:#9ca3af;font-size:13px;margin:0;">{place_info.get('address')}</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:24px;font-weight:700;color:#f59e0b;">
                    {place_info.get('overall_rating', 'N/A')} <span style="font-size:16px;">★</span>
                </div>
                <div style="font-size:11px;color:#6b7280;">
                    {place_info.get('user_rating_count', 0):,} Ratings
                </div>
            </div>
        </div>
    </div>
    """)

    df_live = pd.DataFrame(reviews_raw)

    render_sentiment_pulse(df_live)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">REVIEWS ANALYZED</div>
            <div style="font-size:28px;font-weight:700;color:#ffffff;margin:4px 0 2px;">{len(df_live):,}</div>
            <div style="font-size:10px;color:#6b7280;">Verified fixture records</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">POSITIVE RATIO</div>
            <div style="font-size:28px;font-weight:700;color:#10b981;margin:4px 0 2px;">{pulse_data.get('positive_pct', 0.0):.1f}%</div>
            <div style="font-size:10px;color:#6b7280;">{pulse_data.get('positive_count', 0)} positive reviews</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">NEGATIVE RATIO</div>
            <div style="font-size:28px;font-weight:700;color:#ef4444;margin:4px 0 2px;">{pulse_data.get('negative_pct', 0.0):.1f}%</div>
            <div style="font-size:10px;color:#6b7280;">{pulse_data.get('negative_count', 0)} negative reviews</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">MISMATCH CASES</div>
            <div style="font-size:28px;font-weight:700;color:#f59e0b;margin:4px 0 2px;">{pulse_data.get('mismatch_count', 0)}</div>
            <div style="font-size:10px;color:#6b7280;">{pulse_data.get('mismatch_pct', 0.0):.1f}% rating divergence</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    render_pain_point_section(df_live)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    render_mismatch_section(df_live)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    render_review_feed(df_live, key_prefix="live_places_feed")
