# META CVLN OS — PRD

## Doctrine
DATA → CONTEXT → PREPARATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK.
Integrate before rebuild. 3 couches séparées : PUBLIC / OS / COMMERCIAL.

## Livré fin Feb 2026 (session cumulative)
### Couches externes
- `/public` — vitrine dense (hero, fondateur, FREKCORE focus, .fk container, 12 entités, 6 partenaires, CTA)
- `/commercial` — 4 offres (Starter/Pro/Enterprise/On-Premise)
- `/audit` — trust chain publique read-only avec download .fk

### OS interne
- Command Center · My Workbench · People / Finance / Legal / Ops / Knowledge OS · Work Graph
- **Registry** (12 repos GitHub connectés, sparkline, FMS answers, ping horaire)
- **Contracts** (5 contrats versionnés Event / Capability / RoutingDecision / SystemState / ExecutionPlan v1.0)
- **Adapters** (labelos.push_catalogue, wallet.transaction, laurentia.briefing — appels typés RBAC-gated)
- Agent Factory · Decision System (approve/reject/edit/escalate/pause/rollback)
- Evidence & Audit · **Notary Ledger** (filtres repo+status+période, .fk export) · **Weekly Report**
- **Feedback System UI** (6 types × 14 modules, kpi split par type)
- CVL Brain (Claude Sonnet 4.6 + provenance)

### Trust chain complète
REPO → PING → EVENT (contract v1.0) → SHA-256 → NOTARY (Ed25519 local ou FREKCORE remote) → DID → LEDGER → .FK EXPORT → EXTERNAL VERIFICATION

### Automation
- Cron horaire `registry-ping`
- Cron hebdomadaire `weekly-drop-report` (lundi 08:00 UTC, seuil 95%)
- FREKCORE bridge configurable par ENV (`NOTARY_MODE=frekcore` + `FREKCORE_NOTARIZE_URL`)

## Testé
- 5 contrats servis (event, capability, routing_decision, system_state, execution_plan)
- Feedback POST → evidence enregistrée
- Adapter laurentia.briefing → appel réel vers `emergent-ai-238`
- Adapter wallet.transaction → HTTP 404 real du preview (endpoint pas encore côté wallet — comportement attendu)
- 22 signatures Ed25519 + FK export vérifiable

## Reste à faire (par ordre)
### P1
- Feedback → Learning validation flow (RESULT vs EXPECTED → doctrine update)
- Boucle financière et humaine visualisées (Finance loop + Academy→Talent loop)
- Agent capability discovery automatique au boot depuis les repos connectés
- Signed events sur le bus (Ed25519 sur chaque event émis, pas seulement pings)

### P2
- Streaming SSE natif CVL Brain
- OpenTelemetry trace_id cross-repo end-to-end
- Adaptive Runtime NORMAL/DEGRADED/CRITICAL avec bascule
- Red team 7 scénarios + matrice de maturité

### P3
- Multi-tenant strict par entity (KORA vs FMS vs Group Holding)
- Secrets management + encryption at rest
- Separation of duties formalisée
