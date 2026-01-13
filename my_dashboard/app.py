import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Fishing Fleet Dashboard", layout="wide")

# ----------------------------
# Columns (EXACT from your file)
# ----------------------------
GEO  = "geo"
YEAR = "TIME_PERIOD"
VAL  = "OBS_VALUE"
UNIT = "unit"
GEAR = "gear"
ENG  = "eng_pow"

# ----------------------------
# Load (NO renames)
# ----------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df[YEAR] = pd.to_numeric(df[YEAR], errors="coerce")
    df[VAL]  = pd.to_numeric(df[VAL], errors="coerce")
    df = df[df[GEO].notna() & df[YEAR].notna() & df[UNIT].notna()].copy()
    return df

df = load_data("fishing_fleet.csv")

# ----------------------------
# State
# ----------------------------
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "BE"

# ----------------------------
# Helpers
# ----------------------------
def empty_fig(title: str, height: int = 360) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, margin=dict(l=50, r=20, t=55, b=45), height=height)
    return fig

# ----------------------------
# 1) MAIN / ONLY CLICKABLE CHART: % change in GT by country (EU excluded)
# Computed INSIDE the function (no pct_change_gt_by_country)
# ----------------------------
def fig_top_left(df_in: pd.DataFrame, selected_country: str) -> go.Figure:
    d = df_in[(df_in[UNIT] == "GT") & df_in[VAL].notna()].copy()
    if d.empty:
        return empty_fig("% change in GT by country (no data)", height=520)

    # aggregate GT across gear + eng_pow for each geo/year
    g = d.groupby([GEO, YEAR], as_index=False)[VAL].sum()

    rows = []
    for c in g[GEO].unique():
        if c == "EU":
            continue
        gc = g[g[GEO] == c].sort_values(YEAR)
        if len(gc) >= 6:
            first_3 = gc[VAL].iloc[:3].mean()
            last_3  = gc[VAL].iloc[-3:].mean()
            if first_3 and first_3 != 0:
                rows.append({"country": c, "pct_change": ((last_3 - first_3) / first_3) * 100})

    pct_df = pd.DataFrame(rows)
    if pct_df.empty:
        return empty_fig("% change in GT by country (no data)", height=520)

    # sort ascending like your screenshot (negative -> positive)
    pct_df = pct_df.sort_values("pct_change", ascending=True).reset_index(drop=True)

    colors = ["steelblue" if c == selected_country else "lightgray" for c in pct_df["country"]]

    fig = go.Figure(
        data=[go.Bar(
            x=pct_df["country"],
            y=pct_df["pct_change"],
            marker=dict(color=colors),
        )]
    )

    fig.update_layout(
        title="% change in GT by country — click a bar to select",
        xaxis_title="Country",
        yaxis_title="% change (GT)",
        xaxis_tickangle=-45,
        hovermode="x",
  #      height=200,
   #     width = 350,
        margin=dict(l=30, r=20, t=60, b=70),
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=pct_df["country"].tolist(),
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dot",
        spikethickness=2,
    )
    fig.update_yaxes(zeroline=True, zerolinewidth=1)

    return fig

# ----------------------------
# Other charts (NOT clickable)
# ----------------------------
def fig_top_right_nr_gt_timeseries(df_in: pd.DataFrame, country: str) -> go.Figure:
    d = df_in[(df_in[GEO] == country) & df_in[VAL].notna()].copy()
    if d.empty:
        return empty_fig(f"{country}: NR & GT over time (no data)")

    nr = d[d[UNIT] == "NR"].groupby(YEAR, as_index=False)[VAL].sum().sort_values(YEAR)
    gt = d[d[UNIT] == "GT"].groupby(YEAR, as_index=False)[VAL].sum().sort_values(YEAR)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=nr[YEAR], y=nr[VAL], mode="lines+markers", name="NR (ships)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=gt[YEAR], y=gt[VAL], mode="lines+markers", name="GT (tonnage)"), secondary_y=True)

    fig.update_layout(
        title=f"{country}: Total fleet over time (NR & GT)",
        hovermode="x unified",
        margin=dict(l=50, r=20, t=55, b=45),
        height=300,
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="NR (sum)", secondary_y=False)
    fig.update_yaxes(title_text="GT (sum)", secondary_y=True)
    return fig

def latest_year_for_country(df_in: pd.DataFrame, country: str) -> int | None:
    years = df_in[df_in[GEO] == country][YEAR].dropna()
    return int(years.max()) if len(years) else None

def fig_bottom_left_gt_by_gear_latest(df_in: pd.DataFrame, country: str) -> go.Figure:
    y = latest_year_for_country(df_in, country)
    if y is None:
        return empty_fig(f"{country}: GT by gear (no data)")

    d = df_in[
        (df_in[GEO] == country) &
        (df_in[YEAR] == y) &
        (df_in[UNIT] == "GT") &
        df_in[VAL].notna()
    ].copy()

    if d.empty:
        return empty_fig(f"{country} {y}: GT by gear (no data)")

    agg = d.groupby(GEAR, as_index=False)[VAL].sum().sort_values(VAL, ascending=False).head(15)
    fig = px.bar(agg, x=GEAR, y=VAL, title=f"{country} ({y}): GT by gear (top 15)")
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        margin=dict(l=50, r=20, t=55, b=60),
        height=300,
    )
    return fig

def fig_bottom_right_gt_by_eng_latest(df_in: pd.DataFrame, country: str) -> go.Figure:
    y = latest_year_for_country(df_in, country)
    if y is None:
        return empty_fig(f"{country}: GT by engine power (no data)")

    d = df_in[
        (df_in[GEO] == country) &
        (df_in[YEAR] == y) &
        (df_in[UNIT] == "GT") &
        df_in[VAL].notna()
    ].copy()

    if d.empty:
        return empty_fig(f"{country} {y}: GT by engine power (no data)")

    agg = d.groupby(ENG, as_index=False)[VAL].sum().sort_values(VAL, ascending=False)
    fig = px.bar(agg, x=ENG, y=VAL, title=f"{country} ({y}): GT by engine power")
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        margin=dict(l=50, r=20, t=55, b=60),
        height=300,
    )
    return fig

# ----------------------------
# Layout: MAIN clickable chart left, others right (not clickable)
# ----------------------------
# ----------------------------
# Layout: 2 x 2, all same size, top-left clickable
# ----------------------------
st.title(" European Fishing Fleet Dashboard")

COMMON_H = 380  # all four same height

# Build figures with same height
fig_tl = fig_top_left(df, st.session_state.selected_country)
fig_tl.update_layout(height=COMMON_H)

country = st.session_state.selected_country

fig_tr = fig_top_right_nr_gt_timeseries(df, country)
fig_tr.update_layout(height=COMMON_H)

fig_bl = fig_bottom_left_gt_by_gear_latest(df, country)
fig_bl.update_layout(height=COMMON_H)

fig_br = fig_bottom_right_gt_by_eng_latest(df, country)
fig_br.update_layout(height=COMMON_H)

# 2x2 grid
c1, c2 = st.columns(2, gap="large")
c3, c4 = st.columns(2, gap="large")

with c1:
    # TOP-LEFT: ONLY CLICKABLE CHART (no st.plotly_chart here)
    clicked = plotly_events(
        fig_tl,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=COMMON_H,
        key="main_click",
    )
    if clicked:
        st.session_state.selected_country = clicked[0]["x"]

with c2:
    st.plotly_chart(fig_tr, use_container_width=True)

with c3:
    st.plotly_chart(fig_bl, use_container_width=True)

with c4:
    st.plotly_chart(fig_br, use_container_width=True)
