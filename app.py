from pathlib import Path
import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="NEXORA | Customer Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown("""
<style>
:root { --ink:#17243a; --muted:#68778d; --line:#e6ebf2; --accent:#4768e8; }
.block-container {padding-top:1.5rem;padding-bottom:2.4rem;max-width:1480px;}
section[data-testid="stSidebar"] {background:#f6f8fc;border-right:1px solid #e8edf5;}
.hero {background:linear-gradient(115deg,#17243a 0%,#293e68 72%,#3b5590 100%);
padding:28px 30px;border-radius:18px;color:white;margin-bottom:12px;}
.hero h1 {color:white;font-size:2.15rem;margin:0 0 8px 0;letter-spacing:-.03em;}
.hero p {color:#e0e8f8;margin:0;font-size:1rem;max-width:850px;}
.eyebrow {text-transform:uppercase;letter-spacing:.13em;font-size:.68rem;
font-weight:800;color:#b8c8f2;margin-bottom:10px;}
.section-note {color:#718096;font-size:.86rem;margin-top:-8px;}
div[data-testid="stMetric"] {background:white;border:1px solid #e6ebf2;
padding:15px 17px;border-radius:14px;min-height:108px;}
div[data-testid="stMetricLabel"] p {color:#68778d;font-size:.8rem;}
div[data-testid="stMetricValue"] {color:#17243a;font-weight:750;}
div[data-testid="stDataFrame"] {border:1px solid #e6ebf2;border-radius:12px;}
div.stButton > button {border-radius:9px;}
.pill {display:inline-block;padding:4px 9px;border-radius:999px;background:#eef2ff;
color:#3f57b7;font-size:.75rem;font-weight:700;margin-right:5px;}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / "data" / "synthetic_customers.csv"
MODULES = {
    "Core Workspace": "licenses_core_workspace",
    "Advanced Analytics": "licenses_advanced_analytics",
    "Collaboration": "licenses_collaboration",
    "Automation": "licenses_automation",
}
FEATURES = [
    "segment", "industry", "contract_months", "licensed_seats", "active_seat_rate",
    "weekly_sessions", "feature_adoption_rate", "support_tickets_30d",
    "days_since_last_login", "usage_change_30d", "nps_score", "monthly_active_days",
]

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    required = set(FEATURES + list(MODULES.values()) + [
        "customer_id", "active_users", "module_adoption_rate", "most_used_feature"
    ])
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required fields: {', '.join(sorted(missing))}")
    if data.empty:
        raise ValueError("The synthetic dataset is empty.")
    if (data["active_users"] > data["licensed_seats"]).any():
        raise ValueError("Dataset validation failed: active users exceed licensed seats.")
    return data

def calculate_health(row):
    """Transparent heuristic index (0-100); not a churn probability."""
    components = {
        "seat_activation": min(max(float(row["active_seat_rate"]), 0), 1) * 25,
        "usage_frequency": min(max(float(row["weekly_sessions"]) / 20, 0), 1) * 20,
        "feature_adoption": min(max(float(row["module_adoption_rate"]), 0), 1) * 20,
        "usage_trend": min(max((float(row["usage_change_30d"]) + .5) / 1.0, 0), 1) * 15,
        "recency": (1 - min(max(float(row["days_since_last_login"]) / 30, 0), 1)) * 10,
        "support_load": (1 - min(max(float(row["support_tickets_30d"]) / 10, 0), 1)) * 5,
        "customer_sentiment": min(max(float(row["nps_score"]) / 100, 0), 1) * 5,
    }
    return round(sum(components.values()), 1)

def health_band(score):
    if score < 45:
        return "Needs attention"
    if score < 70:
        return "Watch"
    return "Healthy"

def risk_label(score):
    return {"Needs attention": "High", "Watch": "Medium", "Healthy": "Low"}[health_band(score)]

def suggested_action(row):
    actions = []
    if row["days_since_last_login"] >= 14:
        actions.append("Schedule a customer-success check-in")
    if row["active_seat_rate"] < .4:
        actions.append("Review license activation and onboarding")
    if row["usage_change_30d"] < -.15:
        actions.append("Investigate the recent usage decline")
    if row["module_adoption_rate"] < .35:
        actions.append("Offer targeted module enablement")
    if row["support_tickets_30d"] >= 4:
        actions.append("Review open support friction")
    if not actions:
        actions.append("Explore advanced-feature adoption opportunities")
    return actions

def get_api_key():
    try:
        return st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    except Exception:
        return os.getenv("OPENAI_API_KEY", "")

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the portfolio dataset: {exc}")
    st.stop()

df["health_score"] = df.apply(calculate_health, axis=1)
df["health_status"] = df["health_score"].apply(health_band)
df["risk"] = df["health_status"].map({
    "Needs attention": "High", "Watch": "Medium", "Healthy": "Low"
})
df["next_actions"] = df.apply(suggested_action, axis=1)
df["active_seat_rate_pct"] = df["active_seat_rate"] * 100

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">Independent portfolio case · B2B SaaS · Product analytics · AI-assisted decision support</div>
  <h1>NEXORA <span style="color:#aebfff">/</span> Customer Intelligence</h1>
  <p>Turn product-usage signals into a clearer view of customer adoption, account health and prioritized human follow-up.</p>
</div>
""", unsafe_allow_html=True)
st.caption("Fictional company · 120 synthetic customer accounts · No real customer, employer or research data")

# ---------- Filters ----------
with st.sidebar:
    st.markdown("## Portfolio controls")
    segments = sorted(df["segment"].unique().tolist())
    selected_segments = st.multiselect("Customer segment", segments, default=segments)
    selected_status = st.multiselect(
        "Account health", ["Needs attention", "Watch", "Healthy"],
        default=["Needs attention", "Watch", "Healthy"]
    )
    st.divider()
    st.markdown("**How to read this demo**")
    st.caption("Health is a transparent heuristic index, not a probability of churn. All records are synthetic.")
    if st.button("Reset filters", use_container_width=True):
        st.rerun()

view = df[df["segment"].isin(selected_segments) & df["health_status"].isin(selected_status)].copy()
if view.empty:
    st.warning("No accounts match the selected filters. Adjust the filters to continue.")
    st.stop()

# ---------- Executive overview ----------
st.markdown("### Portfolio overview")
st.markdown('<div class="section-note">A compact view of customer scale, license activation and account health.</div>', unsafe_allow_html=True)
total_seats = int(view["licensed_seats"].sum())
active_users = int(view["active_users"].sum())
activation = active_users / max(total_seats, 1)
attention = int((view["health_status"] == "Needs attention").sum())
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Customer accounts", f"{len(view):,}")
k2.metric("Licensed seats", f"{total_seats:,}")
k3.metric("Active users", f"{active_users:,}")
k4.metric("Seat activation", f"{activation:.1%}")
k5.metric("Needs attention", f"{attention:,}", f"{attention/max(len(view),1):.1%} of filtered base")

left, right = st.columns([1, 1.25])
with left:
    st.markdown("#### License allocation")
    module_data = pd.DataFrame([
        {"Module": label, "Licensed seats": int(view[column].sum())}
        for label, column in MODULES.items()
    ]).sort_values("Licensed seats", ascending=True)
    fig = px.bar(module_data, x="Licensed seats", y="Module", orientation="h",
                 text="Licensed seats", color="Licensed seats",
                 color_continuous_scale=["#cbd5f3", "#4768e8"])
    fig.update_layout(height=320, margin=dict(l=0,r=10,t=10,b=0),
                      coloraxis_showscale=False, xaxis_title="Licensed seats", yaxis_title="")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Adoption and account health")
    fig = px.scatter(
        view, x="active_seat_rate", y="module_adoption_rate",
        size="licensed_seats", color="health_status", hover_name="customer_id",
        color_discrete_map={"Needs attention":"#d96a64","Watch":"#e0ad4e","Healthy":"#4b9b83"},
        labels={"active_seat_rate":"Seat activation","module_adoption_rate":"Module adoption",
                "health_status":"Account health"},
        size_max=26,
    )
    fig.update_layout(height=320, margin=dict(l=0,r=10,t=10,b=0),
                      xaxis_tickformat=".0%", yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Usage signals ----------
st.markdown("### Usage and engagement signals")
m1,m2,m3,m4 = st.columns(4)
m1.metric("Avg. weekly sessions", f"{view.weekly_sessions.mean():.1f}")
m2.metric("Avg. active days / month", f"{view.monthly_active_days.mean():.1f}")
m3.metric("Avg. module adoption", f"{view.module_adoption_rate.mean():.1%}")
m4.metric("Avg. usage change (30d)", f"{view.usage_change_30d.mean():+.1%}")
feat = view["most_used_feature"].value_counts().rename_axis("Feature").reset_index(name="Accounts")
fig = px.bar(feat, x="Accounts", y="Feature", orientation="h", text="Accounts",
             color_discrete_sequence=["#647fe7"])
fig.update_layout(height=270, margin=dict(l=0,r=10,t=5,b=0), yaxis_title="",
                  xaxis_title="Accounts by most-used feature")
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# ---------- Priority accounts ----------
st.markdown("### Accounts to review")
st.markdown('<div class="section-note">Prioritized by the lowest health index. Scores are heuristic and intended to support human review.</div>', unsafe_allow_html=True)
priority = view.sort_values("health_score", ascending=True).copy()
table = priority[[
    "customer_id","segment","health_status","health_score","licensed_seats",
    "active_users","active_seat_rate","usage_change_30d","days_since_last_login"
]].rename(columns={
    "customer_id":"Account","segment":"Segment","health_status":"Health",
    "health_score":"Health index","licensed_seats":"Licenses","active_users":"Active users",
    "active_seat_rate":"Seat activation","usage_change_30d":"Usage change (30d)",
    "days_since_last_login":"Days since login"
})
st.dataframe(table, use_container_width=True, hide_index=True,
             column_config={
                 "Health index": st.column_config.ProgressColumn(min_value=0,max_value=100,format="%.0f/100"),
                 "Seat activation": st.column_config.NumberColumn(format="%.0%%"),
                 "Usage change (30d)": st.column_config.NumberColumn(format="%+.0%%"),
             })
selected_account = st.selectbox("Explore an account", priority["customer_id"].tolist())
account = priority[priority["customer_id"] == selected_account].iloc[0]
with st.container(border=True):
    st.markdown(f"#### {account['customer_id']} · {account['segment']}")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Health index", f"{account['health_score']:.0f}/100")
    c2.metric("Seat activation", f"{account['active_seat_rate']:.1%}")
    c3.metric("Module adoption", f"{account['module_adoption_rate']:.1%}")
    c4.metric("Days since login", f"{int(account['days_since_last_login'])}")
    st.markdown("**Suggested human follow-up**")
    for action in account["next_actions"]:
        st.markdown(f"- {action}")
    st.caption("These are prompts for investigation, not automated decisions.")

# ---------- AI assistant ----------
st.markdown("### Ask NEXORA")
st.markdown('<div class="section-note">Optional natural-language exploration of the currently filtered synthetic portfolio.</div>', unsafe_allow_html=True)
api_key = get_api_key()
if not api_key:
    st.info("The dashboard works without an API key. To enable the AI assistant, add OPENAI_API_KEY in Streamlit Cloud → App settings → Secrets.")
    with st.expander("Example questions"):
        st.markdown("- Which segment has the lowest adoption?\n- Which accounts should the team review first?\n- What signals are common among accounts needing attention?")
else:
    if "nexora_history" not in st.session_state:
        st.session_state.nexora_history = []
    for msg in st.session_state.nexora_history[-8:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("Ask about adoption, usage, account health or priorities...")
    if question:
        st.session_state.nexora_history.append({"role":"user","content":question})
        context_df = view.sort_values("health_score").head(20)
        context = {
            "filtered_account_count": int(len(view)),
            "segment_summary": view.groupby("segment").agg(
                accounts=("customer_id","count"),
                avg_activation=("active_seat_rate","mean"),
                avg_adoption=("module_adoption_rate","mean"),
                avg_usage_change=("usage_change_30d","mean")
            ).round(3).reset_index().to_dict("records"),
            "priority_accounts": context_df[[
                "customer_id","segment","health_status","health_score",
                "active_seat_rate","module_adoption_rate","usage_change_30d",
                "days_since_last_login","next_actions"
            ]].to_dict("records"),
            "note": "All records are synthetic. Health index is a heuristic, not a churn probability."
        }
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Reviewing the selected portfolio..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        instructions=(
                            "You are NEXORA's analytical assistant for a fictional B2B SaaS portfolio. "
                            "Answer in the user's language. Use only the supplied JSON context. "
                            "Do not invent account facts, metrics or causes. Distinguish observations "
                            "from hypotheses. Explain that the health index is heuristic, not a "
                            "validated churn prediction. Recommend human review."
                        ),
                        input="Portfolio context:\n" + json.dumps(context, ensure_ascii=False) +
                              "\n\nUser question:\n" + question,
                        max_output_tokens=500,
                    )
                    answer = response.output_text.strip() or "No answer was generated from the available data."
                    st.markdown(answer)
                    st.session_state.nexora_history.append({"role":"assistant","content":answer})
                except Exception as exc:
                    st.error("The AI assistant could not complete this request. Check the API key, billing and quota.")
                    st.caption(f"Technical detail: {type(exc).__name__}")
    if st.button("Clear assistant conversation"):
        st.session_state.nexora_history = []
        st.rerun()

# ---------- Method and credibility ----------
with st.expander("Methodology, assumptions and limitations"):
    st.markdown("""
    **Data.** The dataset contains 120 generated fictional accounts. No real customer, employer,
    university or research data is included.

    **Health index.** A transparent weighted heuristic combines seat activation, usage frequency,
    feature adoption, usage trend, login recency, support load and a simulated sentiment indicator.
    The index is not a probability and has not been validated against real churn outcomes.

    **Recommendations.** The next-step suggestions are deterministic business rules. They are
    intended to help a human account owner decide what to investigate, not to automate a customer decision.

    **AI assistant.** When enabled, the language model receives an aggregate summary and a limited
    set of fictional account records from the active filters. It does not contact customers, modify
    licenses or write to a CRM.

    **Before real deployment.** Use authorized data, define business-specific success criteria,
    validate metrics with stakeholders, assess model quality over time, review privacy/security,
    monitor drift and retain human oversight.
    """)
st.divider()
st.caption(
    "NEXORA is an independent fictional portfolio case. Its problem framing is inspired by general "
    "B2B SaaS product-adoption and customer-monitoring challenges, but the implementation and data "
    "were created separately. It is not an Eliis product and does not represent an Eliis deployment."
)
