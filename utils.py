import os
import pandas as pd
from config import NAME_FILE, DATA_DIR #Pfade

# --- Name laden / speichern ---
def load_name() -> str:
    """Gespeicherten Nutzernamen aus CSV laden. Fallback: 'Besucher'."""
    if os.path.exists(NAME_FILE):
        try:
            df = pd.read_csv(NAME_FILE, header=None, encoding="utf-8")
            if not df.empty:
                return str(df.iloc[0, 0])
        except Exception:
            pass
    return "Besucher"
 
 
def save_name(name: str) -> None:
    """Nutzernamen in CSV speichern."""
    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame([name]).to_csv(NAME_FILE, index=False, header=False, encoding="utf-8")
 
 
# --- Datenbereinigung & Normalisierung ---
 
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
 
    # Komplett leere Spalten raus
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
 
    # Spalten behalten, die durchgehend Werte haben (keine Lücken in der Mitte/am Ende)
    # → erkennt delisted Aktien, die während des Zeitraums verschwunden sind
    data_valid = data_clean.ffill().bfill()
    complete_cols = data_clean.columns[data_clean.notna().sum() == len(data_clean)]
    data_valid = data_valid[complete_cols]
 
    removed = before_cols - set(data_valid.columns)
 
    if data_valid.empty:
        return data_valid, removed
 
    normalized = data_valid / data_valid.iloc[0]
    return normalized, removed