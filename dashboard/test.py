# app.py - DataPulse Dashboard
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.connection.sql_connection import SQLConnection

# ── تنظیمات صفحه ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataPulse | ETL Monitoring",
    page_icon="📊",
    layout="wide"
)

# ── خواندن environment variables ─────────────────────────────────────────────
load_dotenv()

LOG_HOST = os.getenv("LOG_HOST")
LOG_PORT = int(os.getenv("LOG_PORT"))
LOG_USERNAME = os.getenv("LOG_USERNAME")
LOG_PASSWORD = os.getenv("LOG_PASSWORD")
LOG_DATABASE = os.getenv("LOG_DATABASE")
LOG_SCHEMA = os.getenv("LOG_SCHEMA", "dbo")
LOG_TABLE = os.getenv("LOG_TABLE")


# ── اتصال به دیتابیس با cache ────────────────────────────────────────────────
@st.cache_resource
def get_db_connection():
    """ایجاد connection pool به SQL Server"""
    conn = SQLConnection(
        host=LOG_HOST,
        port=LOG_PORT,
        user=LOG_USERNAME,
        password=LOG_PASSWORD,
        database=LOG_DATABASE,
        windows_authentication=True
    )
    conn.connect()
    return conn


@st.cache_data(ttl=60)
def load_etl_logs():
    """خواندن جدول ETL logs"""
    conn = get_db_connection()
    query = f"SELECT * FROM {LOG_SCHEMA}.{LOG_TABLE} ORDER BY start_time DESC"
    df = pd.read_sql(query, conn.engine)

    # تبدیل ستون‌های زمانی
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'])
    if 'end_time' in df.columns:
        df['end_time'] = pd.to_datetime(df['end_time'])

    return df


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("📊 DataPulse — ETL Monitoring Dashboard")

try:
    with st.spinner("در حال بارگذاری داده‌ها..."):
        df = load_etl_logs()

    st.success(f"✅ {len(df)} رکورد لود شد")

    # نمایش داده‌های خام
    with st.expander("🔍 مشاهده داده‌های خام"):
        st.dataframe(df, use_container_width=True)

    # نمایش اطلاعات ستون‌ها
    st.subheader("اطلاعات جدول")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("تعداد رکوردها", len(df))
        st.metric("تعداد جداول", df['table_name'].nunique() if 'table_name' in df.columns else 0)

    with col2:
        if 'status' in df.columns:
            success_count = (df['status'] == 'success').sum()
            failed_count = (df['status'] == 'failed').sum()
            st.metric("موفق", success_count)
            st.metric("ناموفق", failed_count)

except Exception as e:
    st.error(f"❌ خطا در اتصال به دیتابیس: {e}")
    st.info("لطفاً مشخصات اتصال در فایل .env را بررسی کنید")

import plotly.express as px

# نمودار دونات بر اساس ستون status
def render_status_donut(df):
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    # رنگ‌بندی بر اساس وضعیت
    color_map = {
        'success': '#22c55e',   # سبز
        'failed':  '#ef4444',   # قرمز
        'running': '#3b82f6',   # آبی
        'pending': '#f59e0b',   # نارنجی
    }

    fig = px.pie(
        status_counts,
        names='status',
        values='count',
        hole=0.55,
        color='status',
        color_discrete_map=color_map,
    )

    fig.update_traces(
        textposition='outside',
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>تعداد: %{value}<br>درصد: %{percent}<extra></extra>',
    )

    fig.update_layout(
        title=dict(text='توزیع وضعیت اجرا', font_size=16, x=0.5, xanchor='center'),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
        margin=dict(t=60, b=60, l=20, r=20),
        height=380,
    )

    return fig


# داخل بخش UI
st.plotly_chart(render_status_donut(df), use_container_width=True)
