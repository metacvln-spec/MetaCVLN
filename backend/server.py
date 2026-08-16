from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import uuid
import jwt
import bcrypt
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Any, Dict

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr

from seed_data import build_seed_data

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALG = "HS256"
ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="META CVLN OS")
api = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("meta-cvln-os")


# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_password(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode(), h.encode())
    except Exception:
        return False


def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


async def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    token = None
    if creds and creds.credentials:
        token = creds.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    async def dep(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Insufficient authority_scope")
        return user
    return dep


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
class LoginBody(BaseModel):
    email: EmailStr
    password: str


class BrainQuery(BaseModel):
    question: str
    context: Optional[str] = None
    session_id: Optional[str] = None


class DecisionAction(BaseModel):
    action: str  # approve / reject / edit / escalate / pause / rollback
    comment: Optional[str] = None


class FeedbackBody(BaseModel):
    kind: str  # error / inefficiency / anomaly / opportunity / improvement / need
    subject: str
    message: str
    module: Optional[str] = None


# ------------------------------------------------------------------
# Utility: write evidence / audit
# ------------------------------------------------------------------
async def write_evidence(actor: dict, action: str, entity_type: str, entity_id: str,
                          input_data: Any = None, output_data: Any = None,
                          approval: Optional[str] = None):
    doc = {
        "id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": {"id": actor.get("id"), "email": actor.get("email"), "role": actor.get("role")},
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "input": input_data,
        "output": output_data,
        "approval": approval,
        "authority_scope": actor.get("role"),
    }
    await db.evidence.insert_one(doc)
    return doc


# ------------------------------------------------------------------
# Auth routes
# ------------------------------------------------------------------
@api.post("/auth/login")
async def login(body: LoginBody, response: Response):
    email = body.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    token = create_token(user["id"], user["email"], user["role"])
    response.set_cookie("access_token", token, httponly=True, secure=True,
                        samesite="none", max_age=7 * 24 * 3600, path="/")
    safe = {k: v for k, v in user.items() if k not in ("_id", "password_hash")}
    await write_evidence(safe, "auth.login", "user", user["id"])
    return {"token": token, "user": safe}


@api.post("/auth/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    response.delete_cookie("access_token", path="/")
    await write_evidence(user, "auth.logout", "user", user["id"])
    return {"ok": True}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return user


# ------------------------------------------------------------------
# Command Center: aggregated overview
# ------------------------------------------------------------------
@api.get("/command-center/overview")
async def command_center_overview(user: dict = Depends(get_current_user)):
    entities = await db.entities.find({}, {"_id": 0}).to_list(1000)
    alerts = await db.alerts.find({"status": "open"}, {"_id": 0}).sort("severity", -1).to_list(20)
    pending = await db.decisions.find({"status": "pending"}, {"_id": 0}).to_list(20)
    incidents = await db.incidents.find({"status": {"$ne": "resolved"}}, {"_id": 0}).to_list(10)
    projects = await db.projects.find({}, {"_id": 0}).to_list(30)
    finance = await db.finance_snapshot.find_one({}, {"_id": 0}) or {}
    agents = await db.agents.find({}, {"_id": 0}).to_list(50)
    events_24h = await db.events.count_documents({})
    workflows = await db.workflows.find({}, {"_id": 0}).to_list(30)

    active_agents = [a for a in agents if a.get("health") == "green"]
    global_health = round(
        100 * (len(active_agents) / max(len(agents), 1))
        - (0.5 * sum(1 for a in alerts if a.get("severity") == "critical")),
        1,
    )

    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "global_health": global_health,
        "entities_count": len(entities),
        "active_agents": len(active_agents),
        "agents_total": len(agents),
        "events_24h": events_24h,
        "alerts": alerts,
        "pending_decisions": pending,
        "incidents": incidents,
        "projects": projects,
        "finance": finance,
        "workflows": workflows,
        "agents": agents[:10],
        "entities": entities,
    }


@api.get("/command-center/timeline")
async def timeline(user: dict = Depends(get_current_user)):
    # last 24h aggregated by hour buckets
    buckets = await db.events.find({}, {"_id": 0}).sort("timestamp", -1).limit(500).to_list(500)
    return {"events": buckets}


# ------------------------------------------------------------------
# Generic collection listers
# ------------------------------------------------------------------
@api.get("/entities")
async def list_entities(user: dict = Depends(get_current_user)):
    return await db.entities.find({}, {"_id": 0}).to_list(200)


@api.get("/events")
async def list_events(user: dict = Depends(get_current_user)):
    return await db.events.find({}, {"_id": 0}).sort("timestamp", -1).limit(200).to_list(200)


@api.get("/agents")
async def list_agents(user: dict = Depends(get_current_user)):
    return await db.agents.find({}, {"_id": 0}).to_list(200)


@api.get("/capabilities")
async def list_capabilities(user: dict = Depends(get_current_user)):
    return await db.capabilities.find({}, {"_id": 0}).to_list(500)


@api.get("/alerts")
async def list_alerts(user: dict = Depends(get_current_user)):
    return await db.alerts.find({}, {"_id": 0}).sort("timestamp", -1).to_list(200)


# ------------------------------------------------------------------
# People OS
# ------------------------------------------------------------------
@api.get("/people/overview")
async def people_overview(user: dict = Depends(get_current_user)):
    people = await db.people.find({}, {"_id": 0}).to_list(500)
    return {
        "headcount": len(people),
        "by_entity": _group(people, "entity"),
        "by_role": _group(people, "role"),
        "people": people,
        "onboarding": [p for p in people if p.get("status") == "onboarding"],
        "absences": await db.absences.find({}, {"_id": 0}).to_list(100),
        "objectives": await db.objectives.find({}, {"_id": 0}).to_list(200),
    }


# ------------------------------------------------------------------
# Finance OS
# ------------------------------------------------------------------
@api.get("/finance/overview")
async def finance_overview(user: dict = Depends(get_current_user)):
    snap = await db.finance_snapshot.find_one({}, {"_id": 0}) or {}
    return {
        "snapshot": snap,
        "cashflow_series": snap.get("cashflow_series", []),
        "entities_pnl": snap.get("entities_pnl", []),
        "receivables": snap.get("receivables", []),
        "payables": snap.get("payables", []),
        "budgets": snap.get("budgets", []),
        "approvals": await db.decisions.find(
            {"category": "finance", "status": "pending"}, {"_id": 0}
        ).to_list(50),
    }


# ------------------------------------------------------------------
# Legal OS
# ------------------------------------------------------------------
@api.get("/legal/overview")
async def legal_overview(user: dict = Depends(get_current_user)):
    contracts = await db.contracts.find({}, {"_id": 0}).to_list(200)
    return {
        "contracts": contracts,
        "expiring_soon": [c for c in contracts if c.get("days_to_expiry", 999) <= 60],
        "risks": [c for c in contracts if c.get("risk_level") in ("high", "critical")],
        "obligations": await db.obligations.find({}, {"_id": 0}).to_list(200),
    }


# ------------------------------------------------------------------
# Ops OS
# ------------------------------------------------------------------
@api.get("/ops/overview")
async def ops_overview(user: dict = Depends(get_current_user)):
    return {
        "projects": await db.projects.find({}, {"_id": 0}).to_list(200),
        "workflows": await db.workflows.find({}, {"_id": 0}).to_list(200),
        "incidents": await db.incidents.find({}, {"_id": 0}).to_list(100),
        "tasks": await db.tasks.find({}, {"_id": 0}).to_list(500),
    }


# ------------------------------------------------------------------
# Knowledge OS
# ------------------------------------------------------------------
@api.get("/knowledge/overview")
async def knowledge_overview(user: dict = Depends(get_current_user)):
    docs = await db.documents.find({}, {"_id": 0}).to_list(500)
    return {
        "documents": docs,
        "by_source": _group(docs, "source_system"),
        "orphans": [d for d in docs if not d.get("owner")],
        "recent": sorted(docs, key=lambda d: d.get("updated_at", ""), reverse=True)[:20],
    }


# ------------------------------------------------------------------
# Decision System
# ------------------------------------------------------------------
@api.get("/decisions")
async def list_decisions(user: dict = Depends(get_current_user)):
    return await db.decisions.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)


@api.get("/decisions/{decision_id}")
async def get_decision(decision_id: str, user: dict = Depends(get_current_user)):
    d = await db.decisions.find_one({"id": decision_id}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Decision not found")
    return d


@api.post("/decisions/{decision_id}/action")
async def decide(decision_id: str, body: DecisionAction, user: dict = Depends(get_current_user)):
    d = await db.decisions.find_one({"id": decision_id})
    if not d:
        raise HTTPException(404, "Decision not found")
    if body.action not in ("approve", "reject", "edit", "escalate", "pause", "rollback"):
        raise HTTPException(400, "Invalid action")
    new_status = {
        "approve": "approved",
        "reject": "rejected",
        "edit": "editing",
        "escalate": "escalated",
        "pause": "paused",
        "rollback": "rolled_back",
    }[body.action]
    await db.decisions.update_one(
        {"id": decision_id},
        {"$set": {
            "status": new_status,
            "resolved_by": {"id": user["id"], "email": user["email"], "role": user["role"]},
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolution_comment": body.comment,
        }},
    )
    await write_evidence(user, f"decision.{body.action}", "decision", decision_id,
                          input_data={"comment": body.comment}, output_data={"status": new_status},
                          approval=body.action)
    return {"ok": True, "status": new_status}


# ------------------------------------------------------------------
# Evidence & Audit
# ------------------------------------------------------------------
@api.get("/evidence")
async def list_evidence(user: dict = Depends(get_current_user)):
    return await db.evidence.find({}, {"_id": 0}).sort("timestamp", -1).limit(200).to_list(200)


# ------------------------------------------------------------------
# Feedback
# ------------------------------------------------------------------
@api.post("/feedback")
async def create_feedback(body: FeedbackBody, user: dict = Depends(get_current_user)):
    doc = {
        "id": str(uuid.uuid4()),
        "kind": body.kind,
        "subject": body.subject,
        "message": body.message,
        "module": body.module,
        "author": {"id": user["id"], "email": user["email"]},
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.feedback.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.get("/feedback")
async def list_feedback(user: dict = Depends(get_current_user)):
    return await db.feedback.find({}, {"_id": 0}).sort("created_at", -1).limit(200).to_list(200)


# ------------------------------------------------------------------
# Workbench (personal)
# ------------------------------------------------------------------
@api.get("/workbench")
async def workbench(user: dict = Depends(get_current_user)):
    # Personal: priority tasks, own decisions, own KPIs, own projects.
    tasks = await db.tasks.find({"assignee_email": user["email"]}, {"_id": 0}).to_list(50)
    if not tasks:
        # fallback demo: any high-priority tasks
        tasks = await db.tasks.find({"priority": {"$in": ["high", "critical"]}}, {"_id": 0}).limit(6).to_list(6)
    projects = await db.projects.find({}, {"_id": 0}).limit(6).to_list(6)
    alerts = await db.alerts.find({"status": "open"}, {"_id": 0}).limit(5).to_list(5)
    decisions = await db.decisions.find({"status": "pending"}, {"_id": 0}).limit(5).to_list(5)
    person = await db.people.find_one({"email": user["email"]}, {"_id": 0}) or {}
    return {
        "profile": {**user, "person": person},
        "priority_tasks": tasks,
        "projects": projects,
        "alerts": alerts,
        "decisions_pending": decisions,
        "kpis": [
            {"label": "Décisions traitées", "value": 12, "trend": "+3"},
            {"label": "Temps de deep work", "value": "4.2h", "trend": "+18%"},
            {"label": "Alertes résolues", "value": 7, "trend": "+2"},
            {"label": "Provenance vérifiée", "value": "98%", "trend": "stable"},
        ],
    }


# ------------------------------------------------------------------
# CVL Brain — Claude Sonnet 4.6 via emergentintegrations
# ------------------------------------------------------------------
@api.post("/brain/ask")
async def brain_ask(body: BrainQuery, user: dict = Depends(get_current_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(500, "CVL Brain non configuré (EMERGENT_LLM_KEY manquant)")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    session_id = body.session_id or f"brain-{user['id']}"
    system = (
        "Tu es CVL Brain, la couche cognitive de META CVLN OS. "
        "Tu produis toujours: CONTEXT → ANALYSIS → INSIGHT → RECOMMENDATION. "
        "Chaque réponse mentionne explicitement: SOURCE, CONFIDENCE (0-100%), DATE, TRACEABILITY. "
        "Tu ne prends jamais de décision opérationnelle: tu prépares la décision humaine. "
        "L'écosystème CVLN inclut: KORA, FMS Maker Studio, FREKCORE, FREKANSLA, FREKRAW, "
        "CVLN Academy, Good Mood, Laurentia, Gala Cook & Food, LabelOS, Kiltikonet, "
        "CVLN Wallet, CVLN Blockchain, Agent Factory. "
        "Reste sobre, dense, orienté décision. Réponds en français."
    )
    if body.context:
        system += f"\n\nContexte fourni:\n{body.context}"

    chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id, system_message=system)
    chat = chat.with_model("anthropic", "claude-sonnet-4-6")
    try:
        reply = await chat.send_message(UserMessage(text=body.question))
    except Exception as e:
        log.exception("CVL Brain failed")
        raise HTTPException(502, f"CVL Brain a échoué: {str(e)[:200]}")

    doc = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": user["id"],
        "question": body.question,
        "answer": reply,
        "provenance": {
            "model": "anthropic/claude-sonnet-4-6",
            "confidence": 0.85,
            "source": "CVL Brain",
            "date": datetime.now(timezone.utc).isoformat(),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.brain_messages.insert_one(doc)
    doc.pop("_id", None)
    await write_evidence(user, "brain.ask", "brain_message", doc["id"],
                          input_data={"q": body.question[:300]},
                          output_data={"len": len(reply)})
    return doc


@api.get("/brain/history")
async def brain_history(user: dict = Depends(get_current_user)):
    session_id = f"brain-{user['id']}"
    return await db.brain_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).limit(100).to_list(100)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _group(items: List[dict], key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for it in items:
        k = it.get(key) or "unknown"
        out[k] = out.get(k, 0) + 1
    return out


# ------------------------------------------------------------------
# Seed at startup
# ------------------------------------------------------------------
@app.on_event("startup")
async def _startup():
    # Ensure admin & users
    await db.users.create_index("email", unique=True)
    admin = await db.users.find_one({"email": ADMIN_EMAIL})
    if not admin:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "password_hash": hash_password(ADMIN_PASSWORD),
            "name": "Meta CVLN Admin",
            "role": "admin",
            "authority_scope": "*",
            "entity": "CVLN Group Holding",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    else:
        if not verify_password(ADMIN_PASSWORD, admin["password_hash"]):
            await db.users.update_one({"email": ADMIN_EMAIL},
                                       {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}})

    # Seed test users
    test_users = [
        ("cfo@cvln.local", "Cvln2026!", "Camille Ferrand", "cfo", "finance_os", "CVLN Group Holding"),
        ("hr@cvln.local", "Cvln2026!", "Hana Rakoto", "hr_lead", "people_os", "CVLN Group Holding"),
        ("ops@cvln.local", "Cvln2026!", "Oscar Presley", "ops_lead", "ops_os", "KORA"),
        ("legal@cvln.local", "Cvln2026!", "Leïla Guerra", "legal_lead", "legal_os", "CVLN Group Holding"),
        ("employee@cvln.local", "Cvln2026!", "Enzo Milano", "employee", "workbench", "Good Mood"),
    ]
    for email, pw, name, role, scope, entity in test_users:
        if not await db.users.find_one({"email": email}):
            await db.users.insert_one({
                "id": str(uuid.uuid4()),
                "email": email,
                "password_hash": hash_password(pw),
                "name": name,
                "role": role,
                "authority_scope": scope,
                "entity": entity,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

    # Seed ecosystem data if empty
    if await db.entities.count_documents({}) == 0:
        seed = build_seed_data()
        for coll, items in seed.items():
            if items:
                await db[coll].insert_many(items)
        log.info("Ecosystem seed loaded")


@app.on_event("shutdown")
async def _shutdown():
    client.close()


# ------------------------------------------------------------------
# CORS + include router
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)
