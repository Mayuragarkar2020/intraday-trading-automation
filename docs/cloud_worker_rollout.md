# Read-only cloud preview rollout

This deployment definition is **opt-in** in `deploy/render-preview.yaml`. The original root `render.yaml` and the separate `trading-automation` service are not modified.

## Already implemented
- Browser-accessible FastAPI cockpit with token-protected scanner endpoints.
- `ScanStore`: idempotent, timestamped Postgres snapshot storage.
- `run_cloud_worker`: fifteen-second clock checks, five-minute completed-candle qualification, no broker order routes.
- Worker refuses to boot without persistent Postgres connection and dataset path.
- Dashboard latest-scan refresh.

## Not yet implemented / deployment blockers
- **No DhanHQ subscription or API feed.**
- **No DhanHQ publisher** to populate the new PostgreSQL `candle_batches` inbox. The cloud worker now reads from the database, not a local file.
- No live scan data, no broker order placement, no production login system.
- No cloud database or new service has been created.
- The stack is not ready for one-click Blueprint deployment; the YAML describes the intended components only. Verify current Render plan names, service provisions, network architecture and monthly costs before creation.
- Market calendar and special sessions must be verified from exchange data; basic weekday/session guards are insufficient for production.
- Broker account reconciliation, API rate limits, robust exception monitoring, static egress, and security hardening remain open.

The next step is a DhanHQ publisher of completed, validated five-minute candle batches into the persistent inbox, followed by live-market verification with orders disabled.
