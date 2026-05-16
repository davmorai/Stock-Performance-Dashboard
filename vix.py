import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


VIX_TICKER = "^VIX"
VIX_MAX_RANGE = 80


def fetch_vix_value():
    """Daten holen von yfinance VIX data"""
    try:
        vix = yf.Ticker(VIX_TICKER)
        vix_data = vix.history(period="1d")
        if not vix_data.empty:
            return round(vix_data["Close"].iloc[-1], 1)
    except Exception:
        pass
    return None


def get_vix_status(vix_value):
    """Farbenskala"""
    if vix_value < 15:
        return "Low", "#4CAF50"
    if vix_value < 25:
        return "Moderate", "#FFB300"
    return "High", "#FF4B4B"


def build_vix_figure(vix_value, vix_color):
    """Gauge Figure Plotly"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vix_value,
        number={"font": {"color": "#ffffff", "size": 26}},
        gauge={
            "axis": {"range": [None, VIX_MAX_RANGE], "tickwidth": 1, "tickcolor": "#999"},
            "bar": {"color": vix_color},
            "bgcolor": "#1f2937",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 15], "color": "#1e5e42"},
                {"range": [15, 25], "color": "#725d1e"},
                {"range": [25, VIX_MAX_RANGE], "color": "#551d1d"},
            ],
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=10, l=20, r=20),
        height=140,
        width=250,
    )
    return fig


def render_vix_widget():
    """Vix Widget rendern"""
    vix_value = fetch_vix_value()
    if vix_value is None:
        st.markdown('<div style="color: #aaa; font-size: 0.85rem;">VIX data unavailable</div>', unsafe_allow_html=True)
        return

    vix_status, vix_color = get_vix_status(vix_value)
    fig = build_vix_figure(vix_value, vix_color)

    with st.container(border=True):
        st.markdown(
            '<div style="font-size: 0.75rem; color: #aaa; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: -5px;">VIX Index</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center; color: {vix_color}; font-weight: 600; font-size: 0.8rem; margin-top: -8px;">{vix_status}</div>',
            unsafe_allow_html=True,
        )

