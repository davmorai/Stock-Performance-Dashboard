
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px #alle Plots

from stocks import STOCKS, DEFAULT_STOCKS, SEKTOREN_ETFS as sektoren_etfs
from time_logic import begruessung, aktuell, std_min, nyse_nasdaq, lse, tse, crypto, local_tz
from sektor_details import zeige_top_10_bereich
from technical_analysis import get_ta_summary_for_ticker
from vix import render_vix_widget
from styles import apply_custom_css
from utils import load_name, save_name, normalized_and_clean
from config import (
    COLOR_MARKET_OPEN,
    COLOR_MARKET_CLOSED,
    HORIZON_MAP,
    SEKTOR_ZEIT_MAP,
    CACHE_TTL_KURSE,
)#einzelne config Konstanten

#Session State für das problem mit rerun
if "last_clicked_sector" not in st.session_state:
    st.session_state.last_clicked_sector = None

st.set_page_config(
    page_title="Aktien Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
# --- Speichervariablen initialisieren ---

#--Header Zellen---
# CSS Header
apply_custom_css()

if 'name' not in st.session_state:
    st.session_state.name = load_name()
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

#----Ende Name Check---


# Datum, Begrüßung und VIX in einer Zeile
header_left, header_right = st.columns([0.75, 0.25], gap="xsmall")

#Name und Datum
with header_left:
    st.markdown(f'<p class="date-text">{aktuell.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)

    greeting_row, edit_col = st.columns([0.80, 0.20], gap="xxsmall")
    with greeting_row:
        st.markdown(
            f'''
            <div class="greeting-container">
                <span class="greeting-text">{begruessung},</span>
                <span class="name-text">{st.session_state.name}</span>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        
    with edit_col:
        if not st.session_state.edit_mode:
            if st.button("✎", key="edit_name"):
                st.session_state.edit_mode = True
                st.rerun()

    if st.session_state.edit_mode:
        neuer_name = st.text_input("Name", value=st.session_state.name)
        if st.button("Speichern", key="save_name"):
            st.session_state.name = neuer_name
            save_name(neuer_name)
            st.session_state.edit_mode = False
            st.rerun()


    #Logik von Öffnunszeiten
    crypto_color = COLOR_MARKET_OPEN
    nyse_nasdaq_color = COLOR_MARKET_OPEN if nyse_nasdaq else COLOR_MARKET_CLOSED
    lse_color = COLOR_MARKET_OPEN if lse else COLOR_MARKET_CLOSED
    tse_color = COLOR_MARKET_OPEN if tse else COLOR_MARKET_CLOSED
    #---Zeit Logik Ende---

    st.markdown('<p style="color: #888; font-size: 1rem; margin: 0.3rem;">Marktübersicht & Portfolio Tracker</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <p style="font-size: 0.9rem; color: #aaa; margin: 0.3rem;">
            <span style="color: {nyse_nasdaq_color};">●</span> NYSE &nbsp;&nbsp;
            <span style="color: {nyse_nasdaq_color};">●</span> NASDAQ &nbsp;&nbsp;
            <span style="color: {lse_color};">●</span> LSE &nbsp;&nbsp;
            <span style="color: {tse_color};">●</span> TSE &nbsp;&nbsp;
            <span style="color: {crypto_color};">●</span> Crypto
        </p>
        """,
        unsafe_allow_html=True,
    )

#---Datum und Begrüßung Ende---
#---VIX Widget---
with header_right:
    render_vix_widget()

#---VIX Widget Ende---
#---Header Ende---


#---Anpassungen/ Hinzufügen von Aktien---
#falls stocks nicht in liste dann werden Sie dazugefügt, damit sie in der Auswahl auftauchen
def stocks_to_str(stocks):
    return ",".join(stocks)

if "tickers_input" not in st.session_state:
    st.session_state.tickers_input = st.query_params.get(
        "stocks", stocks_to_str(DEFAULT_STOCKS)
    ).split(",")

#---Ende Anpassungen/ Hinzufügen von Aktien---


#---2 Zellen Layout---
#Verteilung in der Breite zwischen beide Zellen
cols = st.columns([0.30, 0.70], gap="medium")

#Zelle mit Selektionsbox
top_left_cell = cols[0].container(border=True, height="content", vertical_alignment="center")
with top_left_cell:
    tickers = st.multiselect(
        "Aktien auswählen",
        options=sorted(set(STOCKS) | set(st.session_state.tickers_input)),
        default=st.session_state.tickers_input,
        placeholder="Wähle eine Aktie aus. Beispiel: NVDA",
        accept_new_options=True,
    )

#Zelle mit Zeithorizont Auswahl
with top_left_cell:
    selected_horizon = st.pills("Zeithorizont", options=list(HORIZON_MAP.keys()), default="6 Monate")
    horizon = str(selected_horizon) if selected_horizon is not None else "6 Monate"


#---Selektion Aktie---
tickers = [t.upper() for t in tickers]

if tickers:
    st.query_params["stocks"] = stocks_to_str(tickers)
else:
    st.query_params.pop("stocks", None)
    
if not tickers:
    top_left_cell.info("Wähle Aktien um sie zu vergleichen", icon=":material/info:")
    st.stop()

right_cell = cols[1].container(border=True, height="stretch", vertical_alignment="center")
#---Ende Selektion---

#----erlaubt schnelleres Laden der Daten/ Caching---
@st.cache_resource(show_spinner=False, ttl="6h")
def load_data(tickers, period):
    tickers_obj = yf.Tickers(tickers)
    data = tickers_obj.history(period=period)
    if data is None:
        raise RuntimeError("YFinance returned no data.")
    return data["Close"]
#---Ende Caching---


# ---- Normalisierungs- und Cleaning-Funktion ----
try:
    data = load_data(tickers, HORIZON_MAP[horizon])
except Exception as e:
    message = str(e) or "Unbekannter Fehler beim Laden der Daten."
    if "rate limit" in message.lower() or "429" in message:
        st.warning("YFinance hat ein Rate-Limit erreicht :(\nBitte später versuchen.")
        try:
            load_data.clear()
        except Exception:
            pass
        st.stop()
    st.error(f"Fehler beim Laden der Daten: {message}")
    st.stop()

#Daten bereinigen UND die Variable 'normalized' erstellen
normalized, removed_tickers = normalized_and_clean(data)

#Warnung raising falls was nicht stimmt
if removed_tickers:
    st.warning(f"⚠️ Folgende Aktien wurden entfernt (unvollständige Daten): {', '.join(sorted(removed_tickers))}")
    tickers = list(normalized.columns) # Ticker-Liste aktualisieren

if normalized.empty or len(normalized.columns) == 0:
    st.error("Keine gültigen Daten für diese Aktien und Zeitraum.")
    st.stop()

# --- Berechnung der Performance ---
latest_norm_values = {normalized[ticker].iat[-1]: ticker for ticker in tickers}

max_norm_value = max(latest_norm_values.items())
min_norm_value = min(latest_norm_values.items())

bottom_left_cell = cols[0].container(border=True, height="stretch", vertical_alignment="center")

# Sicherstellen, dass wir eine Liste von Werten haben
latest_prices = []
for ticker in tickers:
    if ticker in normalized.columns:
        val = normalized[ticker].iat[-1]
        latest_prices.append((val, ticker))

if latest_prices:
    # Sortieren nach Performance (Wert)
    latest_prices.sort() 
    min_norm_value = latest_prices[0]  # Schlechtester
    max_norm_value = latest_prices[-1] # Bester

    with bottom_left_cell:
        m_cols = st.columns(2, gap="small")
        # Performance berechnen: (Wert - 1) * 100
        # Beispiel: 1.20 wird zu +20% | 0.80 wird zu -20%
        best_perf = (max_norm_value[0] - 1) * 100
        worst_perf = (min_norm_value[0] - 1) * 100

        m_cols[0].metric(
            "Beste Aktie",
            max_norm_value[1],
            delta=f"{best_perf:.1f}%"
        )
        m_cols[1].metric(
            "Schlechteste Aktie",
            min_norm_value[1],
            delta=f"{worst_perf:.1f}%"
        )
#----Zelle für Performance Ende ----


#---- Linien Diagramme zum Vergleich der Aktien----
with right_cell:
    # Daten für Plotly vorbereiten (melten)
    plot_data = normalized.reset_index().melt(
        id_vars=["Date"], 
        var_name="Aktie", 
        value_name="Normalisierter Preis"
    )
    
    # Plotly Express - alle Linien überlagert
    fig = px.line(
        plot_data,
        x="Date",
        y="Normalisierter Preis",
        color="Aktie",
        title="Normalisierte Aktienperformance",
        labels={"Normalisierter Preis": "Normalisierter Preis (Basis = 1,0)", "Date": "Datum"},
        height=460
    )
    
    # Layout anpassen für Dark Mode
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#aaa'),
        hovermode='x unified',
        margin=dict(l=30, r=30, t=50, b=40),
        xaxis_title="Datum",
        yaxis_title="Normalisierter Preis"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
#---- Ende Plot ----


#---3 Zellen Layout für weitere Analysen---
#---Technisch Analyse---
st.divider()

st.header("Technische Analyse")
st.markdown(
    "Zeigt die wichtigsten technischen Kennzahlen für die aktuell ausgewählten Aktien.\n" 
    " Die Werte basieren auf dem Tageschart und werden automatisch aktualisiert.",
    unsafe_allow_html=True,
)

summary_rows = []
for ticker in tickers:
    # bei Zeithorizont von 5 tage werden aufgrund von 
    # fehlenden daten die daten von 1 mo genommen und genügend datenpunkte anzuzeigen
    ta_horizon = HORIZON_MAP[horizon]
    if ta_horizon == "5d":
        ta_horizon = "1mo"    
    summary_rows.append(get_ta_summary_for_ticker(ticker, ta_horizon))

summary_df = pd.DataFrame(summary_rows).set_index("Ticker")

if summary_df.empty:
    st.warning("Für die ausgewählten Aktien konnten keine technischen Kennzahlen berechnet werden.")
else:
    st.dataframe(summary_df, use_container_width=True)

    first_ticker = summary_df.index[0]
    first_values = summary_df.loc[first_ticker]
    metric_cols = st.columns(4)
    metric_cols[0].metric("Ticker", first_ticker)
    metric_cols[1].metric("RSI 14", f"{first_values['RSI 14']}")
    metric_cols[2].metric("Trend", first_values['Trend'])
    metric_cols[3].metric("ATR 14", f"{first_values['ATR 14']}")
#---Ende TA---


#---Sektor Performance---
st.divider()

st.title("Weltweite ETF-Sektorperformance")

@st.cache_data(ttl=CACHE_TTL_KURSE)
def get_sector_performance(horizon_days):
    tickers = list(sektoren_etfs.values())
    raw_data = yf.download(tickers, period=f"{horizon_days}d")
    results = []
    
    if raw_data is not None and "Close" in raw_data:
        data = raw_data["Close"]
        for name, ticker in sektoren_etfs.items():
            if ticker in data.columns:
                series = data[ticker].dropna()
                if len(series) > 1:
                    perf = (series.iloc[-1] / series.iloc[0] - 1) * 100
                    results.append({
                        "Sektor": name,
                        "Performance %": round(perf, 2)
                    })
    return pd.DataFrame(results)


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
        custom_data=["Performance %"]
    )
    
    fig_tree.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
        textposition="middle center",
        textfont_size=16
    )
    fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=500)
    
    st.caption("💡 Klicke auf einen Sektor, um Top 10 Unternehmen im jeweiligen Sektor anzuzeigen.")
    
#---FIXED rerun klick logik

    #Dynamische Key, zwingt Streamlit alte Klicks zu vergessen
    chart_key = f"treemap_sektor_{auswahl}"

    #Chart zeigen
    event = st.plotly_chart(
        fig_tree, 
        use_container_width=True, 
        on_select="rerun", 
        key=chart_key
    )

    # Klick-login auswerten mit Türsteher funktion
    if event and len(event.get("selection", {}).get("points", [])) > 0:
        sektor = event["selection"]["points"][0].get("label")
        
        if sektor:
            #prüft ob Sektor geklickt wurde
            if st.session_state.last_clicked_sector != sektor:
                # merkt ob es offen ist
                st.session_state.last_clicked_sector = sektor 
                # Zeigt Popup
                zeige_top_10_bereich(sektor)
    else:
        #falls kein klick, wird es zurückgesetzt
        st.session_state.last_clicked_sector = None
