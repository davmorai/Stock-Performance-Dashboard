import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import numpy as np

# 1. Definition der Sektoren und ihrer entsprechenden ETFs (S&P 500 Sektoren)
sektoren_etfs = {
    "Technology": "XLK",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB"
}

@st.cache_data(ttl="1h")
def get_sector_performance(horizon_days):
    results = []
    # Alle Ticker auf einmal herunterladen für bessere Performance
    tickers = list(sektoren_etfs.values())
    data = yf.download(tickers, period=f"{horizon_days}d")["Close"]
    
    for name, ticker in sektoren_etfs.items():
        if ticker in data.columns:
            series = data[ticker].dropna()
            if len(series) > 1:
                # Performance berechnen: (Endpreis / Startpreis) - 1
                perf = (series.iloc[-1] / series.iloc[0] - 1) * 100
                results.append({
                    "Sektor": name,
                    "Ticker": ticker,
                    "Performance %": round(perf, 2),
                    "Weight": 1 # Wir geben jedem Sektor hier das gleiche visuelle Gewicht
                })
    return pd.DataFrame(results)

# --- Streamlit UI ---
st.title("Sektor Performance Heatmap")

# Zeit-Filter
zeit_map = {"1 Woche": 7, "1 Monat": 30, "6 Monate": 180, "1 Jahr": 365}
auswahl = st.select_slider("Zeitraum wählen", options=list(zeit_map.keys()), value="1 Monat")

df_perf = get_sector_performance(zeit_map[auswahl])

if not df_perf.empty:
    # Heatmap (Treemap) erstellen
    fig = px.treemap(
        df_perf,
        path=["Sektor"], 
        values="Weight", 
        color="Performance %",
        color_continuous_scale="RdYlGn", 
        color_continuous_midpoint=0,
        # Wir übergeben die Performance-Daten als custom_data für den Hover/Text
        custom_data=["Performance %", "Ticker"],
        title="Sektor Performance Übersicht" # Titel muss ein String sein, keine Liste!
    )

    # Hier definieren wir, was auf der Kachel stehen soll
    # %{label} ist der Name des Sektors, %{customdata[0]} ist die Performance
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
        textposition="middle center",
        textfont_size=16
    )

    fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), height=500)

    st.plotly_chart(fig, use_container_width=True)