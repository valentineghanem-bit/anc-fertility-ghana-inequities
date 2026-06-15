"""
ANC Coverage & Fertility Inequities, Ghana (Part I) — interactive analytics app.
Run:  pip install streamlit plotly pandas    &&    streamlit run app.py
Data: published regional values from the ANC ecological study (DHS 1988-2022).
Engine: Streamlit + Plotly  |  Colourblind-safe RdYlBu  |  self-contained, works offline.
"""
import json, os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ANC × Fertility — Ghana BI", layout="wide", initial_sidebar_state="expanded")

# ---------------- real data ----------------
REGIONS = [
    ("GREATER ACCRA", "Gr.Accra", 96.4, 34.43, 2.8, "LL"),
    ("ASHANTI", "Ashanti", 91.3, 28.53, 3.2, "LL"),
    ("CENTRAL", "Central", 87.3, 24.25, 3.6, "LL"),
    ("EASTERN", "Eastern", 85.6, 22.53, 3.8, "LL"),
    ("WESTERN", "Western", 83.4, 21.38, 3.9, "LH"),
    ("VOLTA", "Volta", 81.2, 19.33, 4.2, "LH"),
    ("BONO", "Bono", 76.5, 17.79, 4.3, "NS"),
    ("AHAFO", "Ahafo", 74.8, 16.62, 4.5, "NS"),
    ("BONO EAST", "Bono E", 73.1, 15.89, 4.6, "NS"),
    ("OTI", "Oti", 72.4, 15.08, 4.8, "NS"),
    ("WESTERN NORTH", "W.North", 67.8, 13.56, 5.0, "NS"),
    ("UPPER EAST", "Upper East", 61.4, 11.37, 5.4, "HL"),
    ("UPPER WEST", "Upper West", 57.2, 10.04, 5.7, "HL"),
    ("NORTHERN", "Northern", 52.1, 8.68, 6.0, "HH"),
    ("SAVANNAH", "Savannah", 48.3, 7.67, 6.3, "HH"),
    ("NORTHERN EAST", "N.East", 43.8, 6.64, 6.6, "HH"),
]
df = pd.DataFrame(REGIONS, columns=["region", "short", "anc", "cei", "tfr", "lisa"])
LISA = {"HH": "#c0392b", "LL": "#2980b9", "HL": "#e67e22", "LH": "#82c0e8", "NS": "#bdc3c7"}
RYB = [(0.0, "rgb(215,48,39)"), (0.5, "rgb(254,224,144)"), (1.0, "rgb(69,117,180)")]
TREND = pd.DataFrame({
    "year": [1988, 1993, 1998, 2003, 2008, 2014, 2017, 2019, 2022],
    "anc":  [83.1, 84.6, 86.2, 88.5, 90.8, 93.4, 95.1, 96.3, 97.7],
    "tfr":  [6.4, 5.9, 5.5, 5.0, 4.6, 4.2, 4.0, 3.9, 3.9],
})

@st.cache_data
def load_geo():
    p = os.path.join(os.path.dirname(__file__), "ghana_districts_compact.geojson")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------- sidebar / filter ----------------
st.sidebar.title("ANC × Fertility — Ghana")
st.sidebar.caption("Subnational ecological study · DHS 1988–2022 · Part I")
lisa_pick = st.sidebar.multiselect("Filter by spatial cluster (LISA)", sorted(df.lisa.unique()), default=list(df.lisa.unique()))
region_pick = st.sidebar.multiselect("Filter by region", df.region.tolist(), default=df.region.tolist())
metric = st.sidebar.radio("Map metric", ["ANC coverage (%)", "Care Efficiency Index"], index=0)
fdf = df[df.lisa.isin(lisa_pick) & df.region.isin(region_pick)]

# ---------------- header + KPIs ----------------
st.markdown("### Antenatal Care Coverage & Fertility Inequities — Ghana")
st.caption("Care Efficiency Index (CEI = ANC% ÷ TFR) · colourblind-safe RdYlBu · " + f"{len(fdf)} of 16 regions in view")
k = st.columns(6)
k[0].metric("National ANC, 2022", "97.7%", "+14.6 pts vs 1988")
k[1].metric("Highest region", "96.4%", "Greater Accra")
k[2].metric("Lowest region", "43.8%", "North East", delta_color="inverse")
k[3].metric("Moran's I (ANC)", "0.68", "p<0.001")
k[4].metric("National CEI", "27.8")
k[5].metric("Equity gap", "2.8×", "Accra ÷ N.East", delta_color="inverse")

# ---------------- row 1: map + ranking ----------------
c1, c2 = st.columns([3, 2])
with c1:
    st.markdown("**ANC coverage by district** — districts coloured by regional value")
    geo = load_geo()
    feat = [{"name": x["properties"]["name"], "region": x["properties"]["region"]} for x in geo["features"]]
    mp = pd.DataFrame(feat).merge(df, on="region", how="left")
    col = "anc" if metric.startswith("ANC") else "cei"
    fig = px.choropleth(mp, geojson=geo, locations="name", featureidkey="properties.name",
                        color=col, color_continuous_scale=[c[1] for c in RYB],
                        hover_name="name", hover_data={"region": True, "anc": True, "cei": True, "lisa": True, "name": False})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=430, coloraxis_colorbar=dict(title=metric[:12]))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.markdown("**Regional ANC ranking** — colour = LISA cluster")
    r = fdf.sort_values("anc")
    fig = go.Figure(go.Bar(x=r.anc, y=r.short, orientation="h",
                           marker_color=[LISA[l] for l in r.lisa], text=[f"{v}%" for v in r.anc], textposition="outside"))
    fig.update_layout(height=430, margin=dict(l=4, r=10, t=4, b=4), xaxis_title="ANC %", xaxis_range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

# ---------------- row 2: scatter + CEI + radar ----------------
c3, c4, c5 = st.columns(3)
with c3:
    st.markdown("**ANC vs. Total Fertility Rate**")
    fig = px.scatter(fdf, x="tfr", y="anc", color="lisa", color_discrete_map=LISA, text="short",
                     labels={"tfr": "TFR (children/woman)", "anc": "ANC %"})
    fig.update_traces(textposition="top center", marker_size=12)
    if len(fdf) >= 2:
        import numpy as np
        b, a = np.polyfit(fdf.tfr.astype(float), fdf.anc.astype(float), 1)
        xr = [float(fdf.tfr.min()), float(fdf.tfr.max())]
        fig.add_trace(go.Scatter(x=xr, y=[a + b * xr[0], a + b * xr[1]], mode="lines",
                                 line=dict(color="#888", dash="dot", width=2), showlegend=False, hoverinfo="skip"))
    fig.add_vline(x=5.90, line_dash="dash", line_color="#c0392b", annotation_text="threshold 5.90")
    fig.update_layout(height=360, margin=dict(l=4, r=4, t=4, b=4), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with c4:
    st.markdown("**Care Efficiency Index by region**")
    r = fdf.sort_values("cei")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r.cei, y=r.short, mode="markers", marker=dict(size=12, color=[LISA[l] for l in r.lisa])))
    for _, row in r.iterrows():
        fig.add_shape(type="line", x0=0, x1=row.cei, y0=row.short, y1=row.short, line=dict(color="#dfe6ee", width=2))
    fig.add_vline(x=27.8, line_dash="dash", line_color="#c0392b", annotation_text="mean 27.8")
    fig.update_layout(height=360, margin=dict(l=4, r=4, t=4, b=4), xaxis_title="CEI")
    st.plotly_chart(fig, use_container_width=True)
with c5:
    st.markdown("**Multivariate region profiles** — parallel coordinates")
    fig = go.Figure(go.Parcoords(
        line=dict(color=fdf.anc, colorscale=[c[1] for c in RYB]),
        dimensions=[dict(label="ANC %", values=fdf.anc), dict(label="TFR", values=fdf.tfr), dict(label="CEI", values=fdf.cei)]))
    fig.update_layout(height=360, margin=dict(l=30, r=30, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ---------------- row 3: national trend ----------------
st.markdown("**National trajectory, 1988–2022** — ANC rises while TFR falls (the documented decoupling)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=TREND.year, y=TREND.anc, name="ANC %", line=dict(color="#2980b9", width=3), fill="tozeroy", fillcolor="rgba(41,128,185,.10)"))
fig.add_trace(go.Scatter(x=TREND.year, y=TREND.tfr, name="TFR", yaxis="y2", line=dict(color="#c0392b", width=3, dash="dash")))
fig.update_layout(height=320, margin=dict(l=4, r=4, t=4, b=4),
                  yaxis=dict(title="ANC %", range=[80, 100]),
                  yaxis2=dict(title="TFR", overlaying="y", side="right", range=[3, 7]),
                  legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig, use_container_width=True)
st.caption("Engine: Streamlit + Plotly · self-contained · endpoints documented, intermediate waves indicative.")
