# Cloud cockpit MVP — deployment disabled

This is a minimal cloud API, not a deployed trading service.

- GET /health: public health check, no personal information
- GET /api/status: authenticated, explicitly PREVIEW_ONLY
- POST /api/preview: authenticated cost-inclusive sizing preview
- No POST /api/orders endpoint; live order placement is impossible in this build.
- Set COCKPIT_ACCESS_TOKEN to a long random value before any protected endpoint use.
- Do not make the app public or store credentials in git.
- Future: persistent order journal with transaction IDs, startup reconciliation, restricted network egress/static IP, server-side order deduplication, and secure browser authentication.
- Existing Render trading-automation service must not be modified.
- A new Render web service/background worker require an explicit cost and deployment decision.
