from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

st.set_page_config(page_title="NEXORA | Customer Intelligence", page_icon="◈", layout="wide")

# Visual identity
st.markdown("""
<style>
:root { --ink:#17243a; --muted:#68778d; --line:#e6ebf2; --surface:#f5f7fb; --accent:#4768e8; }
.block-container {padding-top:1.7rem; padding-bottom:2.5rem; max-width:1440px;}
[data-testid="stMetric"] {background:white;border:1px solid var(--line);padding:16px 18px;border-radius:13px;}
[data-testid="stMetricLabel"] p {color:var(--muted);font-size:.82rem;}
[data-testid="stMetricValue"] {color:var(--ink);font-weight:700;}
section[data-testid="stSidebar"] {background:#f7f8fc;}
.hero {background:linear-gradient(115deg,#17243a,#293e68);padding:25px 28px;border-radius:16px;color:white;margin-bottom:20px;}
.hero h1 {color:white;font-size:2rem;margin:0 0 5px 0;}
.hero p {color:#dbe4f5;margin:0;font-size:.95rem;}
.eyebrow {text-transform:uppercase;letter-spacing:.12em;font-size:.7rem;font-weight:700;color:#aebfe8;margin-bottom:8px;}
.small-note {color:#68778d;font-size:.82rem;}
div[data-testid="stDataFrame"] {border:1px solid #e6ebf2;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / "data" / "synthetic_customers.csv"
MODULES = {
    "Core Workspace": "licenses_core_workspace",
    "Advanced Analytics": "licenses_advanced_analytics",
    "Collaboration": "licenses_collaboration",
    "Automation": "licenses_automation",
}

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["active_users"] = df["active_users"].astype(int)
    df["licensed_seats"] = df["licensed_seats"].astype(int)
    return df

@st.cache_resource
def build_model(df):
    features = ["segment", "industry", "contract_months", "licensed_seats", "active_seat_rate",
                "weekly_sessions", "feature_adoption_rate", "support_tickets_30d",
                "days_since_last_login", "usage_change_30d", "nps_score", "monthly_active_days"]
    cat = ["segment", "industry"]
    num = [c for c in features if c not in cat]
    prep = ColumnTransformer([
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                           ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat),
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                           ("scale", StandardScaler())]), num),
    ])
    clf = Pipeline([("prep", prep), ("model", RandomForestClassifier(
        n_estimators=220, min_samples_leaf=3, class_weight="balanced", random_state=42))])
    clf.fit(df[features], df["churn_next_90d"])
    return clf, features


def risk_label(p):
    if p >= .65: return "High"
    if p >= .35: return "Medium"
    return "Low"


def suggested_action(r):
    if r["days_since_last_login"] >= 14:
        return "Customer success check-in"
    if r["active_seat_rate"] < .4:
        return "Review license activation"
    if r["usage_change_30d"] < -.15:
        return "Investigate usage decline"
    if r["module_adoption_rate"] < .35:
        return "Offer module enablement"
    if r["support_tickets_30d"] >= 4:
        return "Review support friction"
    return "Share adoption opportunities"


df = load_data()
model, model_features = build_model(df)
df["risk_score"] = model.predict_proba(df[model_features])[:, 1]
df["risk"] = df["risk_score"].map(risk_label)
df["active_seat_rate_pct"] = df["active_seat_rate"] * 100

st.markdown("""
<div class="hero">
  <div class="eyebrow">B2B SaaS · Product adoption · Customer intelligence</div>
  <h1>NEXORA <span style="color:#9db2ff">/</span> Customer Intelligence</h1>
  <p>Turn product usage signals into a prioritized customer-success and commercial action plan.</p>
</div>
""", unsafe_allow_html=True)
st.caption("Independent portfolio prototype · Fictional company · 120 synthetic customer accounts · No real customer or company data")

with st.sidebar:
    st.markdown("### Portfolio filters")
    segments = sorted(df["segment"].unique())
    selected_segments = st.multiselect("Customer segment", segments, default=segments)
    selected_risks = st.multiselect("Risk level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    st.divider()
    st.markdown("**About this demo**")
    st.caption("All values are simulated. The risk model is illustrative and is not validated for real customer decisions.")

view = df[df["segment"].isin(selected_segments) & df["risk"].isin(selected_risks)].copy()
if view.empty:
    st.info("No accounts match these filters. Adjust the selections in the sidebar.")
    st.stop()

# Portfolio KPIs
st.markdown("#### Portfolio at a glance")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Customer companies", f"{len(view):,}")
k2.metric("Licensed seats", f"{view.licensed_seats.sum():,}")
k3.metric("Active users", f"{view.active_users.sum():,}")
k4.metric("Seat activation", f"{view.active_users.sum()/max(view.licensed_seats.sum(),1):.1%}")
k5.metric("High-risk accounts", f"{(view.risk=='High').sum():,}", f"{(view.risk=='High').mean():.1%} of filtered base")

# License mix
st.markdown("#### License portfolio and product adoption")
left,right = st.columns([1,1.25])
with left:
    module_rows=[]
    for module,col in MODULES.items():
        module_rows.append({"Module":module,"Licensed seats":int(view[col].sum())})
    module_df=pd.DataFrame(module_rows).sort_values("Licensed seats",ascending=True)
    fig=px.bar(module_df,x="Licensed seats",y="Module",orientation="h",text="Licensed seats",
               color="Licensed seats",color_continuous_scale=["#cbd5f3","#4768e8"])
    fig.update_layout(height=300,margin=dict(l=0,r=5,t=10,b=0),coloraxis_showscale=False,
                      xaxis_title="Number of licensed seats",yaxis_title="")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig,use_container_width=True)
with right:
    fig2=px.scatter(view,x="active_seat_rate",y="module_adoption_rate",size="licensed_seats",color="risk",
                    hover_name="customer_id",color_discrete_map={"High":"#d95f59","Medium":"#e3ad4e","Low":"#4a9b82"},
                    labels={"active_seat_rate":"Active seats / licenses","module_adoption_rate":"Module adoption","risk":"Risk"})
    fig2.update_layout(height=300,margin=dict(l=0,r=5,t=10,b=0),xaxis_tickformat=".0%",yaxis_tickformat=".0%")
    st.plotly_chart(fig2,use_container_width=True)

# Usage insights
st.markdown("#### Usage and engagement")
u1,u2,u3=st.columns(3)
u1.metric("Avg. weekly sessions",f"{view.weekly_sessions.mean():.1f}")
u2.metric("Avg. active days / month",f"{view.monthly_active_days.mean():.1f}")
u3.metric("Avg. module adoption",f"{view.module_adoption_rate.mean():.1%}")
feature_counts=view["most_used_feature"].value_counts().rename_axis("Feature").reset_index(name="Customer accounts")
fig3=px.bar(feature_counts,x="Customer accounts",y="Feature",orientation="h",text="Customer accounts",
            color_discrete_sequence=["#647fe7"])
fig3.update_layout(height=270,margin=dict(l=0,r=10,t=5,b=0),yaxis_title="",xaxis_title="Accounts where this is the most-used feature")
fig3.update_traces(textposition="outside")
st.plotly_chart(fig3,use_container_width=True)

# Prioritization
st.markdown("#### Accounts to review")
priority=view.sort_values("risk_score",ascending=False).copy()
priority["Next best action"]=priority.apply(suggested_action,axis=1)
show=priority[["customer_id","segment","risk","licensed_seats","active_users","active_seat_rate","weekly_sessions","usage_change_30d","risk_score","Next best action"]].rename(columns={
    "customer_id":"Account","segment":"Segment","risk":"Risk","licensed_seats":"Licenses","active_users":"Active users",
    "active_seat_rate":"Seat activation","weekly_sessions":"Sessions / week","usage_change_30d":"Usage change (30d)","risk_score":"Illustrative score"})
st.dataframe(show,use_container_width=True,hide_index=True,column_config={
    "Seat activation":st.column_config.NumberColumn(format="%.0%%"),
    "Usage change (30d)":st.column_config.NumberColumn(format="%+.0%%"),
    "Illustrative score":st.column_config.ProgressColumn(min_value=0,max_value=1,format="%.0%%")})

st.markdown("#### Account detail")
account=st.selectbox("Choose a fictional customer account",priority.customer_id.tolist())
r=priority[priority.customer_id==account].iloc[0]
a,b,c,d=st.columns(4)
a.metric("Risk band",r.risk)
b.metric("Licensed seats",int(r.licensed_seats))
c.metric("Active users",int(r.active_users))
d.metric("Weekly sessions",int(r.weekly_sessions))
st.info(f"**Suggested human follow-up:** {suggested_action(r)}")
module_detail=pd.DataFrame([{"Module":m,"Licenses":int(r[col])} for m,col in MODULES.items() if int(r[col])>0])
st.write("**Licensed modules for this account**")
st.dataframe(module_detail,use_container_width=True,hide_index=True)
st.caption(f"Most-used feature: {r.most_used_feature} · Last login: {int(r.days_since_last_login)} days ago · Support tickets (30d): {int(r.support_tickets_30d)}")

with st.expander("Methodology, assumptions and limitations"):
    st.markdown("""
    - **Synthetic dataset:** 120 fictional companies. Company names, license allocations, users, usage patterns and outcomes are simulated.
    - **Risk score:** Random Forest trained on a simulated 90-day churn label. It demonstrates a machine-learning workflow; it is not a validated forecast.
    - **Recommendations:** transparent business rules based on usage and support indicators. No messages are sent and no CRM is updated.
    - **Human oversight:** recommendations are prompts for investigation, not automated decisions.
    - **Real deployment:** would require authorized historical data, temporal validation, calibration, monitoring, privacy/security review and approval from the data owner.
    """)

st.divider()
st.caption("NEXORA is an independent fictional portfolio case inspired by common B2B SaaS product-adoption and customer-monitoring challenges. It is not an Eliis product and does not contain Eliis data.")
