# Paper entry selection - inactive review component

Working rule accepted on 31 October 2026: among valid breakouts in the same five-minute interval, rank by descending 20-day average traded value. Equal scores use symbol then security ID for reproducibility. Future reviewed policy versions can add ranking factors without changing accounting or stop/exit rules.

`src/paper_entry_selection.py` validates one completed interval, ranks candidates, sizes within available cash and planned risk inclusive of estimated round-trip costs, and atomically reserves one prospective paper entry through the existing ledger. The immutable entry event stores the policy version, ranked candidates, source identities, decision time and selection fingerprint. Retries return the original reservation even after a fill; competing workers cannot create a second pending entry. Instrument identity follows a filled order into the position.

Selection at a completed interval cannot backdate a fill into that interval. The reservation is known at its actual decision time, and the ledger accepts only a later bar open. This is a conservative bar-based paper model, not an implementation of live intrabar trigger execution.

All four source attestations must be true before touching the database: timestamps, session contract, reference prices and breakout receipts. These declarations must eventually come from a trusted adapter; this module cannot establish their truth itself. Current research payloads remain unverified and must hold. No endpoint accepts these attestations, and no feed, API or cron imports this module.

This component reserves an order; it does not fill orders, activate paper trading or connect the manager to a running feed. The existing EMA10-close exit remains active before 1.5R; 1.5R additionally requests cost breakeven. No fixed target is introduced. Persistent manager orchestration, verified signal delivery and a reviewed end-of-day exit policy remain necessary before runtime activation.

Validation: targeted selection, ledger and signal tests cover ranking, ties, input validation, concurrent reservations, immutable retries, source holds and prevention of earlier fills. PostgreSQL and full API/browser validation run in CI. Production approval is separate from this source-only draft.

