# META CVLN OS — PRD & Working Memory

## Mission
Construire le système d'exploitation du travail interne de CVLN. Automatiser la friction. Libérer le deep work.

## Doctrine
DATA → CONTEXT → PREPARATION → ORCHESTRATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK.
**Integrate before rebuild.** Meta CVLN ne réécrit jamais un système existant.

## Personas
CEO admin (metacvln@gmail.com), CFO, HR Lead, Ops Lead, Legal Lead, Employee.

## Architecture
- Backend FastAPI + MongoDB, auth FREKCORE (JWT Bearer + cookies) + RBAC
- Claude Sonnet 4.6 via Emergent LLM Key pour CVL Brain
- 18 entités démo + 12 agents + 6 décisions + 200 events

## Registry écosystème (Aug 16 2026 · 8 repos réels)
| key | github | rôle |
|---|---|---|
| frekcore | frekcore/FrekCore-JUILLET-2026 | Trust Anchor · Ed25519 Musical Proof v0.4 |
| frekansla | frekcore/FREKANSLA | Master Certifier · signed .FK containers |
| cvln_agent_factory | frekcore/CVLNAgentfactory | Agent Factory branch |
| laurentia | cultureconnectorg/Laurent.ia | Sovereign Decision Infra v1.2 (BSL 1.1) |
| cvl_academy | cultureconnectorg/CVL-ACADEMY | Formation & certification |
| kiltikonet | cultureconnectorg/Kiltikonet-Aout2026 | CC2026 Martinique + Network Phase 0-1 |
| gala_cook_food | fms-stack/GALA-cf | Gala culinaire Paris 12.12.2026 |
| fms_os | fms-os/fms | LabelOS deployment (`entity_id=labelos:fms`) |

## Automation delivered
- **Cron horaire** `.emergent/crons.yml` → `/api/cron/registry-ping-all` avec Bearer `WEBHOOK_CRON_SECRET`
- **Ping history** dans `db.ping_history` (48 pings/repo)
- **Sparkline** par repo (recharts AreaChart 140×36)
- **Notarisation FREKCORE** : SHA-256 signé sur chaque ping quand FREKCORE=CONNECTED, stocké dans `db.frek_notarizations` (7 notarisations au premier cron)
- **FMS answers** exposées via `/api/registry/fms-answers` et affichées en tête du Registry

## FMS OS · 3 réponses officielles
- Gateway URL → **B** (pas de gateway central, chaque entité expose /api/entities/{key}/... sur son propre preview URL)
- Auth preview → **B** (Bearer token émis par FREKCORE, API Key comme shim temporaire seulement)
- FMS identity → **C** (`labelos:fms` — FMS est un déploiement du domaine LabelOS, pas une entité soeur)

## Testé
- Backend 14/14 auth + modules + brain LLM
- Registry ping live : tous CONNECTED après cron ; 8 pings dans history, 7 notarisations signées
- Cron endpoint : 401 sans secret, 200 avec

## P1 backlog
- Streaming SSE natif CVL Brain
- OpenTelemetry trace_id cross-repo
- Adapters typés (labelos.push_catalogue, wallet.transaction, laurentia.briefing)
- Signer Ed25519 réel par FREKCORE (aujourd'hui SHA-256 hash seulement)

## P2 backlog
- Adaptive Runtime NORMAL/DEGRADED/CRITICAL
- Red team 7 scénarios + matrice de maturité mensuelle
- Feedback signaler UI
- Multi-tenant strict par entity
