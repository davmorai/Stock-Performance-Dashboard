# Stock Performance Dashboard

A personal stock market dashboard built with Streamlit — featuring portfolio tracking, sector heatmaps, technical analysis, and real-time market data via yfinance.

---

## Features

**Portfolio Tracker**
- Compare multiple stocks over customizable time horizons (5 days to max.)
- Normalized performance chart (base = 1.0) for fair comparison
- Best/worst performer metrics at a glance
- Persistent ticker selection via URL query params

**Market Overview**
- Personalized greeting with editable name (persisted to CSV)
- Live exchange status indicators: NYSE, NASDAQ, LSE, TSE, DAX, SIX, Crypto
- VIX fear index gauge with color-coded risk levels (Low / Moderate / High)

**Technical Analysis**
- Per-ticker summary: RSI 14, MACD Diff, EMA 20/50/200, ATR 14, BB Width, Trend
- Automatically scales data window to ensure enough data points for indicators
- Built on the `ta` library with full OHLCV data from yfinance

**Sector Performance**
- ETF-based sector heatmap (treemap) using SPDR sector ETFs (XLK, XLV, XLF, ...)
- Selectable time periods: 1 week, 1 month, 6 months, 1 year, 5 years
- Click any sector to open a popup with the Top 10 companies by market cap
- Shows daily change (%) and market cap per company

---

## Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | UI framework |
| `yfinance` | Market data (stocks, ETFs, VIX) |
| `plotly` / `plotly.express` | Charts (line, treemap, gauge) |
| `pandas` | Data handling and transformation |
| `ta` | Technical analysis indicators |
| `zoneinfo` | Timezone-aware market hours |

---

## Project Structure

```
├── dashboard.py          # Main app entry point
├── config.py             # Constants (thresholds, TTLs, maps)
├── stocks.py             # Ticker lists, sector ETFs, Top 10 per sector
├── data_utils.py         # Data loading, caching, normalization, helpers
├── sektor_details.py     # Sector performance + Top 10 popup dialog
├── technical_analysis.py # TA indicators and summary per ticker
├── vix.py                # VIX gauge widget
├── time_logic.py         # Greeting logic and market open/close checks
├── styles.py             # Custom CSS injection
├── data/
│   └── name.csv          # Persisted user name
└── requirements.txt
```

---

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/davmorai/Stock-Performance-Dashboard.git
cd Stock-Performance-Dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python -m streamlit run dashboard.py
```

---

## Configuration

All tuneable constants live in `config.py`:

| Constant | Description |
|---|---|
| `VIX_LOW_THRESHOLD` | VIX below this → green (low fear) |
| `VIX_MODERATE_THRESHOLD` | VIX below this → yellow (moderate) |
| `CACHE_TTL_KURSE` | Price data cache duration (default: 6h) |
| `CACHE_TTL_SEKTOR` | Sector data cache duration (default: 1h) |
| `HORIZON_MAP` | Display name → yfinance period mapping |
| `SEKTOR_ZEIT_MAP` | Display name → days mapping for sector view |

---

## Roadmap

- [ ] Performance & Caching Optimization: Implement asynchronous/parallel data fetching and refine cache invalidation to prevent slow initial loads
- [ ] Unit-tests for edge-cases around Stock Split/ Reverse-Split and also for data utilities and TA computations
- [ ] News feed with sentiment analysis or economic calendar
- [ ] Additional TA indicators and signal overlays
- [ ] Expand stock universe beyond US markets and overall Global Etf's

---

## License

MIT — see [LICENSE](LICENSE) for details.
