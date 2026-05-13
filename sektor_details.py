import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Das Dictionary
top_10_sektoren = {
    "Technologie": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "AMD", "ACN", "CSCO"],
    "Gesundheitswesen": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "TMO", "DHR", "ABT", "PFE", "AMGN"],
    "Finanzwesen": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "SPGI", "GS", "MS", "AXP"],
    "Nicht-Basiskonsumgüter": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "BKNG", "TJX", "TGT"],
}

# 2. Die Daten-Logik
@st.cache_data(ttl="1h", show_spinner="Lade Unternehmensdaten...")
def get_top_10_data(sector_name):
    tickers = top_10_sektoren[sector_name]
    raw_data = yf.download(tickers, period="5d", progress=False)
    ergebnisse = []
    
    for ticker in tickers:
        try:
            close_prices = raw_data['Close'][ticker].dropna()
            tages_perf = (close_prices.iloc[-1] / close_prices.iloc[-2] - 1) * 100 if len(close_prices) >= 2 else 0.0
            
            info = yf.Ticker(ticker).info
            ergebnisse.append({
                "Ticker": ticker,
                "Unternehmen": info.get('shortName', ticker),
                "Market Cap": info.get('marketCap', 0),
                "Heute %": tages_perf
            })
        except Exception:
            continue
            
    df = pd.DataFrame(ergebnisse)
    if not df.empty:
        df = df.sort_values(by="Market Cap", ascending=False).reset_index(drop=True)
    return df

# 3. Formatierungs-Hilfen
def format_market_cap(val):
    if val >= 1e12: return f"{val/1e12:.2f} Bio. $"
    elif val >= 1e9: return f"{val/1e9:.2f} Mrd. $"
    return f"{val:,.0f} $"

def color_perf(val):
    color = '#00C851' if val > 0 else '#ff4444' if val < 0 else 'gray'
    return f'color: {color}; font-weight: bold;'

# 4. DAS IST DIE FUNKTION, DIE WIR SPÄTER AUFRUFEN
def zeige_top_10_bereich():
    st.divider()
    st.subheader("🔍 Top 10 Unternehmen im Detail")

    gewaehlter_sektor = st.selectbox("Sektor auswählen", options=list(top_10_sektoren.keys()))
    df_top10 = get_top_10_data(gewaehlter_sektor)

    if not df_top10.empty:
        df_anzeige = df_top10.copy()
        df_anzeige["Market Cap"] = df_anzeige["Market Cap"].apply(format_market_cap)
        
        styled_df = df_anzeige.style.format({
            "Heute %": "{:+.2f} %"
        }).map(color_perf, subset=["Heute %"])
        
        st.dataframe(
            styled_df,
            column_config={
                "Ticker": st.column_config.TextColumn("Symbol", width="small"),
                "Unternehmen": st.column_config.TextColumn("Name", width="medium"),
                "Market Cap": st.column_config.TextColumn("Marktkapitalisierung", width="medium"),
                "Heute %": st.column_config.TextColumn("Tagesveränderung", width="small"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Konnte keine Daten für diesen Sektor laden.")