import os
import pandas as pd
import yfinance as yf
import streamlit as st

from config import NAME_FILE, DATA_DIR, CACHE_TTL_KURSE #Pfade

# --- Name laden / speichern ---
def load_name() -> str:
    """Lädt name von csv und falls keiner verfügbar ist dann fallback: 'Besucher'."""
    if os.path.exists(NAME_FILE):
        try:
            df = pd.read_csv(NAME_FILE, header=None, encoding="utf-8")
            if not df.empty:
                return str(df.iloc[0, 0])
        except Exception:
            pass
    return "Besucher"
 
def save_name(name: str) -> None:
    """Speichert name in /data/name.csv"""
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame([name]).to_csv(NAME_FILE, index=False, header=False, encoding="utf-8")


 #Kursdaten laden
@st.cache_data(show_spinner=False, ttl=CACHE_TTL_KURSE)
def load_data(tickers: tuple, period: str) -> pd.DataFrame:
    """
    Schlusskurse für eine Liste von Tickern laden.
    tickers als tuple übergeben, da st.cache_data keine Listen cached
    """
    tickers_obj = yf.Tickers(" ".join(tickers))
    data = tickers_obj.history(period=period)
    if data is None:
        raise RuntimeError("YFinance returned no data.")
    return data["Close"] #type: ignore


#Zeithorizont logik
def resolve_ta_horizon(period: str) -> str:
    """
    TA braucht genug Datenpunkte für EMA-200 etc.
    Bei 5d-Ansicht auf 1mo hochsetzen.
    """
    return "1mo" if period == "5d" else period

#Data Handling and Cleaning
def normalized_and_clean(data: pd.DataFrame) -> tuple[pd.DataFrame, set]:
    """
    Bereinigt und normalisiert Kursdaten.
 
    Schritte:
    - Komplett leere Spalten entfernen
    - Führende NaN-Zeilen entfernen (z.B. erste Zeile bei 1y-Daten)
    - Spalten mit Lücken in der Mitte/am Ende entfernen (Aktie delisted)
    - Verbleibende Lücken mit ffill/bfill füllen
    - Normalisieren: erste gültige Zeile = 1.0
 
    Rückgabe:
        normalized  — bereinigter, normalisierter DataFrame
        removed     — Set der entfernten Ticker
    """
    before_cols = set(data.columns)
 
    data_clean = data.dropna(axis=1, how="all")
    if data_clean.empty:
        return data_clean, before_cols
 
    # Führende NaN-Zeilen entfernen
    first_valid_idx = next(
        (idx for idx in data_clean.index if data_clean.loc[idx].notna().any()),
        None,
    )
    if first_valid_idx is None:
        return pd.DataFrame(), before_cols
 
    data_clean = data_clean.loc[first_valid_idx:]
 
    #es werden nur spalten beibehalten die Werte haben- also falls delistet dann weg
    data_valid = data_clean.ffill().bfill()
    complete_cols = data_clean.columns[data_clean.notna().sum() == len(data_clean)]
    data_valid = data_valid[complete_cols]
 
    removed = before_cols - set(data_valid.columns)
 
    if data_valid.empty:
        return data_valid, removed
 
    normalized = data_valid / data_valid.iloc[0]
    return normalized, removed

#Hilfsfunktionen für sektor-Performance
def format_marketcap(x: float) -> str:
    if x >= 1e12:
        return f"{x/1e12:.2f} Bio. $"
    if x >= 1e9:
        return f"{x/1e9:.2f} Mrd. $"
    return f"{x:,.0f} $"

def style_daychange(v: float | str) -> str:
    color = "#00C851" if float(v) > 0 else "#ff4444"
    return f"color: {color}; font-weight: bold;"


