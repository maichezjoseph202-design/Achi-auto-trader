import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ACHI Auto Trader", page_icon="🤖", layout="wide")

st.title("🤖 ACHI Auto Trader")
st.caption("XAUUSD & EURUSD • M5 strategy lab • Demo-first")

st.warning(
    "SAFETY MODE: This starter project does NOT place real-money orders and does not claim "
    "live prices. No strategy can guarantee 99.9% accuracy or profits. Connect and verify "
    "a legitimate broker/data feed and test in demo mode before considering live execution."
)

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Trading mode", ["Demo / paper only"], index=0)
    symbol = st.selectbox("Market", ["XAUUSD", "EURUSD"])
    timeframe = st.selectbox("Timeframe", ["M5"])
    ema_fast = st.number_input("Fast EMA", min_value=2, max_value=100, value=20)
    ema_slow = st.number_input("Slow EMA", min_value=5, max_value=300, value=50)
    rsi_period = st.number_input("RSI period", min_value=2, max_value=50, value=14)
    risk_pct = st.number_input("Planned risk per trade (%)", min_value=0.1, max_value=0.5, value=0.5, step=0.1)
    daily_loss_pct = st.number_input("Daily loss stop (%)", min_value=0.5, max_value=2.0, value=2.0, step=0.5)
    st.caption("Risk settings are safeguards, not guarantees.")

st.subheader("Market data")
st.write(
    "Upload a CSV of candle data to analyze it. Required columns: "
    "`time`, `open`, `high`, `low`, `close`. Data must be for the selected market and M5 timeframe."
)
uploaded = st.file_uploader("Upload candle CSV", type=["csv"])

def rsi(series, period):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

if uploaded is None:
    st.info("No market data loaded. ACHI will not produce a trade signal until you upload verified candle data.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Market", symbol)
    c2.metric("Timeframe", timeframe)
    c3.metric("Status", "NO DATA")
    st.stop()

try:
    df = pd.read_csv(uploaded)
    df.columns = [str(c).strip().lower() for c in df.columns]
    required = {"time", "open", "high", "low", "close"}
    if not required.issubset(df.columns):
        st.error("CSV missing required columns. Required: time, open, high, low, close.")
        st.stop()
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time", "open", "high", "low", "close"]).sort_values("time")
    if len(df) < max(int(ema_slow), int(rsi_period)) + 5:
        st.error("Not enough candles for these indicator settings. Upload more rows.")
        st.stop()
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        st.error("Prices must be positive.")
        st.stop()
except Exception as e:
    st.error(f"Could not read the CSV: {e}")
    st.stop()

df["ema_fast"] = df["close"].ewm(span=int(ema_fast), adjust=False).mean()
df["ema_slow"] = df["close"].ewm(span=int(ema_slow), adjust=False).mean()
df["rsi"] = rsi(df["close"], int(rsi_period))
df["atr"] = atr(df, 14)

last = df.iloc[-1]
previous = df.iloc[-2]
bullish_candle = last["close"] > last["open"]
bearish_candle = last["close"] < last["open"]

signal = "NO SIGNAL"
reason = "Conditions are not aligned."
if pd.notna(last["rsi"]) and last["ema_fast"] > last["ema_slow"] and 50 <= last["rsi"] <= 70 and bullish_candle:
    signal = "BUY (DEMO ANALYSIS)"
    reason = "Fast EMA above slow EMA, RSI bullish, and last candle closed bullish."
elif pd.notna(last["rsi"]) and last["ema_fast"] < last["ema_slow"] and 30 <= last["rsi"] <= 50 and bearish_candle:
    signal = "SELL (DEMO ANALYSIS)"
    reason = "Fast EMA below slow EMA, RSI bearish, and last candle closed bearish."

m1, m2, m3, m4 = st.columns(4)
m1.metric("Market", symbol)
m2.metric("Latest uploaded close", f'{last["close"]:.5f}')
m3.metric("RSI", "N/A" if pd.isna(last["rsi"]) else f'{last["rsi"]:.1f}')
m4.metric("Signal", signal)

st.write("**Signal explanation:**", reason)
st.write(f'**Latest candle timestamp:** {last["time"]}')
st.write(f'**EMA {ema_fast}:** {last["ema_fast"]:.5f}  |  **EMA {ema_slow}:** {last["ema_slow"]:.5f}  |  **ATR(14):** {last["atr"]:.5f}')
st.caption("Signals are educational technical-analysis examples based on the uploaded file, not verified live quotes or financial advice.")

st.subheader("Price and EMA chart")
chart_df = df.set_index("time")[["close", "ema_fast", "ema_slow"]].tail(250)
st.line_chart(chart_df)

st.subheader("Recent candles and indicators")
st.dataframe(df[["time", "open", "high", "low", "close", "ema_fast", "ema_slow", "rsi", "atr"]].tail(20), use_container_width=True)

st.subheader("Risk checklist (not an order)")
st.write(f"- Planned risk cap: **{risk_pct:.1f}%** per trade.")
st.write(f"- Daily stop threshold: **{daily_loss_pct:.1f}%**.")
st.write("- No order has been sent. Position sizing requires verified account equity, contract specifications, tick value, spread, and stop distance.")
st.write("- Automatic live execution is intentionally not enabled in this starter build.")

with st.expander("CSV format example"):
    st.code("time,open,high,low,close\n2026-10-23 10:00:00,2500.0,2502.0,2498.0,2501.0\n2026-10-23 10:05:00,2501.0,2504.0,2500.0,2503.0", language="csv")
