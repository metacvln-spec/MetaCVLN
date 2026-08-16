# META CVLN OS — Existing System Audit (P2 entry)

Date: Feb 16, 2026
Baseline: PRD.md

## What was already there (kept intact)
- 3 layers: /public /commercial /audit
- OS interne: Command Center, Workbench, People/Finance/Legal/Ops/Knowledge OS
- Registry (12 repos + sparkline + FMS answers), Notary Ledger (Ed25519 real, .fk export), Weekly Report
- Feedback UI, 5 contracts versioned, 3 typed adapters (labelos.push_catalogue, wallet.transaction, laurentia.briefing)
- CVL Brain (Claude Sonnet 4.6, non-streaming)
- Cron: registry-ping (hourly), weekly-drop-report (Monday 08:00 UTC)

## What was added in this P2 pass
- **Capability Auto-Discovery** — `POST /api/registry/discover-all` fetches `/api/capabilities` on every repo, sets lifecycle_status (HEALTHY/DEGRADED/UNAVAILABLE/UNKNOWN), persists discovered_capabilities + version + timestamps
- **Signed events (v1.1 extension)** — `POST /api/events/emit` and `POST /api/events/verify` — Ed25519 signature on canonical payload, key_id = notary DID, stored in `db.signed_events`
- **Adaptive Runtime** — `GET /api/runtime/state` computes mode (normal/degraded/critical) from ping_history 1h window + active incidents; `POST /api/runtime/state/override` (admin only). Hysteresis via thresholds documented
- **Learning Validation** — `/api/learning/proposals` POST/GET/approve. Threshold configurable via `LEARNING_PROPOSAL_THRESHOLD`. Doctrine history persisted with full evidence
- **Financial Loop** — `/api/finance/loop` returns 9 stages (REVENUE→COST→MARGIN→CASHFLOW→RESERVES→CAPITAL_ALLOCATION→INVESTMENT→RESULT→FEEDBACK) with real data or `DATA_NOT_AVAILABLE` flag per stage
- **Human Loop** — `/api/people/loop` returns 11 stages (ACADEMY→...→SUCCESSION) with same policy
- UI pages: `/finance-loop`, `/people-loop`, `/runtime`, `/learning`

## Statuses matrix
| Axe | Status | Evidence | Test | Remaining gap |
|---|---|---|---|---|
| Feedback UI | DONE | /feedback works | ✓ | Aggregation into proposals threshold (auto) |
| 5 contracts | DONE | /api/contracts | ✓ | — |
| Adapters | PARTIAL | laurentia OK, wallet 404 real | ✓ | wallet endpoint upstream |
| Capability Discovery | DONE (backend) | /api/registry/discover-all | ✓ | Boot auto-run once at startup |
| Signed events | DONE | /api/events/emit + verify | ✓ | Emit on more actions (decision.approve, etc) |
| Adaptive Runtime | DONE | /api/runtime/state, override | ✓ | Auto-throttle degraded/critical actions |
| Learning Validation | DONE | /api/learning/proposals | ✓ | Auto-proposal from N feedback |
| Finance Loop | DONE | /finance-loop shows N/A on missing | ✓ | Fill COST + CAPITAL_ALLOCATION + INVESTMENT stages |
| People Loop | DONE | /people-loop shows N/A on missing | ✓ | Wire cvl_academy adapter |
| OpenTelemetry | MISSING | — | — | full instrumentation |
| Red Team 7 scenarios | MISSING | — | — | implement + report |
| Brain SSE | MISSING | — | — | streaming refactor |
| Multi-tenant strict | PARTIAL | RBAC + authority_scope | — | tenant_id per doc |
| Encryption at rest | MISSING doc | — | — | see META_CVLN_SECURITY.md |
