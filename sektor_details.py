import streamlit as st
import yfinance as yf
import pandas as pd
from stocks import top_10_sektoren, SEKTOREN_ETFS
from config import CACHE_TTL_SEKTOR
 
 
#Sektorperformance
@st.cache_data(ttl=CACHE_TTL_SEKTOR)
def get_sector_performance(horizon_days: int) -> pd.DataFrame:
    """ETF-Performance pro Sektor für einen gegebenen Zeitraum in Tagen."""
    tickers = list(SEKTOREN_ETFS.values())
    raw_data = yf.download(tickers, period=f"{horizon_days}d", progress=False)
    results = []
 
    if raw_data is not None and "Close" in raw_data:
        data = raw_data["Close"]
        for name, ticker in SEKTOREN_ETFS.items():
            if ticker in data.columns:
                series = data[ticker].dropna()
                if len(series) > 1:
                    perf = (series.iloc[-1] / series.iloc[0] - 1) * 100
                    results.append({
                        "Sektor": name,
                        "Performance %": round(perf, 2),
                    })
 
    return pd.DataFrame(results)
 
 
#Top-10 pro Sektor
@st.cache_data(ttl=CACHE_TTL_SEKTOR, show_spinner="Lade aktuelle Werte...")
def get_top_10_data(sector_name: str) -> pd.DataFrame:
    """Tagesperformance und Marktkapitalisierung der Top-10 im Sektor."""
    if sector_name not in top_10_sektoren:
        return pd.DataFrame()
 
    tickers = top_10_sektoren[sector_name]
    try:
        raw_data = yf.download(tickers, period="2d", progress=False)
    except Exception:
        return pd.DataFrame()
 
    ergebnisse = []
    for ticker in tickers:
        try:
            close = (
                raw_data["Close"][ticker].dropna()
                if isinstance(raw_data["Close"], pd.DataFrame)
                else raw_data["Close"].dropna()
            )
            tages_perf = (
                (close.iloc[-1] / close.iloc[-2] - 1) * 100
                if len(close) >= 2
                else 0.0
            )
            info = yf.Ticker(ticker).info
            ergebnisse.append({
                "Ticker":      ticker,
                "Unternehmen": info.get("shortName", ticker),
                "Market Cap":  info.get("marketCap", 0),
                "Heute %":     tages_perf,
            })
        except Exception:
            continue
 
    df = pd.DataFrame(ergebnisse)
    if not df.empty:
        df = df.sort_values("Market Cap", ascending=False).reset_index(drop=True)
    return df
 
 
#Dialog
@st.dialog("🔍 Sektor Details", width="large")
def zeige_top_10_bereich(geklickter_sektor: str) -> None:
    """Popup mit Top-10-Tabelle für den angeklickten Sektor."""
    st.write(f"### Top Unternehmen im Sektor: **{geklickter_sektor}**")
 
    df = get_top_10_data(geklickter_sektor)
    if df.empty:
        st.warning("Keine Daten für diesen Sektor gefunden.")
        return
 
    df_anzeige = df.copy()
    df_anzeige["Market Cap"] = df_anzeige["Market Cap"].apply(
        lambda x: (
            f"{x/1e12:.2f} Bio. $" if x >= 1e12
            else f"{x/1e9:.2f} Mrd. $" if x >= 1e9
            else f"{x:,.0f} $"
        )
    )
 
    styled = df_anzeige.style.format({"Heute %": "{:+.2f} %"}).map(
        lambda v: f'color: {"#00C851" if float(v) > 0 else "#ff4444"}; font-weight: bold;',
        subset=["Heute %"],
    )
 
    st.dataframe(
        styled,
        column_config={
            "Ticker":      st.column_config.TextColumn("Symbol"),
            "Unternehmen": st.column_config.TextColumn("Name"),
            "Market Cap":  st.column_config.TextColumn("Marktkapitalisierung"),
            "Heute %":     st.column_config.TextColumn("Tagesveränderung"),
        },
        hide_index=True,
        use_container_width=True,
    )