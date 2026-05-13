
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go #nur für Vix Widget
import plotly.express as px #alle Plots
import os

from stocks import STOCKS, DEFAULT_STOCKS, SEKTOREN_ETFS as sektoren_etfs
from time_logic import begruessung, aktuell, std_min, nyse_nasdaq, lse, tse, crypto, local_tz,jetzt
from sektor_details import zeige_top_10_bereich

st.set_page_config(
    page_title="Aktien Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
# --- Speichervariablen initialisieren ---

#--Header Zellen---
# CSS Header
st.markdown("""
    <style>
    .date-text {
        color: #666;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: -10px;
    }
    .greeting-container {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .greeting-text {
        color: white;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
    .name-text {
        color: #4CAF50; /* Das Grün aus dem Bild */
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
    }
    /* Versteckt den Standard-Label vom Input */
    div[data-testid="stTextInput"] label {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)


#---Name checken und speichern in data.csv---
DATA_DIR = "data"
NAME_FILE = os.path.join(DATA_DIR, "name.csv")


def load_name():
    if os.path.exists(NAME_FILE):
        try:
            df = pd.read_csv(NAME_FILE, header=None, encoding="utf-8")
            if not df.empty:
                return str(df.iloc[0, 0])
        except Exception:
            pass
    return "Besucher"

def save_name(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame([name]).to_csv(NAME_FILE, index=False, header=False, encoding="utf-8")

#---Edit Mode

if 'name' not in st.session_state:
    st.session_state.name = load_name()
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

#----Ende Name Check---


# Datum, Begrüßung und VIX in einer Zeile
header_left, header_right = st.columns([0.75, 0.25], gap="xsmall")

#Name und Datum
with header_left:
    st.markdown(f'<p class="date-text">{jetzt.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)

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


    #Grün öffen/ Grau geschlossen
    color_active = "#4CAF50"  # Grün
    color_inactive = "#666"  # Grau

    #Logik von Öffnunszeiten
    crypto_color = color_active
    nyse_nasdaq_color = color_active if nyse_nasdaq else color_inactive
    lse_color = color_active if lse else color_inactive
    tse_color = color_active if tse else color_inactive
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
    vix_value = None
    try:
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")
        if not vix_data.empty:
            vix_value = round(vix_data['Close'].iloc[-1], 1)
    except Exception:
        vix_value = None

    if vix_value is None:
        st.markdown('<div style="color: #aaa; font-size: 0.85rem;">VIX data unavailable</div>', unsafe_allow_html=True)
    else:
        if vix_value < 15:
            vix_status = "Low"
            vix_color = "#4CAF50"
        elif vix_value < 25:
            vix_status = "Moderate"
            vix_color = "#FFB300"
        else:
            vix_status = "High"
            vix_color = "#FF4B4B"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=vix_value,
            number={'font': {'color': '#ffffff', 'size': 26}},
            gauge={
                'axis': {'range': [None, 80], 'tickwidth': 1, 'tickcolor': '#999'},
                'bar': {'color': vix_color},
                'bgcolor': '#1f2937',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 15], 'color': "#1e5e42"},
                    {'range': [15, 25], 'color': "#725d1e"},
                    {'range': [25, 80], 'color': "#551d1d"},
                ],
            },
            domain={'x': [0, 1], 'y': [0, 1]},
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        # Gib links (l) und rechts (r) etwa 15-20 Pixel Platz für die Zahlen
        # Unten (b) reichen ca. 10 Pixel, damit der Text nicht den Boden berührt
            margin=dict(t=20, b=10, l=20, r=20), 
            height=140,
        # WICHTIG: Die Breite muss für einen Halbkreis bei 140px Höhe mindestens bei ca. 250 liegen!
            width=250 
        )

        with st.container(border=True):
            st.markdown('<div style="font-size: 0.75rem; color: #aaa; letter-spacing: 0.15em; ''text-transform: uppercase; margin-bottom: -5px;">VIX</div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div style="text-align:center; color: {vix_color}; font-weight: 600; font-size: 0.8rem; margin-top: -8px;">{vix_status}</div>', unsafe_allow_html=True)

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

#Zeitmapping
horizon_map = {
    "5 Tage": "5d", "1 Monat": "1mo", "3 Monate": "3mo", "6 Monate": "6mo",
    "1 Jahr": "1y", "2 Jahre": "2y", "5 Jahre": "5y", "10 Jahre": "10y", "20 Jahre": "20y", "Max.": "max"
}

#Zelle mit Zeithorizont Auswahl
with top_left_cell:
    selected_horizon = st.pills("Zeithorizont", options=list(horizon_map.keys()), default="6 Monate")
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


# ---- Normalisierungs- und Cleaning-Funktion ----
def normalized_and_clean(data):
    """
    Normalisiert Daten und entfernt Spalten mit fehlenden Werten.
    - Spalten die komplett leer sind → entfernen
    - Führende NaN-Reihen entfernen (z.B. erste Reihe bei 1y)
    - Spalten mit NaN in der Mitte oder am Ende → entfernen (Aktie nicht mehr im System)
    - Restliche Lücken füllen mit ffill/bfill
    Normalisieren: erste gültige Reihe = 1.0

    """
    before_cols = set(data.columns)
    data_clean = data.dropna(axis=1, how='all')
    if data_clean.empty:
        return data_clean, before_cols

    # Führende NaN-Reihen entfernen (z.B. bei 1y-Daten)
    first_valid_idx = None
    for idx in data_clean.index:
        if data_clean.loc[idx].notna().any():
            first_valid_idx = idx
            break
    
    if first_valid_idx is None:
        return pd.DataFrame(), before_cols
    
    data_clean = data_clean.loc[first_valid_idx:]
    
    # Spalten prüfen auf fehlende Daten in der Mitte oder am Ende
    data_valid = data_clean.ffill().bfill()  # Füllen für temporäre Lücken
    
    # Aber: Spalten mit NaN-Werten in den Original-Daten entfernen
    # Das erkennt Aktien, die während des Zeitraums verschwunden sind
    data_valid = data_valid[data_clean.columns[data_clean.notna().sum() == len(data_clean)]]
    
    after_cols = set(data_valid.columns)
    removed = before_cols - after_cols

    if len(data_valid) > 0:
        normalized = data_valid / data_valid.iloc[0]
    else:
        normalized = data_valid

    return normalized, removed
# ---- Ende Normalisierung ----


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
    data = load_data(tickers, horizon_map[horizon])
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

# 2. Daten bereinigen UND die Variable 'normalized' erstellen
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

st.divider()

"""


Hier kommt was schönes!



"""

#---Sektor Performance---
st.divider()

st.title("Weltweite Sektor Performance")

@st.cache_data(ttl="1h")
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


zeit_map = {"1 Woche": 7, "1 Monat": 30, "6 Monate": 180, "1 Jahr": 365, "5 Jahr": 1825}
auswahl = st.select_slider("Zeitraum wählen", options=list(zeit_map.keys()), value="1 Monat")

df_perf = get_sector_performance(zeit_map[auswahl])

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

    event = st.plotly_chart(fig_tree, use_container_width=True, on_select="rerun")
    
    if event and len(event.selection.points) > 0:
        sektor = event.selection.points[0]["label"]
        zeige_top_10_bereich(sektor)

#---4 Zelle (TA- Technische Analysis)

#RSI


#MCDA

#Volume

#Options Trend

#


#---Ende TA---


#--- 5 Zeile News---