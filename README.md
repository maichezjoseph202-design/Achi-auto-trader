# ACHI Auto Trader — starter project

## What this version does
- Mobile-friendly Streamlit dashboard
- XAUUSD / EURUSD selector
- Reads uploaded candle CSV data
- Calculates EMA, RSI and ATR
- Shows an educational BUY / SELL / NO SIGNAL analysis
- Starts in demo/paper-only mode and does not place broker orders

## Important limitations
- No live market feed is connected.
- No Deriv/MT5 order execution is implemented.
- No strategy can guarantee 99.9% accuracy or profits.
- Do not treat uploaded data or signals as a promise of future performance.

## Run on Replit
1. Create a new Python project.
2. Add `app.py` and `requirements.txt` from this package.
3. In the Replit Shell, install requirements if needed:
   `pip install -r requirements.txt`
4. Set the run command to:
   `streamlit run app.py --server.address 0.0.0.0 --server.port 3000`
5. Run the app.
6. Upload a CSV of verified M5 candles with columns:
   `time,open,high,low,close`

## Roadmap before live trading
1. Connect an authorized, reliable market-data source.
2. Verify symbol naming, timestamps, candle completeness, spreads and feed freshness.
3. Backtest with out-of-sample data and realistic costs.
4. Run demo/paper trading for a meaningful period.
5. Design a separate secure broker execution service with authentication, duplicate-order protection, stop-loss validation, daily loss lockout, logging, and emergency stop.
6. Enable live trading only after independent testing and explicit confirmation.

Never put broker passwords or API secrets in frontend code or a public repository.
