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
- **No market-data publisher** to produce the atomic JSON input referenced by `SCAN_DATASET_PATH`. The proposed file path is a placeholder; Render worker local files do not automatically become available from a web service.
- No live scan data, no broker order placement, no production login system.
- No cloud database or new service has been created.
- The stack is not ready for one-click Blueprint deployment; the YAML describes the intended components only. Verify current Render plan names, service provisions, network architecture and monthly costs before creation.
- Market calendar and special sessions must be verified from exchange data; basic weekday/session guards are insufficient for production.
- Broker account reconciliation, API rate limits, robust exception monitoring, static egress, and security hardening remain open.

The next technical step is a DhanHQ collector that writes complete closed-candle batches to a **shared persistent store**, rather than relying on a local JSON path. Make the scan worker load those batches transactionally. Then test on market hours with live orders still disabled.
