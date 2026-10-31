# Session contract evidence checkpoint — 31 October 2026

## Additional verified evidence

The official NSE CAS overview describes the CAS period as 15:15–15:35 and
continuous trading for non-CAS securities through 15:30. It lists the relevant
circulars, including NSE/CMTR/73362, 73845 and 74466.
Source: https://www.nseindia.com/static/products-services/closing-auction-session

The official 30 October CAS archive was fetched (HTTP 200, 29,256 bytes,
218 data rows). It contains RELIANCE, reference price 1,161.00, final price
1,164.90 and final volume 1,120,445. The raw-byte SHA-256, URL and original
RELIANCE CSV row are retained in research/2026-10-30/cas-session-observation.json.
This supports RELIANCE CAS participation on that date, not eligibility on any
future date or the complete reference-history period.
Source archive index: https://www.nseindia.com/static/reports/closing-auction-session-historical-data

The original March 18 circular NSE/CMTR/73362 was readable through the web
retriever. It describes phased applicability to cash securities with derivatives,
CAS reference-price methodology and order/closing-price rules.
Source: https://nsearchives.nseindia.com/content/circulars/CMTR73362.pdf

Dhan's historical API reference describes timestamps as epoch values; that
alone does not specify whether a five-minute candle is labelled at its start
or close. The existing independent user check supports open labels for one
30 October 09:15 RELIANCE candle only.
Source: https://dhanhq.co/docs/v2/historical-data/

## Remaining verification and policy decision

Original NSE circulars 73845 and 74466 could not be read with the available
PDF web retrieval. Search snippets/third-party copies were not treated as
primary verification of their effective date or master-field semantics.
The default Context Mode Python lacked a PDF reader. No package was installed.
No flag interpretation, complete dated session contract or new calendar is
certified from these partial sources.

Request an independent Dhan RELIANCE NSE regular five-minute chart view for
30 October around the close: last regular candle and preceding candle with
date/time/OHLC visible. Expected open-labelled final continuous candle under
the 15:15 boundary hypothesis is 15:10; that is a hypothesis to test, not an
already observed broker output. Retain the supplied independent evidence
before expanding timestamp/session verification.

For an instrument whose continuous trading ends at 15:15, a request made only
at that time cannot assume another regular candle at which to fill. An earlier
flatten request (e.g. 15:10), pending partial exits and any auction handling
must remain an explicit reviewed proposal. No exit timing was changed.

PR #9's receipt-bound journal remains inactive/research-only even when its
scanner returns ARMED. It is not connected to automatic paper execution.
