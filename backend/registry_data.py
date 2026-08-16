"""Real registry of CVLN ecosystem source repositories.

Doctrine: Meta CVLN OS DOES NOT rebuild these — it connects them.
"""
import uuid
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


# Answers to FMS OS' three blocking questions — captured here so the whole
# ecosystem can read them from a single source.
FMS_ANSWERS = {
    "gateway_url": {
        "answer": "B — no central gateway in preview. Each entity keeps its own preview URL and exposes /api/entities/{key}/... on itself.",
        "rationale": (
            "Preview URLs are per-app on Emergent ingress. A central gateway would "
            "add a hop and a single point of failure. Meta CVLN OS is the coherence "
            "layer, not a proxy: it discovers, routes, observes and notarizes."
        ),
        "consequence": (
            "FMS OS resolves each capability by looking up the preview_url of the "
            "target entity in Meta CVLN Registry, then calls it directly with the "
            "auth headers Meta CVLN publishes for that entity."
        ),
    },
    "auth_preview": {
        "answer": "B — Bearer token issued by FREKCORE (Frek-ID SSO). API Key only as a temporary shim for preview environments that cannot verify signed tokens yet.",
        "rationale": (
            "mTLS is not playable on Emergent preview ingress. FREKCORE already "
            "issues did:frek + Ed25519 identities, so Bearer JWT signed by "
            "FREKCORE is the shortest path to real cross-entity auth."
        ),
        "consequence": (
            "Meta CVLN Registry stores per-entity Authorization headers. FMS OS "
            "reads them once at login and reuses the same Bearer for every "
            "cross-entity call. Every call is journalled in Evidence & Audit."
        ),
    },
    "fms_identity": {
        "answer": "C — FMS = `labelos:fms`. FMS is a deployment of the LabelOS domain, not a new sibling entity.",
        "rationale": (
            "LabelOS is the domain (catalogue, contracts, royalties, agents "
            "production musicale). FMS is one label instance running that domain. "
            "Same contracts, same capabilities, distinguished only by the "
            "deployment prefix so cross-entity calls stay unambiguous."
        ),
        "consequence": (
            "In Registry, FMS OS keeps its own repo entry but its entity_id is "
            "`labelos:fms`. All LabelOS capabilities are available. New labels "
            "later reuse the same domain contract — `labelos:<slug>` — without "
            "creating a parallel architecture."
        ),
    },
}


REPOSITORIES = [
    {
        "key": "frekcore",
        "name": "FREKCORE — Musical Proof Standard v0.4",
        "org": "frekcore",
        "github_url": "https://github.com/frekcore/FrekCore-JUILLET-2026",
        "branch": "main",
        "layer": "Trust Layer",
        "role": "Identity, provenance & cultural notarization",
        "preview_url": "https://frekcore-certify.preview.emergentagent.com",
        "description": (
            "Open protocol for verifying DJ mixes and musical performances. "
            "Cryptographic proof (Ed25519) without surveillance. Offline-first — "
            "verification runs in browser. .frek.json format with fingerprint, "
            "segments, signature, public_key."
        ),
        "tech_stack": ["React", "Ed25519", "Zod", "SHA-256"],
        "capabilities": ["notarize_action", "verify_signature", "issue_frek_json"],
        "routes": ["/", "/industry", "/docs/*", "/app"],
        "auth_type": "none",
        "principles": [
            "FREK does not judge music",
            "FREK does not rank artists",
            "FREK does not collect personal data",
            "FREK never becomes a platform",
            "FREK works offline by default",
        ],
        "adapter_status": "NOT_CONNECTED",
        "health": "amber",
        "is_trust_anchor": True,
    },
    {
        "key": "frekansla",
        "name": "FREKANSLA v0.1 — Master Certifier & Creative Engine",
        "org": "frekcore",
        "github_url": "https://github.com/frekcore/FREKANSLA",
        "branch": "main",
        "layer": "Trust Layer",
        "role": "Master certification, signed .FK containers, provenance",
        "description": (
            "Plugin visuel (V026 Creative Engine, décor Logic Pro X simulé, macros "
            "INTENTION MORPH, DSP Web Audio réel) + Master Certifier (pipeline 4 "
            "étapes → Session Analyzer → Asset Compiler → FK Object Creator V3 → "
            "Secure Signature). FREK-ID did:frek + Ed25519 avec clés privées "
            "chiffrées Fernet. Conteneur .FK signé, journal de provenance "
            "append-only, moteur de vérification Authentique/Valide/Invalide + "
            "détection d'altération."
        ),
        "tech_stack": [
            "React", "Web Audio API", "FastAPI",
            "Ed25519", "Fernet", "Motor"
        ],
        "capabilities": [
            "creative_engine_dsp",
            "session_analyze",
            "asset_compile",
            "create_fk_object_v3",
            "sign_ed25519",
            "verify_fk",
            "detect_tampering",
        ],
        "routes": ["/", "/creative-engine", "/master-certifier"],
        "preview_url": "https://groove-studio-21.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
        "notes": "Signatures Ed25519 réelles. Ancrage FREK-Chain et publication KORA restent mockés en v0.1.",
    },
    {
        "key": "cvln_agent_factory",
        "name": "CVLN Agent Factory",
        "org": "frekcore",
        "github_url": "https://github.com/frekcore/CVLNAgentfactory",
        "branch": "CVLN-AGENT-FACTORY",
        "layer": "Control Plane",
        "role": "Agent creation, composition, reuse and lifecycle",
        "description": (
            "Fabrique d'agents spécialisés. Discovery, versioning, capability "
            "registry, health & latency exposure. Reuse → compose → parallelize → "
            "create."
        ),
        "tech_stack": ["FastAPI", "React", "MongoDB"],
        "capabilities": ["create_agent", "compose_agents", "expose_capability", "heartbeat"],
        "routes": ["/", "/os"],
        "preview_url": "https://agent-factory-68.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "laurentia",
        "name": "Laurent.ia — Sovereign Decision Infrastructure v1.2",
        "org": "cultureconnectorg",
        "github_url": "https://github.com/cultureconnectorg/Laurent.ia",
        "branch": "public",
        "layer": "Learning Plane",
        "role": "Cognition, memory, evaluation, confidence",
        "description": (
            "Matrice d'intelligence ancrée dans la culture et la stratégie "
            "économique de la Diaspora. Semi-Open Source (BSL 1.1 → Apache 2.0 en "
            "2029). Chat streaming SSE, AES-256-GCM at rest, HMAC-SHA256 "
            "fingerprint sans cookies, Persona anti-jailbreak v1.2. SDK Python "
            "(pip install laurentia-sdk) + widget web."
        ),
        "tech_stack": [
            "FastAPI", "React", "Tailwind", "MongoDB",
            "AES-256-GCM", "HMAC-SHA256", "SSE", "Ed25519"
        ],
        "capabilities": [
            "chat_stream",
            "persistence_fantome",
            "generate_recharts_json",
            "generate_artifact",
            "export_pdf_qr",
            "pipeline_echo",
        ],
        "tiers": ["Free", "Creator (15€/mo)", "Infinite (39€/mo)", "Enterprise"],
        "license": "Business Source License 1.1",
        "preview_url": None,
        "auth_type": "api_key",
        "principles": [
            "Souveraineté sensorielle",
            "Transparence contrôlée",
            "Ancrage culturel diasporique",
            "RGPD souverain J+90",
            "Zéro white-label",
        ],
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "cvl_academy",
        "name": "CVL Academy",
        "org": "cultureconnectorg",
        "github_url": "https://github.com/cultureconnectorg/CVL-ACADEMY",
        "branch": "main",
        "layer": "Product",
        "role": "Formation, montée en compétences, certification, recherche",
        "description": (
            "Plateforme d'apprentissage & recherche de l'écosystème CVLN. "
            "Contrat d'intégration défini (INTEGRATION_CONTRACT.md). Émet des "
            "événements de certification et de parcours, à connecter à FREKCORE "
            "pour notarisation cross-entités."
        ),
        "tech_stack": ["FastAPI", "React", "MongoDB"],
        "capabilities": [
            "issue_certification",
            "track_learning_path",
            "publish_research",
            "connect_frekcore",
        ],
        "routes": ["/", "/os"],
        "preview_url": "https://culture-builder-4.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "amber",
    },
    {
        "key": "kiltikonet",
        "name": "Kiltikonet — Culture Connect 2026 · Aout",
        "org": "cultureconnectorg",
        "github_url": "https://github.com/cultureconnectorg/Kiltikonet-Aout2026",
        "branch": "main",
        "layer": "Product",
        "role": "Plateforme culturelle souveraine — Martinique · Network",
        "description": (
            "PWA full-stack pour Culture Connect 2026 (Martinique) + Kiltikonet "
            "Network Phase 0 (Discovery) + Phase 1 (14 endpoints /overview /access "
            "/programmes publics, territories/operators/licenses/compliance "
            "protégés, data lineage obligatoire, RBAC 18 rôles, règle FREK-ID = "
            "retrait). Homepage refondue au mockup PNG monumental (Newsreader, "
            "carte du monde SVG 5 continents, sections 02→08 numérotées or, "
            "Observatory temps réel avec traces vérifiées)."
        ),
        "tech_stack": [
            "React 19", "Tailwind 4", "Newsreader", "Framer Motion",
            "FastAPI", "MongoDB Atlas", "Stripe live", "Brevo",
            "WebAuthn", "Baserow NFC", "pywebpush", "Emergent Object Storage"
        ],
        "capabilities": [
            "network_overview",
            "network_territories",
            "network_operators",
            "network_licenses",
            "network_compliance",
            "network_audits",
            "network_training",
            "network_signals",
            "network_governance",
            "accreditation",
            "payment_stripe",
            "nfc_badge",
            "webauthn_auth",
            "web_push",
            "observatory_public_now",
        ],
        "routes": ["/", "/pro", "/network", "/admin/core", "/espace-pro/connexion", "/scan"],
        "iteration": "97",
        "test_status": "backend + frontend 100%",
        "preview_url": "https://culture-chain.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "gala_cook_food",
        "name": "Cook & Food Gala 2026 — Chapter I",
        "org": "fms-stack",
        "github_url": "https://github.com/fms-stack/GALA-cf",
        "branch": "main",
        "layer": "Product",
        "role": "Portail gala culinaire — Paris 12.12.2026",
        "description": (
            "Site public éditorial premium + back-office privé sécurisé. 45+ "
            "endpoints, 20 collections MongoDB, seeds automatiques (25 postes, 7 "
            "pôles, 7 entités écosystème), invitations VIP, contrats & NDA, "
            "cercle & mécénat."
        ),
        "tech_stack": [
            "React 19", "Tailwind", "shadcn/ui", "Framer Motion", "GSAP",
            "FastAPI", "Motor", "Pydantic v2", "JWT httpOnly",
            "Stripe test", "ReportLab", "Resend (mocked)", "Yousign (mocked)"
        ],
        "capabilities": [
            "billetterie", "rsvp", "candidatures", "casting",
            "sponsoring", "mecenat", "invitations_vip", "signature_electronique",
        ],
        "routes": [
            "/", "/concept", "/prix", "/billetterie", "/rsvp",
            "/candidatures", "/casting", "/sponsoring", "/mecenat",
            "/cercle-restreint", "/founders-circle", "/sur-invitation",
            "/contact", "/login", "/admin", "/portail"
        ],
        "preview_url": "https://tarifs-update.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "fms_os",
        "name": "Factory Maker Studio OS (labelos:fms)",
        "org": "fms-os",
        "github_url": "https://github.com/fms-os/fms",
        "branch": "main",
        "layer": "Product",
        "role": "LabelOS deployment · production musicale, catalogue, artistes",
        "entity_id": "labelos:fms",
        "description": (
            "Site vitrine public + FMS OS interne (Command Center, CRUD Projets/"
            "Artistes/Clients/Bookings, A&R Kanban, Leads, Intégrations). "
            "Infrastructure client CVLN livrée : GET /api/os/integrations, PATCH "
            "config (base_url/api_key/entity_id/auth_type), POST test (ping HTTP "
            "réel), GET audit-log. Statut CONNECTED uniquement après test réussi. "
            "7 adapters exposés en NOT_CONNECTED par défaut."
        ),
        "tech_stack": [
            "React 19", "Cormorant Garamond", "Outfit", "IBM Plex",
            "FastAPI", "MongoDB", "JWT"
        ],
        "capabilities": [
            "os_integrations_config",
            "os_integrations_test",
            "audit_log",
            "site_config_cms",
            "projects_crud",
            "artists_crud",
            "bookings_crud",
            "a_r_kanban",
        ],
        "adapters_declared": [
            "Frek-ID", "FREKCORE", "FREKANSLA",
            "KORA", "CVLN Wallet", "CVL Brain", "Laurentia"
        ],
        "routes": ["/", "/os", "/os/cms", "/os/news", "/os/integrations"],
        "founder_email": "anbatolmq@gmail.com",
        "preview_url": "https://dsp-pipeline.preview.emergentagent.com",
        "auth_type": "bearer",
        "resolved_questions": True,
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "cvln_wallet",
        "name": "CVLN Wallet — Revolut-style",
        "org": "cvln",
        "github_url": "https://github.com/cultureconnectorg/cvln-wallet",
        "branch": "main",
        "layer": "Infrastructure",
        "role": "Possession & transfert de valeur",
        "description": (
            "Couche wallet façon Revolut : soldes multi-entités, transferts, "
            "notarisation FREKCORE de chaque transaction, ancrage CVLN Blockchain."
        ),
        "tech_stack": ["React", "FastAPI", "MongoDB"],
        "capabilities": ["wallet_balance", "wallet_transfer", "wallet_history"],
        "preview_url": "https://revolut-style-wallet.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "cvln_command_center",
        "name": "CVLN Command Center (source)",
        "org": "cvln",
        "github_url": "https://github.com/cultureconnectorg/cvln-command-center",
        "branch": "main",
        "layer": "Control Plane",
        "role": "Control plane originel — classify · route · alert",
        "description": (
            "Command Center historique de l'écosystème CVLN. Meta CVLN OS agit "
            "comme méta-vue au-dessus : il aggrège, présente et journalise, "
            "sans réécrire le CC source."
        ),
        "tech_stack": ["FastAPI", "React", "MongoDB"],
        "capabilities": ["classify_event", "route_decision", "alert"],
        "preview_url": "https://command-center-524.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "factory_ops",
        "name": "Factory Ops",
        "org": "fms-stack",
        "github_url": "https://github.com/fms-stack/factory-ops",
        "branch": "main",
        "layer": "Product",
        "role": "Opérations Factory Maker Studio",
        "description": (
            "Layer opérationnel de FMS : sessions studio, plannings, réservations. "
            "Se branche à FREKANSLA pour la certification des masters et à "
            "LabelOS/FMS pour l'export catalogue."
        ),
        "tech_stack": ["React", "FastAPI"],
        "capabilities": ["studio_sessions", "planning", "reservations"],
        "preview_url": "https://factory-ops-51.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "production_vault",
        "name": "Production Vault",
        "org": "fms-stack",
        "github_url": "https://github.com/fms-stack/production-vault",
        "branch": "main",
        "layer": "Infrastructure",
        "role": "Coffre-fort de production (assets · masters · contrats)",
        "description": (
            "Stockage souverain des masters, stems, contrats et pièces "
            "administratives. Provenance FREKCORE obligatoire pour toute pièce "
            "entrant dans le coffre."
        ),
        "tech_stack": ["FastAPI", "Object Storage"],
        "capabilities": ["vault_store", "vault_retrieve", "vault_seal_frekcore"],
        "preview_url": "https://production-vault-5.preview.emergentagent.com",
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
]


def repositories_docs():
    out = []
    for r in REPOSITORIES:
        out.append({
            **r,
            "id": f"repo-{r['key']}",
            "last_ping": None,
            "last_ping_status": None,
            "last_ping_http": None,
            "last_ping_ms": None,
            "registered_at": _now(),
        })
    return out
