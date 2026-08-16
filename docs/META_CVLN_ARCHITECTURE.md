# META CVLN OS — Architecture (P2 snapshot)

## Layers
- **/public** — vitrine institutionnelle
- **/commercial** — offres
- **/audit** — ledger public read-only avec .fk export
- **OS interne** (auth requise) — 18 modules

## Data plane
- MongoDB `meta_cvln_os` — collections: users, entities, agents, people, alerts, decisions, projects, contracts, documents, workflows, capabilities, events, incidents, tasks, absences, objectives, obligations, finance_snapshot, feedback, brain_messages, evidence, repositories, ping_history, frek_notarizations, signed_events, system_keys, reports, runtime_overrides, learning_proposals, doctrine_history

## Trust chain
REPO → PING → EVENT (contract v1.0) → SHA-256 → Ed25519 (local or FREKCORE remote) → DID → LEDGER → .fk EXPORT → EXTERNAL VERIFY

## Runtime
- Cron horaire `registry-ping` → auto notarize + ping_history
- Cron hebdo `weekly-drop-report` → uptime 7j + alert
- `/api/runtime/state` mode auto (normal/degraded/critical) avec hystérésis

## Contracts (v1.0 stable)
Event · Capability · RoutingDecision · SystemState · ExecutionPlan (v1.1 = Event + signature envelope)

## Adapters
labelos.push_catalogue (real, endpoint upstream missing) · wallet.transaction (real, 404 upstream) · laurentia.briefing (real, working)

## Learning loop
feedback → aggregation (manual for now) → proposal (`draft` < threshold, `pending` >= threshold) → admin approve → doctrine_history

## Tested
17/17 P2 backend pytest PASS (iteration_4.json).
