# Human stock choice cockpit — proposed paper-only release

The product journey is shortlist -> Mayur's stock choice -> automatic rule-based
entry/management -> automatic journal. This source delivers the first user-facing
handoff and its durable guard. It does not claim a running forward-paper executor.

Scanner includes a choice shortlist, advisory liquidity order, read-only entry/
SL/quantity/risk review, saved selection, withdrawal, current paper position,
actual ledger fill journal and decision history. Lower-ranked stocks may be chosen.
Three choice tables initialize only on authenticated user writes. GET has no DDL.
Chosen setup, time and size envelope are immutable and content-hashed. Repeated
requests preserve the original choice. Changed request payloads, stale tabs and
competing choices conflict; pending/open/filled-today account state blocks changes.

HumanChoicePaperLedger checks the current exact stock/setup/price/risk envelope
under the same account writer lock as an entry. A changed or missing choice cannot
be used; the engine cannot substitute a liquidity winner. Source verification is
a separate requirement. The base inactive accounting library is not by itself an
authorized executor. No API exposes ledger commands, user-chosen account resets,
prices or verification flags.

Cost preview explicitly assumes Rs 1/share round trip for PAPER only. Final sizing
must be revalidated. Current receipts/universe and runtime are still unverified;
saving a choice is always SELECTED_HELD, with no simulated/broker order or fill.
Withdraw means withdraw the pending stock choice, never close an open position.
One pinned account paper-main retains one-filled-entry/day state across sessions.

Tests cover synthetic sources and future entry-command fixtures, not real market
readiness. Exact-head CI and both browser suites must pass before approval.
The cockpit browser suite covers choosing a lower-ranked stock, review, save,
withdraw, no order request, mobile overflow and clearing private data on lock.

Proposed production release: existing WEB SERVICE ONLY, no cron deployment or
flag/schedule/compute change, new service or paper/live activation. Separate
approval required. Existing research recording continues independently.
