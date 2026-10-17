# ------------------------ Modules ------------------------
# Libraries =>
import sys, os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import plotly.graph_objects as go

# Base Path =>
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Modules =>
from src.connection.sql_connection import SQLConnection

# ------------------------Page Config ------------------------
st.set_page_config(page_title="DataPulse", layout="wide", page_icon="⚡")

# ------------------------ CSS ------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: #283046 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #d0d2d6 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] .stButton > button {
    background: #7367f0 !important;
    color: #ffffff !important;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #5e50ee !important;
}

/* main bg */
.main .block-container {
    background: #f8f8f8;
    padding: 2rem;
    max-width: 1400px;
}

/* chart wrapper — رنگ پس‌زمینه کارت اینجاست نه توی plotly */
[data-testid="stPlotlyChart"] > div {
    background: #ffffff;
    border-radius: 10px;
    padding: 0.5rem;
    box-shadow: 0 4px 24px rgba(34, 41, 47, 0.08);
}

/* dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    box-shadow: 0 4px 24px rgba(34, 41, 47, 0.08);
    overflow: hidden;
}

hr { border-color: #ebe9f1; }
</style>
""", unsafe_allow_html=True)

# ------------------------ Constants ------------------------
STATUS_COLORS = {
    "success": "#28c76f",
    "failed": "#ea5455",
    "running": "#7367f0",
    "pending": "#ff9f43",
}

CARD_GRADIENTS = [
    ("linear-gradient(135deg,#7367f0,#9e95f5)", "⚙️"),
    ("linear-gradient(135deg,#28c76f,#48da89)", "🕐"),
    ("linear-gradient(135deg,#ff9f43,#ffb976)", "📦"),
]

# ------------------------ Basic chart settings ------------------------

# Important: paper_bgcolor and plot_bgcolor must be rgba(0,0,0,0)
# Get the color from CSS; never use "white" or "#fff"
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#5e5873"),
    title_x=0.5,
    title_font=dict(size=14, color="#3d3b8e", family="Inter"),
)

# ------------------------ env & Connection ------------------------
load_dotenv()
LOG_HOST = os.getenv("LOG_HOST")
LOG_PORT = int(os.getenv("LOG_PORT", 1433))
LOG_USERNAME = os.getenv("LOG_USERNAME")
LOG_PASSWORD = os.getenv("LOG_PASSWORD")
LOG_DATABASE = os.getenv("LOG_DATABASE")
LOG_SCHEMA = os.getenv("LOG_SCHEMA", "dbo")
LOG_TABLE = os.getenv("LOG_TABLE")


@st.cache_resource
def get_conn():
    load_dotenv()
    return SQLConnection(
        host=LOG_HOST, port=LOG_PORT,
        database=LOG_DATABASE,
        user=LOG_USERNAME,
        password=LOG_PASSWORD,
    )


@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    conn = get_conn()
    conn.connect()
    df = pd.read_sql(
        f"SELECT * FROM {LOG_SCHEMA}.{LOG_TABLE} ORDER BY start_time DESC",
        conn.engine,
    )
    for col in ("start_time", "end_time"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


df_raw = load_data()

# ------------------------ Sidebar ------------------------
with st.sidebar:
    st.markdown("## ⚡ DataPulse")
    st.markdown("---")

    all_tables = sorted(df_raw["table_name"].unique())
    selected_tables = st.multiselect(
        "Filter by Table",
        options=all_tables,
        default=all_tables,
        placeholder="All tables",
    )
    if not selected_tables:
        st.warning("Select at least one table.")
        st.stop()

    st.markdown("---")
    if st.button("🔄  Refresh data"):
        st.cache_data.clear()
        st.rerun()

# ------------------------ Filtered df ------------------------
df = df_raw[df_raw["table_name"].isin(selected_tables)].copy()


# ------------------------ Helpers ------------------------
def bar_layout(fig: go.Figure, height: int = 340) -> go.Figure:
    """Unified styling for bar charts"""
    fig.update_layout(
        **BASE_LAYOUT,
        height=height,
        margin=dict(t=52, b=52, l=52, r=24),
        xaxis=dict(
            showgrid=False,
            automargin=True,
            tickangle=-30,
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="#ebe9f1",
            automargin=True,
            tickfont=dict(size=11),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=11),
        ),
    )
    return fig


def line_layout(fig: go.Figure, height: int = 340) -> go.Figure:
    """Unified styling for line charts with external legend"""
    fig.update_layout(
        **BASE_LAYOUT,
        height=height,
        margin=dict(t=52, b=52, l=52, r=180),  # فضا برای legend
        xaxis=dict(
            showgrid=False,
            automargin=True,
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="#ebe9f1",
            automargin=True,
            tickfont=dict(size=11),
        ),
        legend=dict(
            x=1.02,
            y=1.0,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=10),
        ),
    )
    return fig


def make_donut(series: pd.Series, title: str, color_map: dict = None) -> go.Figure:
    """
    Making a donut chart with the right colors.

    Reason for the previous blackout: plotly uses the default palette when it doesn't have a color_discrete_map or
    color_discrete_sequence,
    which sometimes interferes with transparent backgrounds.
    Here we give an explicit palette every time.
    """
    counts = series.value_counts().reset_index()
    counts.columns = ["label", "count"]

    if color_map:
        # Get the order of colors according to label from color_map
        colors = [color_map.get(lbl, "#cccccc") for lbl in counts["label"]]
    else:
        # Quality palette with enough variety — not the plotly default
        palette = [
            "#7367f0", "#28c76f", "#ff9f43", "#ea5455",
            "#00cfe8", "#ff6f61", "#6fcf97", "#f2c94c",
            "#9b51e0", "#eb5757",
        ]
        colors = [palette[i % len(palette)] for i in range(len(counts))]

    fig = go.Figure(go.Pie(
        labels=counts["label"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b>: %{value}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title_text=title,
        showlegend=False,
        height=320,
        margin=dict(t=52, b=60, l=80, r=80),  # فضا برای label خارج از دایره
    )
    return fig


def kpi_card(gradient: str, icon: str, label: str, value) -> str:
    return f"""
    <div style="
        background: {gradient};
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        color: #fff;
        box-shadow: 0 4px 20px rgba(0,0,0,.15);
    ">
        <div style="font-size:1.9rem;font-weight:700;line-height:1">{value}</div>
        <div style="font-size:.85rem;opacity:.9;margin-top:.4rem">{icon} {label}</div>
    </div>"""


# ------------------------ ROW 0 — Title ------------------------
st.markdown(
    "<h1 style='font-size:1.6rem;font-weight:700;color:#3d3b8e;"
    "margin-bottom:.25rem'>DataPulse — ETL Monitor</h1>",
    unsafe_allow_html=True,
)

# ------------------------ ROW 1 — KPI cards ------------------------
c1, c2, c3 = st.columns(3)

latest_run = df["start_time"].max()
latest_str = latest_run.strftime("%Y-%m-%d %H:%M") if pd.notna(latest_run) else "N/A"

kpi_values = [
    (df["table_name"].nunique(), "Distinct Tables"),
    (latest_str, "Latest Run"),
    (len(df), "Total Jobs"),
]
for col, (val, label), (grad, icon) in zip([c1, c2, c3], kpi_values, CARD_GRADIENTS):
    col.markdown(kpi_card(grad, icon, label, val), unsafe_allow_html=True)

st.divider()

# ------------------------ ROW 2 — Job counts | Records src vs target ------------------------
c1, c2 = st.columns(2)

with c1:
    tbl_status = (
        df.groupby(["table_name", "status"])
        .size().reset_index(name="count")
    )
    fig2a = px.bar(
        tbl_status, x="table_name", y="count",
        color="status",
        color_discrete_map=STATUS_COLORS,
        barmode="group",
        title="Job Count by Table & Status",
        labels={"table_name": "Table", "count": "Jobs", "status": "Status"},
    )
    bar_layout(fig2a)
    st.plotly_chart(fig2a, use_container_width=True)

with c2:
    rec = (
        df.melt(
            id_vars="table_name",
            value_vars=["source_count", "target_count"],
            var_name="Type", value_name="Records",
        )
        .assign(Type=lambda d: d["Type"].map(
            {"source_count": "Source", "target_count": "Target"}
        ))
        .groupby(["table_name", "Type"], as_index=False)["Records"].sum()
    )
    fig2b = px.bar(
        rec, x="table_name", y="Records",
        color="Type", barmode="group",
        title="Records: Source vs Target",
        labels={"table_name": "Table", "Type": "Type"},
        color_discrete_map={"Source": "#7367f0", "Target": "#ff9f43"},
    )
    bar_layout(fig2b)
    st.plotly_chart(fig2b, use_container_width=True)

st.divider()

# ------------------------ ROW 3 — Avg duration | Records over time ------------------------
with c1:
    avg_dur = (
        df.groupby("table_name")["duration_seconds"]
        .mean().reset_index(name="Avg Duration (sec)")
    )
    fig3a = px.bar(
        avg_dur, x="table_name", y="Avg Duration (sec)",
        title="Average Job Duration",
        labels={"table_name": "Table"},
        color_discrete_sequence=["#7367f0"],
    )
    bar_layout(fig3a)
    st.plotly_chart(fig3a, use_container_width=True, key="fig3a")

with c2:
    df_time = df.copy()
    df_time["date"] = df_time["start_time"].dt.date
    time_rec = (
        df_time.melt(
            id_vars=["table_name", "date"],
            value_vars=["source_count", "target_count"],
            var_name="Type", value_name="Records",
        )
        .groupby(["date", "table_name", "Type"], as_index=False)["Records"].sum()
    )
    time_rec["Type"] = time_rec["Type"].map(
        {"source_count": "Source", "target_count": "Target"}
    )
    fig3b = px.line(
        time_rec, x="date", y="Records",
        color="table_name", line_dash="Type",
        title="Records Over Time",
        labels={"date": "Date", "table_name": "Table"},
        markers=True,
    )
    line_layout(fig3b)
    st.plotly_chart(fig3b, use_container_width=True, key="fig3b")
st.divider()

# ------------------------ ROW 4 — Donut charts ------------------------
c1, c2, c3 = st.columns(3)
error_df = df[df["error_message"].notna() & (df["error_message"].str.strip() != "")]

with c1:
    fig4a = make_donut(df["status"], "Job Status Distribution", STATUS_COLORS)
    st.plotly_chart(fig4a, use_container_width=True)

with c2:
    if not error_df.empty:
        # Truncate error texts so that the label is not cut off
        err_short = error_df["error_message"].str.slice(0, 40)
        fig4b = make_donut(err_short, "Error Type Distribution")
        st.plotly_chart(fig4b, use_container_width=True)
    else:
        st.info("No errors recorded")

with c3:
    if not error_df.empty:
        fig4c = make_donut(error_df["table_name"], "Errors by Table")
        st.plotly_chart(fig4c, use_container_width=True)
    else:
        st.info("No errors recorded")

st.divider()

# ------------------------ ROW 5 — Log table ------------------------
st.markdown(
    "<h3 style='font-size:1rem;font-weight:600;color:#5e5873;"
    "margin-bottom:.5rem'>Recent Events</h3>",
    unsafe_allow_html=True,
)
st.dataframe(
    df.sort_values("start_time", ascending=False).head(20),
    use_container_width=True,
)
