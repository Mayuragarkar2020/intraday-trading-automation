# DhanHQ v2 data adapter — pre-subscription

Implemented `src/dhan_candle_adapter.py` for documented parallel-array response fields `timestamp, open, high, low, close, volume`. Source: https://dhanhq.co/docs/v2/historical-data/

**No Dhan network requests or orders are made.** The adapter only validates and converts a supplied response.

Before connecting the live API:
1. Activate the Dhan Data API subscription and configure token as a secret (never GitHub).
2. Confirm broker candle timestamps mean **open** or **close** of each five-minute interval using real, complete Dhan candles. The adapter refuses unspecified timestamp semantics.
3. Reconcile 5-minute and 15-minute bars with Dhan charts, exchange session timing, market holidays and candle availability.
4. Build an authenticated, rate-limited read-only HTTP fetcher, provide historical twenty-session slot volumes and EMA warm-up, then publish complete `BatchInput` to the Postgres candle inbox. Missing any inputs must block publishing.
5. Observe several market sessions and compare signals before enabling any trade placement.

The cloud worker is separate from the data collector; no subscription, database, or Render deployment has been activated.
