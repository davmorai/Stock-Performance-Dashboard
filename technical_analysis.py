import importlib
import pandas as pd
import yfinance as yf
import streamlit as st


def _import_ta_class(module_name: str, class_name: str):
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError as exc:
        raise ImportError(
            "technical Analysis paket notwendig"
            "Run: pip install ta"
        ) from exc


def _normalize_yfinance_columns(data: pd.DataFrame) -> pd.DataFrame:
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = data.columns.get_level_values(0)
    return data


@st.cache_data(ttl=6 * 60 * 60)
def load_ohlcv_data(ticker: str, period: str) -> pd.DataFrame:
    """OHLCV Data laden"""
    data = yf.download(ticker, period=period, interval="1d")
    if data is None or data.empty:
        return pd.DataFrame()
    data = _normalize_yfinance_columns(data)
    if not set(["Open", "High", "Low", "Close", "Volume"]).issubset(data.columns):
        return pd.DataFrame()
    return data[["Open", "High", "Low", "Close", "Volume"]]


def _ensure_series(series_or_frame):
    if isinstance(series_or_frame, pd.DataFrame):
        return series_or_frame.iloc[:, 0]
    return series_or_frame


def compute_ta_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Data in dataframe umwandeln"""
    if df.empty:
        return df

    df = df.copy()
    df = df.sort_index()
    df = df.ffill().bfill()

    RSIIndicator = _import_ta_class("ta.momentum", "RSIIndicator")
    EMAIndicator = _import_ta_class("ta.trend", "EMAIndicator")
    SMAIndicator = _import_ta_class("ta.trend", "SMAIndicator")
    MACD = _import_ta_class("ta.trend", "MACD")
    BollingerBands = _import_ta_class("ta.volatility", "BollingerBands")
    AverageTrueRange = _import_ta_class("ta.volatility", "AverageTrueRange")
    OnBalanceVolumeIndicator = _import_ta_class("ta.volume", "OnBalanceVolumeIndicator")

    close = _ensure_series(df["Close"])
    high = _ensure_series(df["High"])
    low = _ensure_series(df["Low"])
    volume = _ensure_series(df["Volume"])

    df["rsi_14"] = RSIIndicator(close, window=14, fillna=True).rsi()
    ema_20 = EMAIndicator(close, window=20, fillna=True)
    ema_50 = EMAIndicator(close, window=50, fillna=True)
    ema_200 = EMAIndicator(close, window=200, fillna=True)
    df["ema_20"] = ema_20.ema_indicator()
    df["ema_50"] = ema_50.ema_indicator()
    df["ema_200"] = ema_200.ema_indicator()
    df["sma_50"] = SMAIndicator(close, window=50, fillna=True).sma_indicator()

    macd = MACD(close, window_slow=26, window_fast=12, window_sign=9, fillna=True)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    bb = BollingerBands(close, window=20, window_dev=2, fillna=True)
    df["bb_h"] = bb.bollinger_hband()
    df["bb_l"] = bb.bollinger_lband()
    df["bb_m"] = bb.bollinger_mavg()
    df["bb_width"] = df["bb_h"] - df["bb_l"]

    df["atr_14"] = AverageTrueRange(high, low, close, window=14, fillna=True).average_true_range()
    df["obv"] = OnBalanceVolumeIndicator(close, volume, fillna=True).on_balance_volume()

    return df


def get_ta_summary_for_ticker(ticker: str, period: str) -> pd.Series:
    """Letzte Ticker Info anzeigen"""
    df = load_ohlcv_data(ticker, period)
    if df.empty:
        return pd.Series({"Ticker": ticker})

    ta = compute_ta_indicators(df)
    latest = ta.iloc[-1]
    trend = "Bullish" if latest["ema_20"] > latest["ema_50"] else "Bearish"

    return pd.Series(
        {
            "Ticker": ticker,
            "RSI 14": round(float(latest["rsi_14"]), 1),
            "MACD Diff": round(float(latest["macd_diff"]), 3),
            "EMA 20": round(float(latest["ema_20"]), 2),
            "EMA 50": round(float(latest["ema_50"]), 2),
            "EMA 200": round(float(latest["ema_200"]), 2),
            "ATR 14": round(float(latest["atr_14"]), 2),
            "BB Width": round(float(latest["bb_width"]), 2),
            "Trend": trend,
        }
    )
