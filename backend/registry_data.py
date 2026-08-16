"""Real registry of CVLN ecosystem source repositories.

Doctrine: Meta CVLN OS DOES NOT rebuild these — it connects them.
Each entry is a source system with real metadata from the actual GitHub repo.
"""
import uuid
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


REPOSITORIES = [
    {
        "key": "frekcore",
        "name": "FREKCORE — Musical Proof Standard v0.4",
        "org": "frekcore",
        "github_url": "https://github.com/frekcore/FrekCore-JUILLET-2026",
        "branch": "main",
        "layer": "Trust Layer",
        "role": "Identity, provenance & cultural notarization",
        "description": (
            "Open protocol for verifying DJ mixes and musical performances. "
            "Cryptographic proof (Ed25519) without surveillance. Offline-first — all "
            "verification happens in browser. .frek.json format with fingerprint, "
            "segments, signature."
        ),
        "tech_stack": ["React", "Ed25519", "Zod", "SHA-256"],
        "capabilities": ["notarize_action", "verify_signature", "issue_frek_json"],
        "routes": ["/", "/industry", "/docs/*", "/app"],
        "preview_url": None,
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
            "Fabrique d'agents spécialisés. Discovery, versioning, "
            "capability registry, health & latency exposure. Reuse → compose → "
            "parallelize → create."
        ),
        "tech_stack": ["FastAPI", "React", "MongoDB"],
        "capabilities": ["create_agent", "compose_agents", "expose_capability", "heartbeat"],
        "routes": ["/", "/os"],
        "preview_url": None,
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
            "Matrice d'intelligence ancrée dans la culture, la stratégie économique "
            "et les flux financiers de la Diaspora. Semi-Open Source (BSL 1.1 → "
            "Apache 2.0 en 2029). Chat streaming SSE, AES-256-GCM at rest, "
            "HMAC-SHA256 fingerprint sans cookies, Persona anti-jailbreak v1.2. "
            "SDK Python (pip install laurentia-sdk) + widget web."
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
        "key": "kiltikonet",
        "name": "Kiltikonet — Culture Connect 2026",
        "org": "cultureconnectorg",
        "github_url": "https://github.com/cultureconnectorg/Kiltikonet",
        "branch": "main",
        "layer": "Product",
        "role": "Plateforme culturelle souveraine — Martinique",
        "description": (
            "PWA full-stack pour Culture Connect 2026 (Martinique) : accréditations, "
            "paiements Stripe live, badges NFC (Baserow sync), IA culturelle (Claude "
            "Sonnet via Emergent), gouvernance communautaire. WebAuthn Face ID/Touch "
            "ID, Google OAuth, Magic Link. Web Push VAPID. Offline-first."
        ),
        "tech_stack": [
            "React 19", "Tailwind 4", "Framer Motion", "FastAPI",
            "MongoDB Atlas", "Stripe live", "Brevo", "WebAuthn",
            "Baserow NFC", "pywebpush", "Emergent Object Storage"
        ],
        "capabilities": [
            "accreditation",
            "payment_stripe",
            "nfc_badge",
            "webauthn_auth",
            "web_push",
            "cultural_ai_query",
        ],
        "routes": ["/", "/pro", "/admin/core", "/espace-pro/connexion", "/scan"],
        "iteration": "86",
        "test_status": "backend 11/11 · frontend 100%",
        "preview_url": None,
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
            "Site public éditorial premium + back-office privé sécurisé pour le Cook "
            "& Food Gala 2026 (Paris, 12.12.2026). 45+ endpoints, 20 collections "
            "MongoDB, seeds automatiques (25 postes, 7 pôles, 7 entités écosystème), "
            "invitations VIP, contrats & NDA, cercle & mécénat."
        ),
        "tech_stack": [
            "React 19", "Tailwind", "shadcn/ui", "Framer Motion", "GSAP",
            "FastAPI", "Motor", "Pydantic v2", "JWT httpOnly",
            "Stripe test", "ReportLab", "Resend (mocked)", "Yousign (mocked)"
        ],
        "capabilities": [
            "billetterie",
            "rsvp",
            "candidatures",
            "casting",
            "sponsoring",
            "mecenat",
            "invitations_vip",
            "signature_electronique",
        ],
        "routes": [
            "/", "/concept", "/prix", "/billetterie", "/rsvp",
            "/candidatures", "/casting", "/sponsoring", "/mecenat",
            "/cercle-restreint", "/founders-circle", "/sur-invitation",
            "/contact", "/login", "/admin", "/portail"
        ],
        "preview_url": None,
        "auth_type": "bearer",
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
    {
        "key": "fms_os",
        "name": "Factory Maker Studio OS",
        "org": "fms-os",
        "github_url": "https://github.com/fms-os/fms",
        "branch": "main",
        "layer": "Product",
        "role": "Label · production · édition & distribution",
        "description": (
            "Site vitrine public + FMS OS interne (Command Center, CRUD Projets/"
            "Artistes/Clients/Bookings, A&R Kanban, Leads, Intégrations). "
            "Infrastructure client CVLN livrée : GET /api/os/integrations, "
            "PATCH config (base_url/api_key/entity_id/auth_type), POST test "
            "(ping HTTP réel), GET audit-log. Statut CONNECTED uniquement après "
            "test réussi. 7 adapters exposés en NOT_CONNECTED par défaut."
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
        "preview_url": None,
        "auth_type": "bearer",
        "open_questions": [
            "Gateway central URL vs par-entité preview ?",
            "Auth réelle preview : X-API-Key vs Bearer FREKCORE vs open ?",
            "FMS = labelos ou nouvelle entité factory_maker_studio ?",
        ],
        "adapter_status": "NOT_CONNECTED",
        "health": "green",
    },
]


def repositories_docs():
    """Return the repositories with stable IDs (idempotent seed)."""
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
