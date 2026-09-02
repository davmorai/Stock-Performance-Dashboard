import streamlit as st
import pandas as pd
import plotly.express as px
 
from stocks import STOCKS, DEFAULT_STOCKS
from time_logic import begruessung, aktuell, nyse_nasdaq, lse, tse, crypto, dax_six
from sektor_details import zeige_top_10_bereich, get_sector_performance
from technical_analysis import get_ta_summary_for_ticker
from vix import render_vix_widget
from styles import apply_custom_css
from data_utils import load_name, save_name, normalized_and_clean, load_data, resolve_ta_horizon
from config import (
    COLOR_MARKET_OPEN,
    COLOR_MARKET_CLOSED,
    HORIZON_MAP,
    SEKTOR_ZEIT_MAP,
)

#Seite konfigurieren
st.set_page_config(
    page_title="Stock Performance Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
apply_custom_css()
 

#Session State für das problem mit rerun
if "last_clicked_sector" not in st.session_state:
    st.session_state.last_clicked_sector = None
if "name" not in st.session_state:
    st.session_state.name = load_name()
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False


header_left, header_right = st.columns([0.75, 0.25], gap="xsmall")
 
with header_left:
    # Datum
    st.markdown(
        f'<p class="date-text">{aktuell.strftime("%A, %B %d, %Y")}</p>',
        unsafe_allow_html=True,
    )
    #Begrüssung
    st.markdown(
        f"""
        <div class="greeting-container">
            <span class="greeting-text">{begruessung},</span>
            <span class="name-text">{st.session_state.name}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not st.session_state.edit_mode:
        if st.button("✎", key="edit_name", help="Name bearbeiten"):
            st.session_state.edit_mode = True
            st.rerun()

    if st.session_state.edit_mode:
        neuer_name = st.text_input("Name", value=st.session_state.name, label_visibility="collapsed")
        if st.button("✔ Speichern", key="save_name"):
            st.session_state.name = neuer_name if neuer_name.strip() else "Besucher"
            save_name(st.session_state.name)
            st.session_state.edit_mode = False
            st.rerun()

# Marktübersicht-Untertitel
    st.markdown(
        '<p style="color:#888; font-size:1rem; margin:0.3rem;">Marktübersicht & Portfolio Tracker</p>',
        unsafe_allow_html=True,
    )
 
    # Börsenstatus-Dots
    def dot(color: str, label: str) -> str:
        return f'<span style="color:{color};">●</span> {label}'
 
    nyse_color    = COLOR_MARKET_OPEN if nyse_nasdaq else COLOR_MARKET_CLOSED
    lse_color     = COLOR_MARKET_OPEN if lse         else COLOR_MARKET_CLOSED
    tse_color     = COLOR_MARKET_OPEN if tse         else COLOR_MARKET_CLOSED
    dax_six_color = COLOR_MARKET_OPEN if dax_six     else COLOR_MARKET_CLOSED
 
    st.markdown(
        f'<p style="font-size:0.9rem; color:#aaa; margin:0.3rem;">'
        f'{dot(nyse_color,"NYSE")} &nbsp;&nbsp;'
        f'{dot(nyse_color,"NASDAQ")} &nbsp;&nbsp;'
        f'{dot(lse_color,"LSE")} &nbsp;&nbsp;'
        f'{dot(tse_color,"TSE")} &nbsp;&nbsp;'
        f'{dot(dax_six_color,"DAX")} &nbsp;&nbsp;'
        f'{dot(dax_six_color,"SIX")} &nbsp;&nbsp;'
        f'{dot(COLOR_MARKET_OPEN,"Crypto")}'
        f'</p>',
        unsafe_allow_html=True,
    )
 

with header_right:
    render_vix_widget()



#Ticker-Auswahl & Zeithorizont
def stocks_to_str(stocks: list) -> str:
    return ",".join(stocks)

#lädt beim ersten mal die default danach session state
if "tickers_input" not in st.session_state:
    raw = st.query_params.get("stocks", "")
    st.session_state.tickers_input = raw.split(",") if raw else list(DEFAULT_STOCKS)
 
 
cols = st.columns([0.30, 0.70], gap="medium")
top_left_cell = cols[0].container(border=True, height="content", vertical_alignment="center")
 
with top_left_cell:
    tickers = st.multiselect(
        "Aktien auswählen",
        options=sorted(set(STOCKS) | set(st.session_state.tickers_input)),
        default=st.session_state.tickers_input,
        placeholder="Wähle eine Aktie aus. Beispiel: NVDA",
        accept_new_options=True,
    )
    selected_horizon = st.pills("Zeithorizont", options=list(HORIZON_MAP.keys()), default="6 Monate")
    horizon = str(selected_horizon) if selected_horizon is not None else "6 Monate"
 
tickers = [t.upper() for t in tickers]
st.session_state.tickers_input = tickers
 
if tickers:
    st.query_params["stocks"] = stocks_to_str(tickers)
else:
    st.query_params.pop("stocks", None)
    top_left_cell.info("Wähle Aktien um sie zu vergleichen", icon=":material/info:")
    st.stop()
 
right_cell = cols[1].container(border=True, height="stretch", vertical_alignment="center")



#Kursdaten laden & bereinigen
try:
    data = load_data(tuple(tickers), HORIZON_MAP[horizon])
except Exception as e:
    message = str(e) or "Unbekannter Fehler beim Laden der Daten."
    if "rate limit" in message.lower() or "429" in message:
        st.warning("YFinance hat ein Rate-Limit erreicht :(\nBitte später versuchen.")
        load_data.clear()
        st.stop()
    st.error(f"Fehler beim Laden der Daten: {message}")
    st.stop()
 
normalized, removed_tickers = normalized_and_clean(data)
 
if removed_tickers:
    st.warning(f"⚠️ Folgende Aktien wurden entfernt (unvollständige Daten): {', '.join(sorted(removed_tickers))}")
    tickers = list(normalized.columns)
 
if normalized.empty:
    st.error("Keine gültigen Daten für diese Aktien und Zeitraum.")
    st.stop()
 

#Performance Metriken Best vs Worst
latest_prices = sorted(
    [(float(normalized[t].iat[-1]), t) for t in tickers if t in normalized.columns]  # type: ignore[arg-type]
)#sonst persistierendes problem mit Float, somit beste lösung

min_val, max_val = latest_prices[0], latest_prices[-1]
 
bottom_left_cell = cols[0].container(border=True, height="stretch", vertical_alignment="center")
with bottom_left_cell:
    m_cols = st.columns(2, gap="small")
    m_cols[0].metric("Beste Aktie",        max_val[1], delta=f"{(max_val[0]-1)*100:.1f}%")#float lässt sich auch hier einsetzen aber gleicher fehler
    m_cols[1].metric("Schlechteste Aktie", min_val[1], delta=f"{(min_val[0]-1)*100:.1f}%")#oder auch hier :D
 

#Linien Diagramm zum Vergleich der Aktien
with right_cell:
    plot_data = normalized.reset_index().melt(
        id_vars=["Date"],
        var_name="Aktie",
        value_name="Normalisierter Preis",
    )
    fig = px.line(
        plot_data,
        x="Date",
        y="Normalisierter Preis",
        color="Aktie",
        title="Normalisierte Aktienperformance",
        labels={"Normalisierter Preis": "Normalisierter Preis (Basis = 1,0)", "Date": "Datum"},
        height=460,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aaa"),
        hovermode="x unified",
        margin=dict(l=30, r=30, t=50, b=40),
        xaxis_title="Datum",
        yaxis_title="Normalisierter Preis",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})


#Start TA 
st.divider()
st.header("Technische Analyse")
st.markdown(
    "Zeigt die wichtigsten technischen Kennzahlen für die aktuell ausgewählten Aktien. "
    "Die Werte basieren auf dem Tageschart und werden automatisch aktualisiert."
)

ta_period = resolve_ta_horizon(HORIZON_MAP[horizon])
summary_df = pd.DataFrame(
    [get_ta_summary_for_ticker(t, ta_period) for t in tickers]
).set_index("Ticker")
 
if summary_df.empty:
    st.warning("Für die ausgewählten Aktien konnten keine technischen Kennzahlen berechnet werden.")
else:
    st.dataframe(summary_df, use_container_width=True)
 
    first = summary_df.iloc[0]
    metric_cols = st.columns(4)
    metric_cols[0].metric("Ticker",  summary_df.index[0])
    metric_cols[1].metric("RSI 14",  f"{first['RSI 14']}")
    metric_cols[2].metric("Trend",   first["Trend"])
    metric_cols[3].metric("ATR 14",  f"{first['ATR 14']}")


#---Sektor Performance---
st.divider()
st.title("Weltweite ETF-Sektorperformance")
 
auswahl = st.pills("Zeitraum wählen", options=list(SEKTOR_ZEIT_MAP.keys()), default="1 Monat")
if auswahl is None:
    auswahl = "1 Monat"
 
df_perf = get_sector_performance(SEKTOR_ZEIT_MAP[auswahl])
 
if not df_perf.empty:
    df_perf["Weight"] = 1
    fig_tree = px.treemap(
        df_perf,
        path=["Sektor"],
        values="Weight",
        color="Performance %",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        custom_data=["Performance %"],
    )
    fig_tree.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
        textposition="middle center",
        textfont_size=16,
    )
    fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=500)
 
    st.caption("💡 Klicke auf einen Sektor, um Top 10 Unternehmen im jeweiligen Sektor anzuzeigen.")
 
    event = st.plotly_chart(
        fig_tree,
        use_container_width=True,
        on_select="rerun",
        key=f"treemap_sektor_{auswahl}",
    )
 
    clicked = (event or {}).get("selection", {}).get("points", [])
    sektor  = clicked[0].get("label") if clicked else None
 
    if sektor and st.session_state.last_clicked_sector != sektor:
        st.session_state.last_clicked_sector = sektor
        zeige_top_10_bereich(sektor)
    elif not sektor:
        st.session_state.last_clicked_sector = None