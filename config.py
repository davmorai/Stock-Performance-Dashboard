 
# --- Dateipfade ---
DATA_DIR  = "data"
NAME_FILE = "data/name.csv"
 
# --- VIX ---
VIX_TICKER    = "^VIX"
VIX_MAX_RANGE = 80
 
VIX_LOW_THRESHOLD      = 15
VIX_MODERATE_THRESHOLD = 25
 
VIX_COLOR_LOW      = "#4CAF50"
VIX_COLOR_MODERATE = "#FFB300"
VIX_COLOR_HIGH     = "#FF4B4B"
 
# --- Markt-Farben (Öffnungsstatus) ---
COLOR_MARKET_OPEN   = "#4CAF50"
COLOR_MARKET_CLOSED = "#666666"
 
# --- Zeithorizonte (Anzeigename → yfinance period) ---
HORIZON_MAP = {
    "5 Tage":   "5d",
    "1 Monat":  "1mo",
    "3 Monate": "3mo",
    "6 Monate": "6mo",
    "1 Jahr":   "1y",
    "2 Jahre":  "2y",
    "5 Jahre":  "5y",
    "10 Jahre": "10y",
    "20 Jahre": "20y",
    "Max.":     "max",
}
 
# --- Sektorperformance-Zeiträume (Anzeigename → Tage) ---
SEKTOR_ZEIT_MAP = {
    "1 Woche":  7,
    "1 Monat":  30,
    "6 Monate": 180,
    "1 Jahr":   365,
    "5 Jahre":  1825,
}
 
# --- Cache TTL ---
CACHE_TTL_KURSE   = 6 * 60 * 60   # 6 Stunden  (Kursdaten)
CACHE_TTL_SEKTOR  = 60 * 60        # 1 Stunde   (Sektordaten)