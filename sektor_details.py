import streamlit as st
import yfinance as yf
import pandas as pd

# Dictionary mit den Top-Aktien pro Sektor
top_10_sektoren = {
    "Technologie": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "AMD", "ACN", "CSCO"],
    "Gesundheitswesen": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "TMO", "DHR", "ABT", "PFE", "AMGN"],
    "Finanzwesen": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "SPGI", "GS", "MS", "AXP"],
    "Nicht-Basiskonsumgüter": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "BKNG", "TJX", "TGT"],
    "Kommunikationsdienste": ["GOOGL", "META", "NFLX", "DIS", "CMCSA", "TMUS", "VZ", "T", "CHTR", "EA"],
    "Industrie": ["GE", "CAT", "HON", "BA", "UNP", "UPS", "RTX", "LMT", "DE", "ADP"],
    "Basiskonsumgüter": ["PG", "PEP", "KO", "WMT", "COST", "PM", "MO", "MDLZ", "TGT", "CL"],
    "Energie": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "WMB"],
    "Versorger": ["NEE", "DUK", "SO", "SRE", "AEP", "D", "EXC", "XEL", "ED", "PEG"],
    "Immobilien": ["PLD", "AMT", "EQIX", "WELL", "PSA", "SPG", "O", "DLR", "CSGP", "CCI"],
    "Rohstoffe": ["LIN", "SHW", "FCX", "ECL", "NEM", "APD", "NUE", "DOW", "CTVA", "VMC"]
}

@st.cache_data(ttl="1h", show_spinner="Lade aktuelle Werte...")
def get_top_10_data(sector_name):
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
            close_prices = raw_data['Close'][ticker].dropna() if isinstance(raw_data['Close'], pd.DataFrame) else raw_data['Close'].dropna()
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

# POP UP menü anzeigen mit top10
@st.dialog("🔍 Sektor Details", width="large")

def zeige_top_10_bereich(geklickter_sektor):
    st.write(f"### Top Unternehmen im Sektor: **{geklickter_sektor}**")
    
    df_top10 = get_top_10_data(geklickter_sektor)

    if not df_top10.empty:
        df_anzeige = df_top10.copy()
        df_anzeige["Market Cap"] = df_anzeige["Market Cap"].apply(
            lambda x: f"{x/1e12:.2f} Bio. $" if x >= 1e12 else (f"{x/1e9:.2f} Mrd. $" if x >= 1e9 else f"{x:,.0f} $")
        )
        
        styled_df = df_anzeige.style.format({"Heute %": "{:+.2f} %"}).map(
            lambda val: f'color: {"#00C851" if val > 0 else "#ff4444"}; font-weight: bold;', 
            subset=["Heute %"]
        )
        
        st.dataframe(
            styled_df,
            column_config={
                "Ticker": st.column_config.TextColumn("Symbol"),
                "Unternehmen": st.column_config.TextColumn("Name"),
                "Market Cap": st.column_config.TextColumn("Marktkapitalisierung"),
                "Heute %": st.column_config.TextColumn("Tagesveränderung"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Keine Daten für diesen Sektor gefunden.")