"""Seed data for META CVLN OS — realistic ecosystem demo."""
import uuid
import random
from datetime import datetime, timezone, timedelta


def _now(offset_hours=0):
    return (datetime.now(timezone.utc) + timedelta(hours=offset_hours)).isoformat()


def _id():
    return str(uuid.uuid4())


ENTITIES = [
    ("KORA", "Plateforme culturelle OGP", "culture", "green", "Operating"),
    ("FMS Maker Studio", "Label, production, édition & distribution", "music", "green", "Operating"),
    ("FREKCORE", "Identité, provenance et notariat culturel", "technology", "amber", "Trust Layer"),
    ("FREKANSLA", "Filiale FREK — analyses", "technology", "green", "Product"),
    ("FREKRAW", "Filiale FREK — raw data", "technology", "green", "Product"),
    ("CVLN Academy", "Formation, montée en compétence & recherche", "education", "green", "Operating"),
    ("Good Mood", "Mouvement culturel, événements & communauté", "community", "green", "Product"),
    ("Laurentia", "Recherche cognitive & apprentissage", "cognition", "amber", "Learning"),
    ("Gala Cook & Food", "Restauration & innovation culinaire", "culinary", "green", "Product"),
    ("LabelOS", "Système de labellisation & attestation", "labeling", "green", "Product"),
    ("Kiltikonet", "Entité métier", "business", "green", "Product"),
    ("CVLN Wallet", "Couche wallet / valeur", "infrastructure", "green", "Infra"),
    ("CVLN Blockchain", "Infrastructure de consensus & valeur", "infrastructure", "green", "Infra"),
    ("Command Center", "Orchestration, routing, surveillance", "system", "green", "Control"),
    ("Agent Factory", "Fabrique d'agents spécialisés", "system", "green", "Control"),
    ("CVL Brain", "Cognition, mémoire, apprentissage", "system", "green", "Learning"),
    ("CVLN OS", "Système opérationnel transverse", "system", "green", "Infra"),
    ("CVLN Group Holding", "Gouvernance et propriété du groupe", "governance", "green", "Holding"),
]


AGENTS = [
    ("Executive Briefing Agent", "briefings@cvln", "brain", "green", 0.98, 45, 0.03),
    ("Finance Agent", "finance-agent-v2", "finance_os", "green", 0.97, 52, 0.04),
    ("HR Agent", "hr-agent-v1", "people_os", "green", 0.95, 68, 0.02),
    ("Legal Agent", "legal-agent-v1", "legal_os", "amber", 0.92, 120, 0.06),
    ("Operations Agent", "ops-agent-v2", "ops_os", "green", 0.96, 55, 0.03),
    ("Research Agent", "research-agent-v1", "knowledge_os", "green", 0.94, 88, 0.05),
    ("Risk Agent", "risk-agent-v1", "risk_os", "green", 0.97, 42, 0.04),
    ("Content Analyzer v2.1", "content-v2", "knowledge_os", "green", 0.95, 61, 0.03),
    ("FrekChain Writer", "frekchain-writer", "frekcore", "green", 0.99, 38, 0.02),
    ("Routing Optimizer", "routing-opt", "command_center", "green", 0.97, 22, 0.01),
    ("Context Builder", "ctx-builder", "brain", "green", 0.93, 78, 0.04),
    ("Provenance Notary", "notary-v1", "frekcore", "green", 0.99, 34, 0.02),
]


PEOPLE = [
    ("Meta CVLN Admin", "metacvln@gmail.com", "admin", "CVLN Group Holding", "active"),
    ("Camille Ferrand", "cfo@cvln.local", "cfo", "CVLN Group Holding", "active"),
    ("Hana Rakoto", "hr@cvln.local", "hr_lead", "CVLN Group Holding", "active"),
    ("Oscar Presley", "ops@cvln.local", "ops_lead", "KORA", "active"),
    ("Leïla Guerra", "legal@cvln.local", "legal_lead", "CVLN Group Holding", "active"),
    ("Enzo Milano", "employee@cvln.local", "employee", "Good Mood", "active"),
    ("Marina Costa", "marina@cvln.local", "designer", "FMS Maker Studio", "active"),
    ("Ravi Patel", "ravi@cvln.local", "engineer", "FREKCORE", "onboarding"),
    ("Sofia Herrera", "sofia@cvln.local", "researcher", "Laurentia", "active"),
    ("Yusuf Diallo", "yusuf@cvln.local", "producer", "FMS Maker Studio", "active"),
    ("Nina Volkov", "nina@cvln.local", "curator", "KORA", "active"),
    ("Karim Idrissi", "karim@cvln.local", "chef", "Gala Cook & Food", "active"),
    ("Elena Rossi", "elena@cvln.local", "coordinator", "CVLN Academy", "active"),
    ("Thomas Chen", "thomas@cvln.local", "analyst", "FREKANSLA", "active"),
]


ALERTS = [
    ("critical", "Latence élevée détectée sur Agent Content Analyzer", "ops_os", "Agent Factory", 3),
    ("warning", "Rerouting automatique effectué", "command_center", "Routing Engine", 12),
    ("info", "Agent Factory a déployé un nouvel agent avec succès", "agent_factory", "Deployment", 45),
    ("warning", "Trésorerie sous seuil critique pour FREKANSLA", "finance_os", "Finance Agent", 90),
    ("critical", "Contrat licence KORA expire dans 14 jours", "legal_os", "Legal Agent", 240),
    ("warning", "3 collaborateurs absents non déclarés", "people_os", "HR Agent", 180),
    ("info", "Nouveau signal de marché détecté sur Good Mood", "risk_os", "Risk Agent", 320),
    ("warning", "Provenance manquante sur 8 documents Knowledge OS", "knowledge_os", "Research Agent", 400),
]


DECISIONS = [
    ("Approuver le budget R&D 2026 pour Laurentia", "finance", "high",
     "Investissement de 1.2M€ pour accélérer la recherche cognitive.",
     ["Approuver 1.2M€", "Réduire à 800k€", "Reporter à Q2", "Refuser"],
     "cfo@cvln.local"),
    ("Renouveler partenariat TRACE Caraïbes ?", "legal", "medium",
     "Contrat arrive à échéance dans 22 jours. Revenus estimés +180k€/an.",
     ["Renouveler 3 ans", "Renouveler 1 an", "Renégocier tarifs", "Ne pas renouveler"],
     "legal@cvln.local"),
    ("Recruter Head of Growth pour Good Mood ?", "people", "high",
     "Post-analyse Laurentia recommande recrutement senior.",
     ["Ouvrir poste", "Promouvoir en interne", "Consultant externe", "Reporter"],
     "hr@cvln.local"),
    ("Déprécier Agent Content Analyzer v1 ?", "ops", "medium",
     "Version 2.1 déployée. v1 encore utilisée par 3 workflows.",
     ["Déprécier immédiat", "Migration progressive 30j", "Maintenir en support"],
     "ops@cvln.local"),
    ("Publier attestation FREKCORE pour LabelOS ?", "legal", "low",
     "Provenance validée. Notarisation cross-entités.",
     ["Publier", "Réviser d'abord", "Reporter"],
     "legal@cvln.local"),
    ("Autoriser dépense marketing Q1 pour Gala Cook ?", "finance", "medium",
     "45k€ budget dédié campagne lancement nouvelle offre.",
     ["Approuver 45k€", "Réduire à 25k€", "Refuser"],
     "cfo@cvln.local"),
]


PROJECTS = [
    ("Programme FREKCORE v2", "FREKCORE", "in_progress", 62, "Q1 2026", "critical"),
    ("Refonte KORA Discovery", "KORA", "in_progress", 45, "Q2 2026", "high"),
    ("Onboarding Ravi Patel", "FREKCORE", "in_progress", 30, "3 semaines", "medium"),
    ("Launch Good Mood Season 3", "Good Mood", "planning", 15, "Q2 2026", "high"),
    ("Certification LabelOS ISO", "LabelOS", "in_progress", 78, "6 semaines", "medium"),
    ("Levée de fonds Series B", "CVLN Group Holding", "in_progress", 55, "Q2 2026", "critical"),
    ("Nouvelle carte Gala Cook", "Gala Cook & Food", "planning", 20, "Q1 2026", "low"),
    ("Migration data lake KORA", "KORA", "in_progress", 40, "Q1 2026", "high"),
]


CONTRACTS = [
    ("Partenariat TRACE Caraïbes", "KORA", "partnership", 22, "medium", "180000"),
    ("Licence CNM 2024", "FMS Maker Studio", "license", 88, "low", "45000"),
    ("Sponsoring SACEM", "FMS Maker Studio", "sponsorship", 145, "low", "80000"),
    ("Bail siège Fondation", "CVLN Group Holding", "lease", 14, "critical", "-24000"),
    ("Contrat Cloud AWS", "CVLN OS", "vendor", 210, "low", "-36000"),
    ("Contrat coach Academy", "CVLN Academy", "service", 5, "high", "12000"),
    ("Licence LabelOS Enterprise", "LabelOS", "license", 320, "low", "60000"),
    ("Accord NDA — Laurentia partner", "Laurentia", "nda", 65, "medium", "0"),
]


DOCUMENTS = [
    ("Doctrine Meta CVLN v2.1", "Command Center", "Meta CVLN Admin", "doctrine", 0.99),
    ("FREKCORE — Trust Contract v1.3", "FREKCORE", "Ravi Patel", "contract", 0.97),
    ("KORA Data Model Whitepaper", "KORA", "Nina Volkov", "technical", 0.95),
    ("Rapport Financier 2025", "CVLN Group Holding", "Camille Ferrand", "finance", 0.98),
    ("Onboarding Handbook v3", "CVLN Group Holding", "Hana Rakoto", "hr", 0.94),
    ("Manifeste Good Mood", "Good Mood", "Enzo Milano", "communication", 0.92),
    ("Laurentia — Research Report Q4", "Laurentia", "Sofia Herrera", "research", 0.90),
    ("Politique de sécurité v1.5", "CVLN OS", None, "security", 0.87),
    ("LabelOS — Certification Process", "LabelOS", "Elena Rossi", "process", 0.93),
    ("Gala Cook — Menu Concepts 2026", "Gala Cook & Food", "Karim Idrissi", "creative", 0.85),
]


WORKFLOWS = [
    ("Event KORA → Classifier → Routing → Agent → Notarisation FREKCORE", "running", "green"),
    ("FMS Release → LabelOS Attestation → Wallet Emission", "running", "green"),
    ("Academy Certification → FREKCORE Notary → CVLN Wallet Badge", "running", "green"),
    ("Finance Alert → Analysis → CFO Approval → Ledger Update", "paused", "amber"),
    ("HR Onboarding → Access Provisioning → Objectives Setup", "running", "green"),
]


CAPABILITIES = [
    ("classify_event", "content-v2", "2.1.0", 48, 0.05, "green"),
    ("summarize_document", "research-agent-v1", "1.0.4", 85, 0.08, "green"),
    ("financial_forecast", "finance-agent-v2", "2.0.1", 120, 0.12, "green"),
    ("contract_analysis", "legal-agent-v1", "1.2.0", 220, 0.18, "amber"),
    ("route_decision", "routing-opt", "1.0.0", 22, 0.01, "green"),
    ("notarize_action", "notary-v1", "1.0.2", 34, 0.02, "green"),
    ("build_context", "ctx-builder", "0.9.5", 78, 0.06, "green"),
    ("write_frekchain", "frekchain-writer", "1.1.0", 38, 0.03, "green"),
]


def build_seed_data():
    # Entities
    entities = []
    for name, desc, kind, health, layer in ENTITIES:
        entities.append({
            "id": _id(), "name": name, "description": desc,
            "kind": kind, "health": health, "layer": layer,
            "created_at": _now(-24 * 30),
        })

    # Agents
    agents = []
    for name, code, scope, health, precision, latency_p95, error_rate in AGENTS:
        agents.append({
            "id": _id(), "name": name, "code": code,
            "authority_scope": scope, "health": health,
            "precision": precision, "latency_p95_ms": latency_p95,
            "error_rate": error_rate,
            "mode": "normal", "mission": f"Exécute des tâches spécialisées sur {scope}",
            "tools": ["query_data", "call_api", "produce_recommendation"],
            "allowed_actions": ["prepare", "recommend", "notify"],
            "prohibited_actions": ["autonomous_financial_transfer", "delete_evidence"],
            "last_heartbeat": _now(-random.randint(0, 30)),
            "version": "2.1.0",
        })

    # People
    people = []
    for name, email, role, entity, status in PEOPLE:
        people.append({
            "id": _id(), "name": name, "email": email, "role": role,
            "entity": entity, "status": status,
            "start_date": _now(-random.randint(30, 900)),
            "objectives_count": random.randint(2, 5),
        })

    # Alerts
    alerts = []
    for sev, msg, module, source, mins_ago in ALERTS:
        alerts.append({
            "id": _id(), "severity": sev, "message": msg,
            "module": module, "source": source, "status": "open",
            "timestamp": _now(-mins_ago / 60),
        })

    # Decisions
    decisions = []
    for i, (title, cat, prio, ctx, opts, owner) in enumerate(DECISIONS):
        decisions.append({
            "id": _id(), "title": title, "category": cat, "priority": prio,
            "context": ctx, "options": opts, "owner_email": owner,
            "status": "pending",
            "risks": ["Impact financier", "Impact opérationnel", "Impact réputation"],
            "recommendation": opts[0] if opts else None,
            "confidence": 0.72 + i * 0.03,
            "prepared_by": "Executive Briefing Agent",
            "sources": ["Finance snapshot Q1", "Contrat courant", "Analyse Laurentia"],
            "created_at": _now(-random.randint(1, 48)),
        })

    # Projects
    projects = []
    for name, entity, status, prog, due, prio in PROJECTS:
        projects.append({
            "id": _id(), "name": name, "entity": entity,
            "status": status, "progress": prog, "due": due, "priority": prio,
            "owner": random.choice(PEOPLE)[0],
        })

    # Contracts
    contracts = []
    for name, entity, kind, days, risk, value in CONTRACTS:
        contracts.append({
            "id": _id(), "name": name, "entity": entity, "kind": kind,
            "days_to_expiry": days, "risk_level": risk,
            "annual_value_eur": int(value),
            "signed_at": _now(-365),
            "auto_renew": random.choice([True, False]),
        })

    # Documents
    documents = []
    for title, source, owner, kind, freshness in DOCUMENTS:
        documents.append({
            "id": _id(), "title": title, "source_system": source,
            "owner": owner, "kind": kind, "freshness": freshness,
            "version": f"{random.randint(1,3)}.{random.randint(0,9)}",
            "confidence": round(0.85 + random.random() * 0.14, 2),
            "updated_at": _now(-random.randint(1, 60) * 24),
        })

    # Workflows
    workflows = []
    for desc, status, health in WORKFLOWS:
        workflows.append({
            "id": _id(), "description": desc, "status": status, "health": health,
            "steps_count": desc.count("→") + 1,
            "last_run": _now(-random.randint(1, 12)),
        })

    # Capabilities
    capabilities = []
    for name, agent, version, latency, cost, health in CAPABILITIES:
        capabilities.append({
            "id": _id(), "name": name, "agent_code": agent, "version": version,
            "latency_p95_ms": latency, "cost_eur": cost, "health": health,
            "last_heartbeat": _now(-random.randint(0, 5)),
        })

    # Events (200 recent events)
    events = []
    types = ["work.updated", "decision.prepared", "alert.raised", "agent.deployed",
             "notarization.completed", "onboarding.step", "contract.review",
             "brain.query", "workflow.completed", "capability.registered"]
    sources = [e[0] for e in ENTITIES]
    for i in range(200):
        events.append({
            "id": _id(), "trace_id": _id(),
            "type": random.choice(types),
            "source_system": random.choice(sources),
            "confidence": round(0.7 + random.random() * 0.3, 2),
            "priority": random.randint(1, 5),
            "timestamp": _now(-random.randint(0, 24)),
        })

    # Incidents
    incidents = [
        {"id": _id(), "title": "Panne partielle Agent Factory", "severity": "warning",
         "status": "investigating", "opened_at": _now(-4), "entity": "Agent Factory"},
        {"id": _id(), "title": "Latence FREKCORE Notary", "severity": "info",
         "status": "monitoring", "opened_at": _now(-8), "entity": "FREKCORE"},
    ]

    # Tasks
    tasks = []
    task_titles = [
        ("Réviser proposition budget R&D", "high", "cfo@cvln.local"),
        ("Valider contrat TRACE Caraïbes", "high", "legal@cvln.local"),
        ("Préparer briefing exécutif Lundi", "critical", "metacvln@gmail.com"),
        ("Onboarding session avec Ravi", "medium", "hr@cvln.local"),
        ("Analyser rapport Laurentia Q4", "medium", "metacvln@gmail.com"),
        ("Publier attestation LabelOS", "low", "legal@cvln.local"),
        ("Approuver dépense marketing Gala", "medium", "cfo@cvln.local"),
        ("Coordonner lancement Good Mood S3", "high", "ops@cvln.local"),
        ("Signer NDA Laurentia partner", "medium", "legal@cvln.local"),
        ("Réunir équipe FMS pour release", "medium", "ops@cvln.local"),
    ]
    for title, prio, owner in task_titles:
        tasks.append({
            "id": _id(), "title": title, "priority": prio,
            "assignee_email": owner, "status": "open",
            "due": _now(random.randint(1, 7) * 24),
        })

    # Absences
    absences = [
        {"id": _id(), "person": "Marina Costa", "kind": "vacation",
         "from": _now(48), "to": _now(120), "approved": True},
        {"id": _id(), "person": "Yusuf Diallo", "kind": "sick",
         "from": _now(-24), "to": _now(24), "approved": True},
    ]

    # Objectives
    objectives = [
        {"id": _id(), "person": "Camille Ferrand", "title": "Réduire OPEX de 8%", "progress": 42},
        {"id": _id(), "person": "Hana Rakoto", "title": "Onboarder 12 talents Q1", "progress": 58},
        {"id": _id(), "person": "Oscar Presley", "title": "Zéro incident critique KORA", "progress": 88},
        {"id": _id(), "person": "Leïla Guerra", "title": "Cartographier 100% des contrats", "progress": 76},
    ]

    # Obligations
    obligations = [
        {"id": _id(), "title": "Déclaration TVA Trimestrielle", "entity": "CVLN Group Holding",
         "due_in_days": 12, "status": "pending"},
        {"id": _id(), "title": "Rapport annuel Fondation", "entity": "CVLN Group Holding",
         "due_in_days": 45, "status": "pending"},
        {"id": _id(), "title": "Audit RGPD Data OS", "entity": "CVLN OS",
         "due_in_days": 90, "status": "pending"},
    ]

    # Finance snapshot
    finance = {
        "id": _id(),
        "cash_position_eur": 5_712_400,
        "revenue_ytd_eur": 12_400_000,
        "ebitda_eur": 3_100_000,
        "runway_months": 22,
        "burn_rate_monthly_eur": 260_000,
        "gross_margin_pct": 62.4,
        "cashflow_series": [
            {"month": "Sept", "in": 950_000, "out": 780_000},
            {"month": "Oct", "in": 1_020_000, "out": 812_000},
            {"month": "Nov", "in": 1_180_000, "out": 855_000},
            {"month": "Déc", "in": 1_310_000, "out": 890_000},
            {"month": "Jan", "in": 1_140_000, "out": 920_000},
            {"month": "Fév", "in": 1_260_000, "out": 940_000},
        ],
        "entities_pnl": [
            {"entity": "KORA", "revenue": 4_200_000, "cost": 2_100_000, "margin": 2_100_000},
            {"entity": "FMS Maker Studio", "revenue": 2_800_000, "cost": 1_900_000, "margin": 900_000},
            {"entity": "FREKCORE", "revenue": 2_100_000, "cost": 1_200_000, "margin": 900_000},
            {"entity": "CVLN Academy", "revenue": 1_500_000, "cost": 900_000, "margin": 600_000},
            {"entity": "Good Mood", "revenue": 1_000_000, "cost": 800_000, "margin": 200_000},
            {"entity": "Autres", "revenue": 800_000, "cost": 600_000, "margin": 200_000},
        ],
        "receivables": [
            {"client": "TRACE Caraïbes", "amount_eur": 180_000, "days_overdue": 0},
            {"client": "Google for Startups", "amount_eur": 120_000, "days_overdue": 12},
            {"client": "SACEM", "amount_eur": 80_000, "days_overdue": 0},
        ],
        "payables": [
            {"vendor": "AWS", "amount_eur": 36_000, "due_in_days": 8},
            {"vendor": "Legal Firm", "amount_eur": 18_000, "due_in_days": 15},
        ],
        "budgets": [
            {"category": "R&D Laurentia", "allocated": 1_200_000, "spent": 480_000},
            {"category": "Marketing", "allocated": 400_000, "spent": 220_000},
            {"category": "Infrastructure", "allocated": 300_000, "spent": 180_000},
            {"category": "Talent", "allocated": 900_000, "spent": 610_000},
        ],
        "updated_at": _now(),
    }

    return {
        "entities": entities,
        "agents": agents,
        "people": people,
        "alerts": alerts,
        "decisions": decisions,
        "projects": projects,
        "contracts": contracts,
        "documents": documents,
        "workflows": workflows,
        "capabilities": capabilities,
        "events": events,
        "incidents": incidents,
        "tasks": tasks,
        "absences": absences,
        "objectives": objectives,
        "obligations": obligations,
        "finance_snapshot": [finance],
    }
