# META CVLN OS — PRD (P2 delivered + verified)

## Baseline P0+P1 (inchangée, non re-buildée)
Voir historique précédent — Registry 12 repos, Notary Ed25519, Weekly Report, Feedback, Contracts, 3 Adapters, 3 couches Public/Commercial/Audit.

## P2 livré et vérifié cette session
- **Capability Auto-Discovery** — `POST /api/registry/discover-all` sur tous les 12 repos, lifecycle_status persisté. Test live: 12/12 DEGRADED (aucun n'expose /api/capabilities → comportement réel, pas mock)
- **Signed Events (v1.1 extension)** — `POST /api/events/emit` + `/api/events/verify` Ed25519, key_id=notary DID. Test: verify VALID ✓, tampered → quarantined
- **Adaptive Runtime** — `GET /api/runtime/state` mode auto (normal/degraded/critical) avec 7 signaux persistants + policy; `POST /api/runtime/state/override` admin only. UI `/runtime` auto-refresh 15s
- **Learning Validation** — proposals POST/GET/{id}/approve, seuil `LEARNING_PROPOSAL_THRESHOLD`, doctrine_history persistée
- **Financial Loop Map** `/finance-loop` — 9 stages avec status OK|DATA_NOT_AVAILABLE, no invented data. CASHFLOW correctement OK=€1.66M
- **Human Loop Map** `/people-loop` — 11 stages, même politique
- Docs : `/docs/META_CVLN_EXISTING_SYSTEM_AUDIT.md` + `/docs/META_CVLN_SECURITY.md`

## Bugs corrigés dans cette session (rapport testing_agent iteration_2)
- LoginBody.email `EmailStr` → `str` (bloquait tous les comptes @cvln.local par RFC 6761)
- `/api/runtime/state` retourne toujours signals complets (7 clés) même sans historique
- `/api/finance/loop` CASHFLOW ne collapse plus 0 en DATA_NOT_AVAILABLE

## Vérifications live post-fix
- `POST /api/auth/login employee@cvln.local` → 200 + token ✓
- `/api/runtime/state.signals` → 7 clés ✓
- `/api/finance/loop` CASHFLOW → OK value=1663000 ✓

## Gaps réels restants (non mockés)
- 12 repos ne servent pas /api/capabilities — à implémenter côté chaque repo
- Wallet endpoint 404 réel — à créer côté cvln_wallet
- Multi-tenant strict (tenant_id doc-level), encryption at rest, OpenTelemetry, Red Team 7 scénarios, Brain SSE, boot-time auto-discovery, auto-proposal aggregation
