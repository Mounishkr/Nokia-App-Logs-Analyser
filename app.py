import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from parser import parse_logs
from analyzer import LogAnalyzer
import json
import os
from pdf_generator import generate_pdf_report

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LOG PULSE | Advanced Log Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # Give more space for the main UI
)

# -----------------------------------------------------------------------------
# CUSTOM PREMIUM STYLING (Glassmorphism & Neomorphism)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        color: #e0e0e0;
    }

    /* Target custom UI components only to protect internal icons */
    .hero-title, .hero-subtitle, .glass-card, .metric-value, .metric-label, .timeline-content, h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Main background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1c2c 0%, #0d0e15 100%);
    }

    /* Custom Title */
    .hero-title {
        background: linear-gradient(90deg, #6e8efb, #a777e3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .hero-title::after {
        content: "NOKIA APP LOG ANALYSER";
    }

    .hero-subtitle {
        color: #888;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Metrics Styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .metric-label {
        color: #888;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 1px;
    }

    /* Timeline styling */
    .timeline-item {
        border-left: 2px solid rgba(110, 142, 251, 0.3);
        padding-left: 25px;
        margin-left: 20px;
        padding-bottom: 20px;
        position: relative;
    }

    .timeline-dot {
        position: absolute;
        left: -9px;
        top: 0;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #6e8efb;
        box-shadow: 0 0 10px #6e8efb;
    }

    .timeline-content {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0 25px;
        color: #888;
        border: none;
        transition: all 0.3s;
    }

    .stTabs [aria-selected="true"] {
        background-color: #6e8efb !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(110, 142, 251, 0.4);
    }

    /* Sidebar hide/style */
    [data-testid="stSidebar"] {
        background-color: #0d0e15;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Expander fix for text overlap */
    .stExpander {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        margin-top: -10px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------------------
st.markdown('<div class="hero-title">NOKIA APP LOG ANALYSER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Visual Intelligence for Production Ecosystems</div>', unsafe_allow_html=True)

# Sidebar functionality
st.sidebar.title("Configuration")
uploaded_file = st.sidebar.file_uploader("Drop log files here", type=["json"])
st.sidebar.markdown("---")
st.sidebar.info("Tip: Double-click rows in Log Explorer to view full JSON payload.")

# -----------------------------------------------------------------------------
# DATA LOADING & LANDING PAGE
# -----------------------------------------------------------------------------
if not uploaded_file:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 60px; margin-top: 50px;">
        <h2 style="color: #6e8efb; font-size: 2.5rem;">Let's Get Started 🛫</h2>
        <p style="color: #888; font-size: 1.2rem; margin-top: 20px;">
            Your log intelligence engine is ready. Please upload your production logs to begin the analysis.
        </p>
        <div style="margin-top: 40px; padding: 20px; border-radius: 15px; border: 1px dashed rgba(110, 142, 251, 0.4); display: inline-block;">
            <p style="color: #6e8efb; font-weight: 600;">Drag and Drop your .json log file in the sidebar</p>
        </div>
        <p style="color: #555; font-size: 0.9rem; margin-top: 30px;">
            Supports compressed logs and standard JSON formats.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
else:
    temp_path = "temp_uploaded_log.json"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = parse_logs(temp_path)

analyzer = LogAnalyzer(df)
stats = analyzer.get_summary_stats()

# Sidebar: Export Report Section
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Reporting")
if st.sidebar.button("Generate Summary Report (.pdf)"):
    try:
        report_data = generate_pdf_report(stats, analyzer.get_failing_apis())
        st.sidebar.download_button(
            label="⬇️ Download PDF Result",
            data=report_data,
            file_name=f"log_analysis_report_{stats['total']}_events.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.sidebar.error("Error generating report. Please check characters in logs.")

# -----------------------------------------------------------------------------
# STATS KPI GRID
# -----------------------------------------------------------------------------
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Total Events</div>
        <div class="metric-value">{stats['total']}</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">System Health</div>
        <div class="metric-value" style="color: #00ff88;">{stats['success_rate']}%</div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    error_color = "#ff4b4b" if stats['error'] > 0 else "#ffffff"
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Critical Errors</div>
        <div class="metric-value" style="color: {error_color};">{stats['error']}</div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-label">Warnings</div>
        <div class="metric-value" style="color: #ffa500;">{stats['warn']}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD TABS
# -----------------------------------------------------------------------------
tab_overview, tab_failures, tab_flow, tab_explorer = st.tabs([
    "📈 Analytics Hub", 
    "🚨 Root Cause Analysis", 
    "🗺 Trace Timeline", 
    "🔍 RAW Logs"
])

# -----------------
# TAB 1: ANALYTICS
# -----------------
with tab_overview:
    g_col1, g_col2 = st.columns([1, 1])
    
    with g_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Event Intensity Over Time")
        tl_df = df.copy()
        if tl_df['timestamp'].notnull().any():
            tl_df['time_str'] = tl_df['timestamp'].dt.strftime('%H:%M:%S')
            tl_df = tl_df.groupby(['time_str', 'level']).size().reset_index(name='count')
            fig_tl = px.area(tl_df, x='time_str', y='count', color='level',
                           color_discrete_map={'error': '#ff4b4b', 'warn': '#ffa500', 'info': '#6e8efb', 'debug': '#a777e3'},
                           line_shape='spline')
            fig_tl.update_layout(template="plotly_dark", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_tl, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with g_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Impact breakdown")
        levels = df['level'].value_counts()
        fig_donut = go.Figure(data=[go.Pie(labels=levels.index, values=levels.values, hole=.6)])
        fig_donut.update_traces(marker=dict(colors=['#6e8efb', '#a777e3', '#ffa500', '#ff4b4b']))
        fig_donut.update_layout(template="plotly_dark", height=350, paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Page Traffic Heatmap")
    p_data = df[df['page_name'] != 'N/A']['page_name'].value_counts().reset_index()
    p_data.columns = ['Page', 'Visits']
    fig_p = px.bar(p_data, y='Page', x='Visits', orientation='h', color='Visits',
                  color_continuous_scale='Magma')
    fig_p.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_p, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------
# TAB 2: FAILURES
# -----------------
with tab_failures:
    st.markdown("### Critical Diagnostics")
    raw_failures = analyzer.get_failing_apis()
    
    if raw_failures.empty:
        st.success("Your system is running smoothly. 0 critical API failures detected.")
    else:
        for idx, row in raw_failures.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid #ff4b4b; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: #fff;">{row['api_action']}</div>
                            <div style="color: #6e8efb; font-size: 0.85rem; margin-top: 4px; font-family: monospace;">{row['api_method']} • {row['api_url']}</div>
                        </div>
                        <div style="background: rgba(255, 75, 75, 0.2); color: #ff4b4b; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; border: 1px solid #ff4b4b; font-weight: 700;">
                            STATUS: {row['api_status']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("INSPECT DETAILED TRACE PAYLOAD"):
                    col_e1, col_e2 = st.columns([1, 2])
                    with col_e1:
                        st.write("**Origin Page:**", row['page_name'])
                        st.write("**Captured At:**", str(row['timestamp']))
                    with col_e2:
                        st.write("**Payload Diagnostics:**")
                        try:
                            # Try to pretty print if it's JSON
                            err_data = json.loads(row['api_error'].replace("'", "\""))
                            st.json(err_data)
                        except:
                            st.code(row['api_error'], language="json")
                st.markdown('<div style="margin-bottom: 25px;"></div>', unsafe_allow_html=True)

# -----------------
# TAB 3: TIMELINE
# -----------------
with tab_flow:
    st.markdown("### Sequential Execution Trace")
    flow_df = analyzer.get_flow_sequence()
    
    if flow_df.empty:
        st.info("No sequence data available.")
    else:
        for _, step in flow_df.iterrows():
            ts = step['timestamp']
            time_str = ts.strftime('%H:%M:%S') if ts and not pd.isna(ts) else "??:??:??"
            
            dot_color = "#6e8efb"
            if step['type'] == 'ERROR': dot_color = "#ff4b4b"
            elif step['type'] == 'APP_EVENT': dot_color = "#ffa500"
            
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot" style="background: {dot_color}; box-shadow: 0 0 10px {dot_color};"></div>
                <div class="timeline-content">
                    <span style="color: #888; font-size: 0.8rem;">{time_str}</span>
                    <div style="font-weight: 600;">{step['detail']}</div>
                    <div style="font-size: 0.7rem; color: #555;">CATEGORY: {step['type']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -----------------
# TAB 4: EXPLORER
# -----------------
with tab_explorer:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    filters = st.multiselect("Level Presence", ['info', 'debug', 'error', 'warn'], default=['error', 'warn', 'info'])
    search = st.text_input("Global Search", "")
    
    view_df = df[df['level'].isin(filters)]
    if search:
        view_df = view_df[view_df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    
    st.dataframe(
        view_df[['timestamp', 'level', 'page_name', 'message', 'api_status']],
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #444; font-size: 0.8rem;">LOG PULSE ENGINE • v2.0 • PRO-BUILD</div>', unsafe_allow_html=True)
