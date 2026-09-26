"""
pain_point_section.py
─────────────────────
Customer Pain-Point Analytics & Top Concerns component.
Transforms negative reviews into:
Aspect → Detected Issue → Priority → Recommended Action
Uses render_html from frontend.ui_utils to guarantee zero raw HTML leaks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui_utils import render_html
from frontend.components.aspect_analyzer import extract_aspects_and_issues


def analyze_negative_aspects(neg_reviews: pd.DataFrame):
    """
    Extracts aspects, issues, and priorities across negative reviews.
    Returns aggregated aspect data and specific issue breakdowns.
    """
    total_neg = len(neg_reviews)
    if total_neg == 0:
        return [], {}, 0

    # Sample for speed if large, maintaining deterministic output
    sample_neg = neg_reviews if total_neg <= 2500 else neg_reviews.sample(2500, random_state=42)
    sample_size = len(sample_neg)

    aspect_counts = {}
    aspect_issues = {}
    aspect_actions = {}
    high_priority_count = 0

    for _, row in sample_neg.iterrows():
        intel = extract_aspects_and_issues(str(row["text"]), sentiment="negative", rating=float(row.get("rating", 1.0)))
        p_aspect = intel["primary_aspect"]
        issue = intel["issue"]
        priority = intel["priority"]
        action = intel["suggested_action"]

        aspect_counts[p_aspect] = aspect_counts.get(p_aspect, 0) + 1

        if p_aspect not in aspect_issues:
            aspect_issues[p_aspect] = {}
        if issue != "General Feedback":
            aspect_issues[p_aspect][issue] = aspect_issues[p_aspect].get(issue, 0) + 1

        if p_aspect not in aspect_actions:
            aspect_actions[p_aspect] = action

        if priority == "HIGH":
            high_priority_count += 1

    aspect_summary = []
    for aspect, sample_cnt in sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True):
        share_pct = (sample_cnt / sample_size) * 100
        est_volume = int(round(total_neg * (share_pct / 100)))

        top_issue = "General Complaints"
        if aspect in aspect_issues and aspect_issues[aspect]:
            top_issue = max(aspect_issues[aspect].items(), key=lambda x: x[1])[0]

        if share_pct >= 20 or aspect in ["Product Quality", "Delivery"] and any(term in top_issue.lower() for term in ["reaction", "delay", "broken"]):
            pri = "HIGH"
        elif share_pct >= 10:
            pri = "MEDIUM"
        else:
            pri = "LOW"

        aspect_summary.append({
            "aspect": aspect,
            "count": est_volume,
            "share_pct": share_pct,
            "issue": top_issue,
            "priority": pri,
            "action": aspect_actions.get(aspect, "Review customer feedback and audit quality standards.")
        })

    return aspect_summary, aspect_issues, high_priority_count


def render_pain_point_section(df: pd.DataFrame):
    """
    Renders Top Customer Concerns, Pain-Point Intelligence cards, and Areas to Investigate.
    """
    neg_reviews = df[df["sentiment"] == "negative"]
    total_neg = len(neg_reviews)

    if total_neg == 0:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.25rem;">
            <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
                PAIN-POINT INTELLIGENCE
            </div>
            <div style="color:#22C55E;font-size:0.85rem;">No negative customer complaints detected in the active filter selection.</div>
        </div>
        """)
        return

    aspect_summary, aspect_issues, high_pri_cnt = analyze_negative_aspects(neg_reviews)

    if not aspect_summary:
        st.info("No pain points extracted.")
        return

    # ── 1. TOP CUSTOMER CONCERNS (Ranked Visualization) ─────────────────────────
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                TOP CUSTOMER CONCERNS
            </span>
            <span style="font-size:0.72rem;color:#98A2B3;">
                Where negative feedback is concentrated
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.75rem;">
            Relative share and volume of complaints across key customer experience dimensions
        </div>
    </div>
    """)

    df_chart = pd.DataFrame(aspect_summary)

    fig = px.bar(
        df_chart,
        x="share_pct",
        y="aspect",
        orientation="h",
        text=df_chart.apply(lambda r: f"{r['count']:,} reviews ({r['share_pct']:.1f}%)", axis=1),
        color="share_pct",
        color_continuous_scale=[[0, "#3B82F6"], [0.5, "#F59E0B"], [1, "#EF4444"]],
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#F5F7FA", size=11),
        marker=dict(line=dict(width=0))
    )
    fig.update_layout(
        height=max(180, len(aspect_summary) * 38),
        margin=dict(l=10, r=70, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", tickfont=dict(color="#F5F7FA", size=11), title=""),
        xaxis=dict(showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3", size=10), range=[0, max(df_chart['share_pct'].max() * 1.35, 10)], title="% of Negative Feedback")
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── 2. PAIN-POINT INTELLIGENCE (Aspect Detail Breakdown) ─────────────────────
    render_html(f"""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                PAIN-POINT INTELLIGENCE — WHAT ARE CUSTOMERS COMPLAINING ABOUT?
            </span>
            <span style="font-size:0.72rem;color:#EF4444;background:rgba(239,68,68,0.12);padding:2px 8px;border-radius:4px;border:1px solid rgba(239,68,68,0.3);font-weight:600;">
                {total_neg:,} Negative Reviews
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.9rem;">
            Empirical breakdown of customer complaint themes, severity priority, and suggested business interventions
        </div>
    </div>
    """)

    top_aspects = aspect_summary[:4]
    cols = st.columns(2)

    for i, item in enumerate(top_aspects):
        pri_col = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#22C55E"}.get(item["priority"], "#98A2B3")
        pri_bg = {"HIGH": "rgba(239,68,68,0.12)", "MEDIUM": "rgba(245,158,11,0.12)", "LOW": "rgba(34,197,94,0.12)"}.get(item["priority"], "#151A24")
        pri_bdr = {"HIGH": "rgba(239,68,68,0.3)", "MEDIUM": "rgba(245,158,11,0.3)", "LOW": "rgba(34,197,94,0.3)"}.get(item["priority"], "#242A35")

        with cols[i % 2]:
            render_html(f"""
            <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.9rem 1rem;margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                    <span style="font-size:0.85rem;font-weight:800;color:#F5F7FA;text-transform:uppercase;letter-spacing:0.04em;">
                        {item['aspect']}
                    </span>
                    <span style="background:{pri_bg};color:{pri_col};border:1px solid {pri_bdr};padding:2px 8px;border-radius:4px;font-size:0.68rem;font-weight:800;">
                        {item['priority']} PRIORITY
                    </span>
                </div>
                <div style="display:flex;gap:0.75rem;font-size:0.75rem;color:#98A2B3;margin-bottom:0.5rem;">
                    <span><b>Volume:</b> <span style="color:#F5F7FA;">{item['count']:,} reviews</span></span>
                    <span><b>Share of complaints:</b> <span style="color:#EF4444;">{item['share_pct']:.1f}%</span></span>
                </div>
                <div style="font-size:0.78rem;color:#D0D5DD;margin-bottom:0.55rem;">
                    <b style="color:#98A2B3;">Detected Issue:</b> {item['issue']}
                </div>
                <div style="background:#11151D;border-left:3px solid #7C5CFF;padding:0.4rem 0.65rem;border-radius:0 4px 4px 0;font-size:0.74rem;color:#98A2B3;">
                    <b style="color:#F5F7FA;">Suggested Action:</b> {item['action']}
                </div>
            </div>
            """)

    # ── 3. AREAS TO INVESTIGATE (Action Priority List) ───────────────────────────
    top_3 = aspect_summary[:3]
    investigate_header = """
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1rem;">
        <div style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
            AREAS TO INVESTIGATE — RECOMMENDED NEXT STEPS
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.75rem;">
            These areas account for the largest portions of negative feedback in the current dataset:
        </div>
    """
    render_html(investigate_header)

    for rank, item in enumerate(top_3, 1):
        item_html = f"""
        <div style="display:flex;align-items:flex-start;gap:0.85rem;background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.65rem 0.85rem;margin-bottom:0.5rem;">
            <div style="background:#7C5CFF;color:#fff;font-weight:800;font-size:0.75rem;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                {rank}
            </div>
            <div style="flex-grow:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
                    <b style="color:#F5F7FA;font-size:0.85rem;">{item['aspect']}</b>
                    <span style="color:#EF4444;font-size:0.75rem;font-weight:700;">{item['count']:,} negative reviews ({item['share_pct']:.1f}%)</span>
                </div>
                <div style="color:#98A2B3;font-size:0.76rem;line-height:1.4;">
                    <b>Focus:</b> {item['issue']} — <i>{item['action']}</i>
                </div>
            </div>
        </div>
        """
        render_html(item_html)

    render_html("""
        <div style="font-size:0.72rem;color:#667085;margin-top:0.4rem;">
            Prioritizing remediation in these top 3 areas addresses the majority of customer friction identified in this review set.
        </div>
    </div>
    """)
