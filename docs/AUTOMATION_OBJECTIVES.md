# Automation objectives and mechanics

Confirmed by Mayur, 1 November 2026. This workflow takes priority over older
automatic stock-selection assumptions.

## User experience

1. The system builds the liquid daily NSE universe and scans the whole eligible
   pool for the agreed setup. No daily manual chart checks for every stock.
2. Mayur reviews a short, ranked list and chooses WHICH STOCK/setup to trade.
   Liquidity ranking helps comparison; it must never choose or enter a different
   stock automatically. More ranking factors may be added later.
3. The system displays entry, initial SL, quantity and cost-inclusive risk. After
   the explicit choice, it watches for a later valid entry and manages the trade.
   Selecting a stock is not an immediate market order or an assured fill.
4. Once filled, the system handles protective stops, exits, partial/rejected
   fills, recovery and the post-trade journal without daily manual data entry.
   Journal: decision/setup provenance, entry/exit times and fills, size, stop
   changes, costs, realised P&L/R and exit reasons. Unresolved exposure stays visible.
5. A selected stock may be replaced/withdrawn before an order is pending. Never
   replace it with another stock automatically. Pending/open trades and a used
   daily filled-entry limit block selection changes.

## Agreed trading rules

- Daily liquid NSE universe from twenty completed sessions; preserve liquidity/
  price filters, surveillance exclusions and identity/band holds. Exclude 2%/5%.
- Completed five-minute setup: existing EMA10/20, VWAP, relative volume,
  completed 15-minute confirmation and range conditions.
- Entry above range high plus buffer; initial SL below range low minus buffer.
  Later eligible breakout only; never backdate an entry before the user's choice.
- Capital Rs 980,000; maximum planned risk Rs 9,800 including estimated costs.
  Long only, one filled entry/day, no leverage.
- Keep initial SL; EMA10-close exits apply before 1.5R too. At 1.5 price R also
  request cost breakeven. No fixed target.
- All exposure CLOSED by 15:00 IST. Flatten early enough; rejected/partial exits
  remain visible and a late recovery does not erase the deadline breach.

## Delivery and current boundary

Prioritize the human-choice cockpit, exact choice-to-entry binding, automatic
management and journaling. Data verification and source evidence support that
workflow; they are not the product objective or a reason to stop source work.

The first release is PAPER MODE. Current deployed web/research source still has
execution disabled. Actual verified-data forward paper trading and live-money
trading are not activated. Replay is a controlled test, not forward execution.
Current market/session/source readiness remains unproven. Later production
changes require approval of a concrete, tested release. No subagents.

The human-choice cockpit saves explicit paper decisions only while data/runtime
gates are incomplete. Its fixed paper cost assumption is Rs 1/share round trip,
clearly shown; it is not certified broker pricing. Final sizing must be rechecked
before entry. One pinned paper account prevents API clients resetting daily limits.

PR #13's automatic liquidity-winner path is superseded. Reuse its evidence,
accounting and management work only behind the human-choice guard; do not deploy
it unchanged. Use HumanChoicePaperLedger to validate the exact saved choice under
the same writer lock as a prospective entry. This guard does not verify source
data or activate an executor.
