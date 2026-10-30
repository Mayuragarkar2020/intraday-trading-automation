# Live source verification — 2026-10-30

GitHub Actions workflow: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41056540857

The GitHub-hosted probe successfully fetched:
- NSE CM UDiFF bhavcopy for 2026-09-25 (204425-byte ZIP, 34 CSV headers). Sample EQ row: TradDt=2026-09-25, symbol=20MICRONS, ISIN=INE144J01027, close=217.58, volume=101345, turnover=21981347.25.
- Dhan detailed master (34342386 bytes, 33 CSV headers). Sample NSE E EQ row: ISIN=INE885A01032, security ID=100, ASM_GSM_FLAG=N, BUY_SELL_INDICATOR=A.

The fields required by the current ingestion and broker-control modules are present. This establishes header compatibility on these particular source files, not complete production validation. NSE sample was historical; all 20 consecutive exchange sessions, date-scoped restrictions, and cross-source universe coverage remain untested.

The source probe performs network access only; it does not submit orders or create a Render service.
