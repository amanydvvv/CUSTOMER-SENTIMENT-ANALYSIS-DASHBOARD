"""
pain_point_section.py
─────────────────────
Customer Pain-Point Analytics & Top Concerns component.
Transforms negative reviews into:
Aspect → Detected Issue → Priority → Recommended Action
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
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                PAIN-POINT INTELLIGENCE
            </div>
            <div style="color:#10b981;font-size:13px;">No negative customer complaints detected in the active filter selection.</div>
        </div>
        """)
        return

    aspect_summary, aspect_issues, high_pri_cnt = analyze_negative_aspects(neg_reviews)

    if not aspect_summary:
        st.info("No pain points extracted.")
        return

    # ── 1. TOP CUSTOMER CONCERNS (Ranked Visualization) ─────────────────────────
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                TOP CUSTOMER CONCERNS
            </span>
            <span style="font-size:11px;color:#6b7280;">
                Where negative feedback is concentrated
            </span>
        </div>
        <div style="font-size:13px;color:#d1d5db;margin-bottom:12px;">
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
        color_continuous_scale=[[0, "#3b82f6"], [0.5, "#f59e0b"], [1, "#ef4444"]],
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#ffffff", size=11),
        marker=dict(line=dict(width=0))
    )
    fig.update_layout(
        height=max(180, len(aspect_summary) * 38),
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", tickfont=dict(color="#ffffff", size=11), title=""),
        xaxis=dict(showgrid=True, gridcolor="#1e2533", tickfont=dict(color="#9ca3af", size=10), range=[0, max(df_chart['share_pct'].max() * 1.35, 10)], title="% of Negative Feedback")
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    # ── 2. PAIN-POINT INTELLIGENCE (Aspect Detail Breakdown) ─────────────────────
    render_html(f"""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                PAIN-POINT INTELLIGENCE
            </span>
            <span style="font-size:11px;color:#ef4444;background:rgba(239,68,68,0.12);padding:2px 8px;border-radius:4px;border:1px solid rgba(239,68,68,0.3);font-weight:600;">
                {total_neg:,} Negative Reviews
            </span>
        </div>
        <div style="font-size:13px;color:#d1d5db;margin-bottom:14px;">
            Empirical breakdown of customer complaint themes, severity priority, and suggested business interventions
        </div>
    </div>
    """)

    top_aspects = aspect_summary[:4]
    cols = st.columns(2)

    for i, item in enumerate(top_aspects):
        pri_col = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}.get(item["priority"], "#9ca3af")
        pri_bg = {"HIGH": "rgba(239,68,68,0.12)", "MEDIUM": "rgba(245,158,11,0.12)", "LOW": "rgba(16,185,129,0.12)"}.get(item["priority"], "#181b21")
        pri_bdr = {"HIGH": "rgba(239,68,68,0.3)", "MEDIUM": "rgba(245,158,11,0.3)", "LOW": "rgba(16,185,129,0.3)"}.get(item["priority"], "rgba(255,255,255,0.07)")

        with cols[i % 2]:
            render_html(f"""
            <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:13px;font-weight:600;color:#ffffff;text-transform:uppercase;letter-spacing:0.02em;">
                        {item['aspect']}
                    </span>
                    <span style="background:{pri_bg};color:{pri_col};border:1px solid {pri_bdr};padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">
                        {item['priority']} PRIORITY
                    </span>
                </div>
                <div style="display:flex;gap:12px;font-size:12px;color:#9ca3af;margin-bottom:8px;">
                    <span><b>Volume:</b> <span style="color:#ffffff;">{item['count']:,} reviews</span></span>
                    <span><b>Share:</b> <span style="color:#ef4444;">{item['share_pct']:.1f}%</span></span>
                </div>
                <div style="font-size:12px;color:#d1d5db;margin-bottom:8px;">
                    <b style="color:#9ca3af;">Detected Issue:</b> {item['issue']}
                </div>
                <div style="background:#181b21;border-left:3px solid #10b981;padding:8px 10px;border-radius:0 4px 4px 0;font-size:11px;color:#9ca3af;">
                    <b style="color:#ffffff;">Suggested Action:</b> {item['action']}
                </div>
            </div>
            """)

    # ── 3. AREAS TO INVESTIGATE (Action Priority List) ───────────────────────────
    top_3 = aspect_summary[:3]
    investigate_header = """
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
            AREAS TO INVESTIGATE — RECOMMENDED NEXT STEPS
        </div>
        <div style="font-size:13px;color:#d1d5db;margin-bottom:12px;">
            Key dimensions accounting for the highest concentrations of negative feedback:
        </div>
    """
    render_html(investigate_header)

    for rank, item in enumerate(top_3, 1):
        item_html = f"""
        <div style="display:flex;align-items:flex-start;gap:12px;background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;margin-bottom:8px;">
            <div style="background:rgba(255,255,255,0.08);color:#ffffff;border:1px solid rgba(255,255,255,0.15);font-weight:700;font-size:11px;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                {rank}
            </div>
            <div style="flex-grow:1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
                    <b style="color:#ffffff;font-size:13px;">{item['aspect']}</b>
                    <span style="color:#ef4444;font-size:11px;font-weight:600;">{item['count']:,} negative reviews ({item['share_pct']:.1f}%)</span>
                </div>
                <div style="color:#9ca3af;font-size:12px;line-height:1.4;">
                    <b>Focus:</b> {item['issue']} — <i>{item['action']}</i>
                </div>
            </div>
        </div>
        """
        render_html(item_html)

    render_html("""
        <div style="font-size:11px;color:#6b7280;margin-top:8px;">
            Prioritizing remediation in these top areas addresses the majority of customer friction identified in this review set.
        </div>
    </div>
    """)
