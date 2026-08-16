# META CVLN OS — PRD & Working Memory

## Mission
Système d'exploitation du travail interne CVLN. Doctrine: DATA → CONTEXT → PREPARATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK. **Integrate before rebuild.**

## Personas
CEO admin (metacvln@gmail.com), CFO, HR Lead, Ops Lead, Legal Lead, Employee.

## Registry écosystème (Aug 16 2026 · 12 repos réels avec preview URLs)
| key | github | preview_url |
|---|---|---|
| frekcore | FrekCore-JUILLET-2026 | frekcore-certify |
| frekansla | FREKANSLA | groove-studio-21 |
| cvln_agent_factory | CVLNAgentfactory | agent-factory-68 |
| laurentia | Laurent.ia | emergent-ai-238 |
| cvl_academy | CVL-ACADEMY | culture-builder-4 |
| kiltikonet | Kiltikonet-Aout2026 | culture-chain |
| gala_cook_food | GALA-cf | tarifs-update |
| fms_os (labelos:fms) | fms-os/fms | dsp-pipeline |
| cvln_wallet | cvln-wallet | revolut-style-wallet |
| cvln_command_center | cvln-command-center | command-center-524 |
| factory_ops | factory-ops | factory-ops-51 |
| production_vault | production-vault | production-vault-5 |

**Résultat cron: 12/12 CONNECTED · 22 notarisations Ed25519 signées**

## Notary Ledger (nouveau)
- Meta CVLN OS génère un keypair Ed25519 au premier boot (stocké dans `db.system_keys`)
- DID: `did:meta-cvln:413ba83ba91ff0ac`, algo: `ed25519`
- Chaque ping quand FREKCORE=CONNECTED produit: SHA-256 du payload + signature Ed25519 de ce hash
- Endpoints: `GET /api/notarizations` (ledger public), `POST /api/notarizations/{id}/verify` (vérification cryptographique)
- Page UI `/notarizations` avec: KPI count, clé publique + DID, ledger avec bouton VERIFY par ligne → VALID ✓
- Testé: 22 signatures créées, verify renvoie `{valid:true, algorithm:"ed25519"}`

## Automation
- **Cron horaire** `.emergent/crons.yml` → `/api/cron/registry-ping-all` avec `WEBHOOK_CRON_SECRET`
- **Ping history** 48 pings/repo + sparkline recharts par repo
- **FMS answers** — Gateway=B, Auth=B (Bearer FREKCORE), Identity=C (`labelos:fms`)

## Modules livrés
Command Center, Workbench, People/Finance/Legal/Ops/Knowledge OS, Work Graph, Registry (12 repos + sparkline + FMS answers), Agent Factory, Decision System (approve/reject/edit/escalate/pause/rollback), Evidence & Audit, **Notary Ledger**, CVL Brain (Claude Sonnet 4.6).

## P1 backlog
- Bridge Ed25519 → vrai FREKCORE notarize endpoint quand contract publié (aujourd'hui local key Meta CVLN)
- Streaming SSE natif CVL Brain
- Adapters typés cross-repo (labelos.push_catalogue, wallet.transaction, laurentia.briefing)
- OpenTelemetry trace_id cross-repo
- Weekly drop report (email lundi 9h avec repos < 95% uptime)

## P2 backlog
- Adaptive Runtime NORMAL/DEGRADED/CRITICAL
- Red team 7 scénarios + matrice de maturité
- Feedback signaler UI
- Multi-tenant strict par entity
