# META CVLN OS — PRD & Working Memory

## Mission
Construire le système d'exploitation du travail interne du groupe CVLN. Automatiser la friction opérationnelle pour libérer le deep work des collaborateurs.

## Core Doctrine
DATA → CONTEXT → PREPARATION → ORCHESTRATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK

Ne jamais: AI → DECISION → ACTION sans contrôle humain sur les actions critiques.

## Personas
- CEO / Owner (metacvln@gmail.com) — Command Center global
- CFO — Finance OS + approvals
- HR Lead — People OS
- Ops Lead — Operations OS + workflows
- Legal Lead — Legal OS
- Employee — My Workbench

## Architecture livrée (v1.0 — Feb 2026)
- Backend FastAPI + MongoDB, auth JWT branded FREKCORE (Bearer + cookies), RBAC roles
- Emergent LLM Key + Claude Sonnet 4.6 pour CVL Brain
- Écosystème seedé: 18 entités (KORA, FMS, FREKCORE, Academy, Good Mood, Laurentia, Gala Cook, LabelOS, Kiltikonet, CVLN Wallet/Blockchain, Command Center, Agent Factory, CVL Brain, CVLN OS, Group Holding) + 12 agents + 6 décisions pending + 8 alertes + 8 contrats + 10 documents + 200 événements

## Modules implémentés
- Command Center (KPI globaux, timeline 24h, donut agents, alertes, décisions, écosystème)
- My Workbench (KPI perso, tâches prioritaires, décisions, projets, alertes)
- People OS, Finance OS (cashflow + PnL entités + budgets), Legal OS, Operations OS, Knowledge OS
- Work Graph (écosystème par layer)
- Agent Factory (12 agents, capabilities, actions autorisées/interdites)
- Decision System (context/sources/options/risques + approve/reject/edit/escalate/pause/rollback)
- Evidence & Audit (trace immuable de chaque action)
- CVL Brain (chat Claude Sonnet 4.6 avec provenance/confidence/date)

## Testé
Backend 14/14 PASSED (auth, tous modules, brain LLM, decision + evidence, RBAC 401)

## Backlog / Phases suivantes
- P1: Adapters pour connecter les vrais systèmes existants (KORA, FMS, FREKCORE) via les 5 contrats (Event, Capability, Routing, State, DAG)
- P1: OpenTelemetry + trace_id end-to-end
- P1: Feedback system UI (formulaire signalement error/anomaly/opportunity)
- P2: Red team 7 scénarios (Registry Poisoning, Context Poisoning, etc.)
- P2: Adaptive Runtime (NORMAL / DEGRADED / CRITICAL) avec bascule
- P2: Streaming SSE pour CVL Brain (tokens live)
- P3: Notarisation FREKCORE cross-entités (signature cryptographique par événement)
- P3: Multi-tenant strict par entity (KORA vs FMS vs Group Holding)
