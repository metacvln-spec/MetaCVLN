# META CVLN OS — PRD & Working Memory

## Mission
Construire le système d'exploitation du travail interne du groupe CVLN. Automatiser la friction opérationnelle pour libérer le deep work.

## Core Doctrine
DATA → CONTEXT → PREPARATION → ORCHESTRATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK.
Non-negotiable: **Integrate before rebuild** — Meta CVLN ne réécrit jamais un système existant.

## Personas
- CEO / Owner (metacvln@gmail.com) — Command Center global
- CFO — Finance OS + approvals
- HR Lead — People OS
- Ops Lead — Operations OS + workflows
- Legal Lead — Legal OS
- Employee — My Workbench

## Architecture livrée
- Backend FastAPI + MongoDB, auth JWT branded FREKCORE (Bearer + cookies), RBAC roles
- Emergent LLM Key + Claude Sonnet 4.6 pour CVL Brain (streaming disponible côté SDK)
- Écosystème démo seedé: 18 entités + 12 agents + 6 décisions pending + 8 alertes + 8 contrats + 10 documents + 200 événements

## Registry — repos sources RÉELS (Aug 16, 2026)
1. **FREKCORE** — frekcore/FrekCore-JUILLET-2026 — Ed25519 Musical Proof Standard v0.4 (offline, browser-only)
2. **CVLN Agent Factory** — frekcore/CVLNAgentfactory (branch CVLN-AGENT-FACTORY)
3. **Laurent.ia v1.2** — cultureconnectorg/Laurent.ia (public) — Sovereign Decision Infrastructure, BSL 1.1, streaming SSE, AES-256-GCM
4. **Kiltikonet CC2026** — cultureconnectorg/Kiltikonet — PWA Martinique (WebAuthn, Stripe live, NFC, Baserow)
5. **Cook & Food Gala 2026** — fms-stack/GALA-cf — 45+ endpoints, 20 collections, Stripe test
6. **FMS OS** — fms-os/fms — Factory Maker Studio, adapters config UI existant (7 adapters), audit-log

Chaque repo: preview_url + auth_type + api_key configurables. Ping HTTP réel (`GET /api/registry/repositories/{id}/ping`) met à jour `adapter_status` (CONNECTED / NOT_CONNECTED / ERROR). Toute config + ping journalisé dans `/api/evidence`.

## Modules livrés (v1.0 — Feb 2026)
- Command Center (KPI globaux + timeline 24h + donut agents + alertes + décisions + écosystème)
- My Workbench (KPI perso + tâches prioritaires + décisions + projets + alertes)
- People OS, Finance OS (cashflow + PnL entités + budgets), Legal OS, Operations OS, Knowledge OS
- Work Graph (écosystème par layer)
- **Registry** (6 repos GitHub réels + ping live + config auth)
- Agent Factory (12 agents, capabilities, actions autorisées/interdites)
- Decision System (context/sources/options/risques + approve/reject/edit/escalate/pause/rollback)
- Evidence & Audit (trace immuable, inclut registry.config.update et registry.ping)
- CVL Brain (chat Claude Sonnet 4.6 avec provenance/confidence/date)

## Testé
- Backend 14/14 PASSED (auth, tous modules, brain LLM, decision + evidence, RBAC 401)
- Registry ping live testé: FREKCORE 200 · 622ms, Laurent.ia 200 · 349ms → CONNECTED, evidence journalisée

## Backlog / P1
- Étendre Registry: schedule ping périodique (via .emergent/crons.yml), historique de disponibilité
- Adapters typés cross-repo utilisant les 5 contrats (Event/Capability/Routing/State/DAG)
- Trace ID end-to-end (OpenTelemetry) propagé entre Meta CVLN OS et chaque repo connecté
- Feedback system UI (formulaire signalement error/anomaly/opportunity)

## P2
- Adaptive Runtime NORMAL/DEGRADED/CRITICAL avec bascule automatique
- Streaming SSE natif pour CVL Brain (tokens live)
- Red team 7 scénarios + matrice de maturité mensuelle

## Backlog / P3
- Notarisation FREKCORE cross-entités (signature cryptographique par événement) branchée sur le vrai FREKCORE
- Multi-tenant strict par entity (KORA vs FMS vs Group Holding)
- Résoudre les 3 questions ouvertes FMS: Gateway URL, auth réelle, FMS=labelos?
