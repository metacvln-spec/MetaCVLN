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
from registry_data import repositories_docs
from contracts import contracts_catalog, ALL_CONTRACTS

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
    email: str
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
# Registry — real CVLN ecosystem source repositories (integrate, do not rebuild)
# ------------------------------------------------------------------
class RegistryConfigBody(BaseModel):
    preview_url: Optional[str] = None
    auth_type: Optional[str] = None  # api_key / bearer / mtls / none
    api_key: Optional[str] = None
    notes: Optional[str] = None


@api.get("/registry/repositories")
async def list_repositories(user: dict = Depends(get_current_user)):
    docs = await db.repositories.find({}, {"_id": 0, "api_key": 0}).to_list(50)
    return {"repositories": docs, "count": len(docs)}


@api.patch("/registry/repositories/{repo_id}")
async def config_repository(repo_id: str, body: RegistryConfigBody,
                             user: dict = Depends(get_current_user)):
    repo = await db.repositories.find_one({"id": repo_id})
    if not repo:
        raise HTTPException(404, "Repository not found")
    upd = {k: v for k, v in body.model_dump().items() if v is not None}
    if upd:
        await db.repositories.update_one({"id": repo_id}, {"$set": upd})
    await write_evidence(user, "registry.config.update", "repository", repo_id,
                          input_data={"fields": list(upd.keys())})
    return {"ok": True, "updated": list(upd.keys())}


# ------------------------------------------------------------------
# FREKCORE-compatible Ed25519 notary (real signatures)
# ------------------------------------------------------------------
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization
import base64 as _b64
import hashlib as _hashlib


async def _get_or_create_notary_key():
    """Meta CVLN OS holds an Ed25519 keypair used to notarize until the
    external FREKCORE notarize endpoint contract is published."""
    doc = await db.system_keys.find_one({"name": "meta-cvln-notary"})
    if doc:
        priv = Ed25519PrivateKey.from_private_bytes(_b64.b64decode(doc["private_b64"]))
        return priv, doc["public_b64"], doc.get("did", "did:meta-cvln:notary")
    priv = Ed25519PrivateKey.generate()
    priv_raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pub_b64 = _b64.b64encode(pub_raw).decode()
    did = f"did:meta-cvln:{_hashlib.sha256(pub_raw).hexdigest()[:16]}"
    await db.system_keys.insert_one({
        "name": "meta-cvln-notary",
        "algorithm": "ed25519",
        "did": did,
        "public_b64": pub_b64,
        "private_b64": _b64.b64encode(priv_raw).decode(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return priv, pub_b64, did


async def _notarize_via_frekcore(digest: str) -> Optional[Dict[str, Any]]:
    """Attempt to notarize via the real FREKCORE endpoint (POST /api/notarize).

    Expected contract (FREKCORE side):
        POST {FREKCORE_NOTARIZE_URL}
        Authorization: Bearer {FREKCORE_API_KEY}
        Body: {"sha256": "<hex>", "issuer": "meta-cvln-os"}
        Response: {"signature_b64": "...", "public_key_b64": "...",
                   "did": "did:frek:...", "algorithm": "ed25519",
                   "anchored_at": "iso", "chain_ref": "frek-chain://..."}

    Returns None if not configured or on any error, in which case caller
    falls back to the local Meta CVLN key.
    """
    import asyncio
    import requests as _rq
    url = os.environ.get("FREKCORE_NOTARIZE_URL", "").strip()
    if not url or os.environ.get("NOTARY_MODE", "local").lower() != "frekcore":
        return None
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("FREKCORE_API_KEY", "")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    def _do():
        try:
            r = _rq.post(url, headers=headers, json={
                "sha256": digest, "issuer": "meta-cvln-os"
            }, timeout=8)
            if r.status_code < 300:
                return r.json()
        except Exception as e:
            log.warning(f"FREKCORE notarize failed, falling back to local: {e}")
        return None

    return await asyncio.to_thread(_do)


@api.get("/notarizations")
async def list_notarizations(
    user: dict = Depends(get_current_user),
    repo_key: Optional[str] = None,
    status: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = 200,
):
    q: Dict[str, Any] = {}
    if repo_key:
        q["target_repo_key"] = repo_key
    if status:
        q["status"] = status
    if since or until:
        rng: Dict[str, Any] = {}
        if since:
            rng["$gte"] = since
        if until:
            rng["$lte"] = until
        q["created_at"] = rng
    docs = await db.frek_notarizations.find(q, {"_id": 0}).sort("created_at", -1).limit(min(limit, 500)).to_list(500)
    key = await db.system_keys.find_one({"name": "meta-cvln-notary"}, {"_id": 0, "private_b64": 0})
    return {"notarizations": docs, "notary": key or {}, "count": len(docs), "filters": q}


@api.get("/notarizations/{notarization_id}/export")
async def export_notarization(notarization_id: str, user: dict = Depends(get_current_user)):
    n = await db.frek_notarizations.find_one({"id": notarization_id}, {"_id": 0})
    if not n:
        raise HTTPException(404, "Notarization not found")
    return _build_fk_container(n)


# --- FK container (FREKANSLA FK Object v3 format) --------------------
def _build_fk_container(n: dict) -> dict:
    """Return a signed FK container (FREKANSLA FK Object v3 compatible)."""
    return {
        "fk_version": "3.0",
        "schema": "fk.object.v3",
        "issuer": "meta-cvln-os",
        "issued_at": n.get("created_at"),
        "event": {
            "id": n["id"],
            "trace_id": n.get("trace_id"),
            "type": n.get("target_type"),
            "target_id": n.get("target_id"),
            "target_repo_key": n.get("target_repo_key"),
            "target_repo_name": n.get("target_repo_name"),
            "status": n.get("status"),
            "http": n.get("http"),
            "ms": n.get("ms"),
            "created_at": n.get("created_at"),
        },
        "provenance": [
            {"stage": "observation", "actor": "meta-cvln-os.registry", "at": n.get("created_at")},
            {"stage": "hash", "actor": "meta-cvln-os.notary", "algorithm": "sha256"},
            {"stage": "signature", "actor": n.get("notary_source", "local"),
             "algorithm": "ed25519", "did": n.get("notary_did")},
        ],
        "fingerprint": {"algorithm": "sha256", "value": n["sha256"]},
        "signature": {"algorithm": "ed25519", "value": n["signature_b64"]},
        "public_key": {"algorithm": "ed25519", "value": n["public_key_b64"]},
        "notary": {
            "did": n.get("notary_did"),
            "source": n.get("notary_source", "local"),
            "algorithm": n.get("algorithm", "ed25519"),
            "chain_ref": n.get("chain_ref"),
            "anchored_at": n.get("anchored_at"),
        },
        "verification": {
            "method": "ed25519.verify(public_key, signature, sha256_hex.encode())",
            "off_platform": True,
        },
    }


# --- Public read-only ledger (no auth) - external auditors -------
@api.get("/public/notarizations")
async def public_ledger(repo_key: Optional[str] = None, status: Optional[str] = None,
                        since: Optional[str] = None, limit: int = 50):
    q: Dict[str, Any] = {}
    if repo_key: q["target_repo_key"] = repo_key
    if status: q["status"] = status
    if since: q["created_at"] = {"$gte": since}
    docs = await db.frek_notarizations.find(q, {"_id": 0}).sort("created_at", -1).limit(min(limit, 200)).to_list(200)
    key = await db.system_keys.find_one({"name": "meta-cvln-notary"}, {"_id": 0, "private_b64": 0}) or {}
    return {"notary": key, "notarizations": docs, "count": len(docs)}


@api.get("/public/notarizations/{notarization_id}/fk")
async def public_fk(notarization_id: str):
    n = await db.frek_notarizations.find_one({"id": notarization_id}, {"_id": 0})
    if not n:
        raise HTTPException(404, "Notarization not found")
    return _build_fk_container(n)


# --- Weekly Drop Report ------------------------------------------
@api.get("/reports/weekly-drop/latest")
async def latest_weekly_report(user: dict = Depends(get_current_user)):
    doc = await db.reports.find_one({"kind": "weekly-drop"}, {"_id": 0}, sort=[("created_at", -1)])
    return doc or {}


@api.get("/reports/weekly-drop")
async def list_weekly_reports(user: dict = Depends(get_current_user)):
    return await db.reports.find({"kind": "weekly-drop"}, {"_id": 0}).sort("created_at", -1).limit(20).to_list(20)


async def _compute_weekly_drop_report() -> dict:
    """Aggregate ping_history for last 7 days per repo, flag < 95%."""
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$repo_key",
            "total": {"$sum": 1},
            "up": {"$sum": {"$cond": [{"$eq": ["$status", "CONNECTED"]}, 1, 0]}},
            "avg_ms": {"$avg": "$ms"},
        }},
    ]
    rows = []
    async for r in db.ping_history.aggregate(pipeline):
        total = r["total"] or 1
        uptime = round(100.0 * r["up"] / total, 2)
        rows.append({
            "repo_key": r["_id"],
            "total_pings": total,
            "up": r["up"],
            "uptime_pct": uptime,
            "avg_ms": int(r["avg_ms"] or 0),
            "flag": uptime < 95.0,
        })
    rows.sort(key=lambda x: x["uptime_pct"])
    flagged = [r for r in rows if r["flag"]]
    return {
        "id": str(uuid.uuid4()),
        "kind": "weekly-drop",
        "period_days": 7,
        "since": since,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "threshold_pct": 95.0,
        "rows": rows,
        "flagged": flagged,
        "flagged_count": len(flagged),
        "total_repos": len(rows),
    }


@app.post("/api/cron/weekly-drop-report")
async def cron_weekly_report(request: Request):
    secret = os.environ.get("WEBHOOK_CRON_SECRET", "")
    auth = request.headers.get("Authorization", "")
    if not secret or not auth.startswith("Bearer ") or auth[7:] != secret:
        raise HTTPException(status_code=401, detail="Invalid webhook auth")
    report = await _compute_weekly_drop_report()
    await db.reports.insert_one(dict(report))
    # Also raise an alert per flagged repo
    for f in report["flagged"]:
        await db.alerts.insert_one({
            "id": str(uuid.uuid4()),
            "severity": "warning",
            "message": f"Uptime {f['uptime_pct']}% < 95% pour {f['repo_key']} (7j)",
            "module": "reports",
            "source": "Weekly Drop Report",
            "status": "open",
            "timestamp": report["created_at"],
        })
    return {"ok": True, "flagged_count": report["flagged_count"], "report_id": report["id"]}


@api.post("/notarizations/{notarization_id}/verify")
async def verify_notarization(notarization_id: str, user: dict = Depends(get_current_user)):
    n = await db.frek_notarizations.find_one({"id": notarization_id}, {"_id": 0})
    if not n:
        raise HTTPException(404, "Notarization not found")
    key = await db.system_keys.find_one({"name": "meta-cvln-notary"})
    if not key:
        return {"valid": False, "reason": "no_key"}
    try:
        pub = Ed25519PublicKey.from_public_bytes(_b64.b64decode(key["public_b64"]))
        pub.verify(_b64.b64decode(n["signature_b64"]), n["sha256"].encode())
        return {"valid": True, "algorithm": "ed25519", "notary_did": key["did"]}
    except Exception as e:
        return {"valid": False, "reason": str(e)[:120]}


# ------------------------------------------------------------------
# Signed events — Ed25519 on every important event (extension v1.1)
# ------------------------------------------------------------------
async def _sign_payload(payload: str) -> Dict[str, Any]:
    priv, pub_b64, did = await _get_or_create_notary_key()
    sig = priv.sign(payload.encode())
    return {
        "algorithm": "ed25519",
        "key_id": did,
        "signature_b64": _b64.b64encode(sig).decode(),
        "public_key_b64": pub_b64,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "sha256": _hashlib.sha256(payload.encode()).hexdigest(),
    }


@api.post("/events/emit")
async def emit_signed_event(payload: Dict[str, Any], user: dict = Depends(get_current_user)):
    """Emit a signed event on the internal bus. Extension of Event v1.0
    keeps backward-compat by nesting the signature envelope."""
    event_id = str(uuid.uuid4())
    trace_id = payload.get("trace_id") or str(uuid.uuid4())
    body = {
        "contract": "event", "version": "1.0",
        "id": event_id, "trace_id": trace_id,
        "type": payload.get("type", "custom"),
        "source_system": payload.get("source_system", "meta-cvln-os"),
        "payload": payload.get("payload", {}),
        "priority": payload.get("priority", 3),
        "confidence": payload.get("confidence", 1.0),
        "actor": {"id": user["id"], "email": user["email"], "role": user["role"]},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    canonical = f"{body['id']}|{body['trace_id']}|{body['type']}|{body['timestamp']}"
    sig = await _sign_payload(canonical)
    body["signed"] = True
    body["signature_b64"] = sig["signature_b64"]
    body["public_key_b64"] = sig["public_key_b64"]
    body["key_id"] = sig["key_id"]
    await db.signed_events.insert_one(dict(body))
    return body


@api.post("/events/verify")
async def verify_signed_event(payload: Dict[str, Any]):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey as _Pub
    try:
        canonical = f"{payload['id']}|{payload['trace_id']}|{payload['type']}|{payload['timestamp']}"
        pub = _Pub.from_public_bytes(_b64.b64decode(payload["public_key_b64"]))
        pub.verify(_b64.b64decode(payload["signature_b64"]), canonical.encode())
        return {"valid": True, "algorithm": "ed25519", "key_id": payload.get("key_id")}
    except Exception as e:
        return {"valid": False, "reason": str(e)[:120], "action": "quarantined"}


# ------------------------------------------------------------------
# Capability Auto-Discovery
# ------------------------------------------------------------------
@api.post("/registry/discover-all")
async def discover_all(user: dict = Depends(get_current_user)):
    """Attempt GET /api/capabilities on every repo with a preview_url and
    store discovered capabilities + set lifecycle_status."""
    import asyncio
    import requests as _rq
    import time

    repos = await db.repositories.find({}, {"_id": 0}).to_list(50)
    results = []

    def _fetch(url, headers):
        t0 = time.time()
        try:
            r = _rq.get(url, headers=headers, timeout=6)
            ms = int((time.time() - t0) * 1000)
            try:
                data = r.json()
            except Exception:
                data = None
            return r.status_code, ms, data, None
        except Exception as e:
            return None, int((time.time() - t0) * 1000), None, str(e)[:200]

    for r in repos:
        base = r.get("preview_url")
        if not base:
            await db.repositories.update_one(
                {"id": r["id"]},
                {"$set": {"lifecycle_status": "UNKNOWN", "discovery_at": datetime.now(timezone.utc).isoformat()}}
            )
            results.append({"repo": r["key"], "status": "UNKNOWN", "reason": "no_preview_url"})
            continue
        headers = {}
        if r.get("auth_type") == "bearer" and r.get("api_key"):
            headers["Authorization"] = f"Bearer {r['api_key']}"
        elif r.get("auth_type") == "api_key" and r.get("api_key"):
            headers["X-API-Key"] = r["api_key"]
        url = base.rstrip("/") + "/api/capabilities"
        code, ms, data, err = await asyncio.to_thread(_fetch, url, headers)
        if code and code < 400 and isinstance(data, list):
            lifecycle = "HEALTHY"
            discovered = data
        elif code and code == 404:
            lifecycle = "DEGRADED"
            discovered = []
        elif code is None:
            lifecycle = "UNAVAILABLE"
            discovered = []
        else:
            lifecycle = "DEGRADED"
            discovered = []
        upd = {
            "lifecycle_status": lifecycle,
            "discovery_at": datetime.now(timezone.utc).isoformat(),
            "discovery_http": code,
            "discovery_ms": ms,
            "discovery_error": err,
            "discovered_capabilities": discovered,
            "discovered_capabilities_count": len(discovered),
        }
        await db.repositories.update_one({"id": r["id"]}, {"$set": upd})
        results.append({"repo": r["key"], "status": lifecycle, "http": code, "ms": ms,
                        "capabilities_count": len(discovered)})
        await write_evidence(user, "registry.discover", "repository", r["id"],
                              output_data={"lifecycle": lifecycle, "count": len(discovered)})

    return {"results": results, "healthy": sum(1 for x in results if x["status"] == "HEALTHY"),
            "degraded": sum(1 for x in results if x["status"] == "DEGRADED"),
            "unavailable": sum(1 for x in results if x["status"] == "UNAVAILABLE"),
            "total": len(results)}


# ------------------------------------------------------------------
# Adaptive Runtime (NORMAL / DEGRADED / CRITICAL)
# ------------------------------------------------------------------
async def _compute_runtime_mode() -> dict:
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    recent = await db.ping_history.find({"timestamp": {"$gte": since}}, {"_id": 0}).to_list(500)
    active_incidents = await db.incidents.count_documents({"status": {"$ne": "resolved"}})
    if not recent:
        return {
            "mode": "normal" if active_incidents == 0 else "degraded",
            "reason": "no ping signal in window",
            "signals": {
                "window": "1h",
                "total_pings": 0,
                "up_pings": 0,
                "error_rate": 0.0,
                "avg_ms": 0,
                "p95_ms": 0,
                "active_incidents": active_incidents,
            },
            "policy": {
                "critical_if": "error_rate>=0.30 OR p95_ms>=5000 OR incidents>=3",
                "degraded_if": "error_rate>=0.10 OR p95_ms>=2500 OR incidents>=1",
            },
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
    total = len(recent)
    up = sum(1 for x in recent if x.get("status") == "CONNECTED")
    err_rate = round((total - up) / total, 3)
    ms_series = sorted([x.get("ms", 0) for x in recent])
    avg_ms = int(sum(ms_series) / total)
    idx = min(total - 1, max(0, int(0.95 * (total - 1))))
    p95_ms = ms_series[idx]
    if err_rate >= 0.30 or p95_ms >= 5000 or active_incidents >= 3:
        mode = "critical"
    elif err_rate >= 0.10 or p95_ms >= 2500 or active_incidents >= 1:
        mode = "degraded"
    else:
        mode = "normal"
    return {
        "mode": mode,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "signals": {
            "window": "1h",
            "total_pings": total,
            "up_pings": up,
            "error_rate": err_rate,
            "avg_ms": avg_ms,
            "p95_ms": p95_ms,
            "active_incidents": active_incidents,
        },
        "policy": {
            "critical_if": "error_rate>=0.30 OR p95_ms>=5000 OR incidents>=3",
            "degraded_if": "error_rate>=0.10 OR p95_ms>=2500 OR incidents>=1",
        },
    }


@api.get("/runtime/state")
async def runtime_state(user: dict = Depends(get_current_user)):
    return await _compute_runtime_mode()


@api.post("/runtime/state/override")
async def runtime_override(payload: Dict[str, Any], user: dict = Depends(require_role("admin"))):
    mode = payload.get("mode")
    if mode not in ("normal", "degraded", "critical"):
        raise HTTPException(400, "invalid mode")
    doc = {
        "id": str(uuid.uuid4()),
        "mode": mode,
        "reason": payload.get("reason", "manual override"),
        "actor": user["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.runtime_overrides.insert_one(dict(doc))
    await write_evidence(user, "runtime.override", "runtime", doc["id"],
                          input_data={"mode": mode})
    return doc


# ------------------------------------------------------------------
# Learning Validation — proposals from feedback
# ------------------------------------------------------------------
class ProposalBody(BaseModel):
    subject: str
    old_doctrine: Optional[str] = None
    new_doctrine: str
    supporting_feedback_ids: List[str] = []
    expected_impact: Optional[str] = None
    affected_systems: List[str] = []


@api.post("/learning/proposals")
async def create_proposal(body: ProposalBody, user: dict = Depends(get_current_user)):
    threshold = int(os.environ.get("LEARNING_PROPOSAL_THRESHOLD", "3"))
    supporting = 0
    if body.supporting_feedback_ids:
        supporting = await db.feedback.count_documents({"id": {"$in": body.supporting_feedback_ids}})
    doc = {
        "id": str(uuid.uuid4()),
        "subject": body.subject,
        "old_doctrine": body.old_doctrine,
        "new_doctrine": body.new_doctrine,
        "supporting_feedback_ids": body.supporting_feedback_ids,
        "supporting_count": supporting,
        "threshold": threshold,
        "expected_impact": body.expected_impact,
        "affected_systems": body.affected_systems,
        "status": "pending" if supporting >= threshold else "draft",
        "author": {"id": user["id"], "email": user["email"], "role": user["role"]},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.learning_proposals.insert_one(dict(doc))
    await write_evidence(user, "learning.propose", "proposal", doc["id"],
                          input_data={"subject": body.subject},
                          output_data={"status": doc["status"], "supporting": supporting})
    doc.pop("_id", None)
    return doc


@api.get("/learning/proposals")
async def list_proposals(user: dict = Depends(get_current_user)):
    return await db.learning_proposals.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)


@api.post("/learning/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, user: dict = Depends(require_role("admin"))):
    p = await db.learning_proposals.find_one({"id": proposal_id})
    if not p:
        raise HTTPException(404, "Proposal not found")
    ts = datetime.now(timezone.utc).isoformat()
    await db.learning_proposals.update_one(
        {"id": proposal_id},
        {"$set": {"status": "approved", "approved_by": user["email"], "approved_at": ts}}
    )
    await db.doctrine_history.insert_one({
        "id": str(uuid.uuid4()),
        "proposal_id": proposal_id,
        "old_doctrine": p.get("old_doctrine"),
        "new_doctrine": p["new_doctrine"],
        "author": p.get("author"),
        "approved_by": user["email"],
        "approved_at": ts,
        "evidence": {"supporting": p.get("supporting_count"), "threshold": p.get("threshold")},
    })
    await write_evidence(user, "learning.approve", "proposal", proposal_id, approval="approve")
    return {"ok": True, "status": "approved"}


# ------------------------------------------------------------------
# Financial + Human loop maps
# ------------------------------------------------------------------
@api.get("/finance/loop")
async def finance_loop(user: dict = Depends(get_current_user)):
    snap = await db.finance_snapshot.find_one({}, {"_id": 0}) or {}
    ts = snap.get("updated_at")
    def _stage(name, value, source):
        return {
            "stage": name,
            "value": value,
            "source": source,
            "timestamp": ts,
            "confidence": 0.85 if value is not None else 0.0,
            "provenance": "finance_snapshot" if value is not None else None,
            "status": "OK" if value is not None else "DATA_NOT_AVAILABLE",
        }
    series = snap.get("cashflow_series", [])
    cashflow_value = sum(m["in"] - m["out"] for m in series) if series else None
    stages = [
        _stage("REVENUE", snap.get("revenue_ytd_eur"), "finance_snapshot.revenue_ytd_eur"),
        _stage("COST", None, "not tracked yet"),
        _stage("MARGIN", snap.get("gross_margin_pct"), "finance_snapshot.gross_margin_pct"),
        _stage("CASHFLOW", cashflow_value, "aggregate(cashflow_series)"),
        _stage("RESERVES", snap.get("cash_position_eur"), "finance_snapshot.cash_position_eur"),
        _stage("CAPITAL_ALLOCATION", None, "not tracked yet"),
        _stage("INVESTMENT", None, "not tracked yet"),
        _stage("RESULT", snap.get("ebitda_eur"), "finance_snapshot.ebitda_eur"),
        _stage("FEEDBACK", await db.feedback.count_documents({"module": "finance_os"}), "feedback[module=finance_os]"),
    ]
    bottleneck = next((s["stage"] for s in stages if s["status"] == "DATA_NOT_AVAILABLE"), None)
    return {"stages": stages, "bottleneck": bottleneck, "loop_health": "partial"}


@api.get("/people/loop")
async def people_loop(user: dict = Depends(get_current_user)):
    def _stage(name, count, source):
        return {
            "stage": name,
            "count": count,
            "source": source,
            "status": "OK" if count is not None else "DATA_NOT_AVAILABLE",
        }
    onboarding = await db.people.count_documents({"status": "onboarding"})
    active = await db.people.count_documents({"status": "active"})
    objectives = await db.objectives.count_documents({})
    stages = [
        _stage("ACADEMY", None, "cvl_academy adapter — not connected yet"),
        _stage("TRAINING", None, "not tracked yet"),
        _stage("CERTIFICATION", None, "cvl_academy issue_certification"),
        _stage("JURY", None, "not tracked yet"),
        _stage("TALENT", active + onboarding, "people(all)"),
        _stage("RECRUITMENT", onboarding, "people(status=onboarding)"),
        _stage("ONBOARDING", onboarding, "people(status=onboarding)"),
        _stage("WORK", active, "people(status=active)"),
        _stage("DEVELOPMENT", objectives, "objectives(count)"),
        _stage("LEADERSHIP", None, "not tracked yet"),
        _stage("SUCCESSION", None, "not tracked yet"),
    ]
    bottleneck = next((s["stage"] for s in stages if s["status"] == "DATA_NOT_AVAILABLE"), None)
    return {"stages": stages, "bottleneck": bottleneck, "loop_health": "partial"}


@api.post("/registry/repositories/{repo_id}/ping")
async def ping_repository(repo_id: str, user: dict = Depends(get_current_user)):
    result = await _ping_repo(repo_id, actor=user)
    return result


@api.get("/registry/repositories/{repo_id}/history")
async def repo_history(repo_id: str, user: dict = Depends(get_current_user)):
    docs = await db.ping_history.find(
        {"repo_id": repo_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(48).to_list(48)
    docs.reverse()
    return {"history": docs}


@api.get("/registry/fms-answers")
async def get_fms_answers(user: dict = Depends(get_current_user)):
    from registry_data import FMS_ANSWERS
    return FMS_ANSWERS


# --- internal ping helper (used by manual + cron) ------------------
async def _ping_repo(repo_id: str, actor: Optional[dict] = None) -> Dict[str, Any]:
    import asyncio
    import time
    import hashlib
    import requests as _rq

    repo = await db.repositories.find_one({"id": repo_id})
    if not repo:
        return {"status": "ERROR", "error": "not_found", "repo_id": repo_id}
    url = repo.get("preview_url") or repo.get("github_url")
    headers = {}
    if repo.get("auth_type") == "api_key" and repo.get("api_key"):
        headers["X-API-Key"] = repo["api_key"]
    elif repo.get("auth_type") == "bearer" and repo.get("api_key"):
        headers["Authorization"] = f"Bearer {repo['api_key']}"

    def _do():
        t0 = time.time()
        try:
            r = _rq.get(url, headers=headers, timeout=6, allow_redirects=True)
            return r.status_code, int((time.time() - t0) * 1000), None
        except Exception as e:
            return None, int((time.time() - t0) * 1000), str(e)[:200]

    http_code, ms, err = await asyncio.to_thread(_do)
    if err:
        status = "ERROR"
    elif http_code is not None and http_code < 500:
        status = "CONNECTED"
    else:
        status = "ERROR"

    ts = datetime.now(timezone.utc).isoformat()
    ping_doc = {
        "id": str(uuid.uuid4()),
        "repo_id": repo_id,
        "repo_key": repo.get("key"),
        "timestamp": ts,
        "status": status,
        "http": http_code,
        "ms": ms,
        "error": err,
        "url": url,
    }

    # Notarize (best-effort): FREKCORE remote if configured, else local Ed25519
    frekcore = await db.repositories.find_one({"id": "repo-frekcore"})
    if frekcore and frekcore.get("adapter_status") == "CONNECTED" and repo_id != "repo-frekcore":
        payload = f"{repo_id}|{ts}|{status}|{http_code}|{ms}".encode()
        digest = hashlib.sha256(payload).hexdigest()

        remote = await _notarize_via_frekcore(digest)
        if remote and remote.get("signature_b64") and remote.get("public_key_b64"):
            sig_b64 = remote["signature_b64"]
            pub_b64 = remote["public_key_b64"]
            did = remote.get("did", "did:frek:unknown")
            notary_name = "FREKCORE (remote)"
            notary_source = "frekcore"
            chain_ref = remote.get("chain_ref")
            anchored_at = remote.get("anchored_at")
        else:
            priv, pub_b64, did = await _get_or_create_notary_key()
            signature = priv.sign(digest.encode())
            sig_b64 = _b64.b64encode(signature).decode()
            notary_name = "FREKCORE-compatible (meta-cvln-local)"
            notary_source = "local"
            chain_ref = None
            anchored_at = None

        ping_doc["notarization"] = {
            "notary": notary_name,
            "notary_source": notary_source,
            "notary_did": did,
            "sha256": digest,
            "algorithm": "ed25519",
            "signature_b64": sig_b64,
            "public_key_b64": pub_b64,
            "notarized_at": ts,
            "chain_ref": chain_ref,
            "anchored_at": anchored_at,
        }
        await db.frek_notarizations.insert_one({
            "id": str(uuid.uuid4()),
            "trace_id": ping_doc["id"],
            "target_type": "registry.ping",
            "target_id": ping_doc["id"],
            "target_repo_key": repo.get("key"),
            "target_repo_name": repo.get("name"),
            "sha256": digest,
            "signature_b64": sig_b64,
            "public_key_b64": pub_b64,
            "notary_did": did,
            "notary_source": notary_source,
            "algorithm": "ed25519",
            "chain_ref": chain_ref,
            "anchored_at": anchored_at,
            "status": status,
            "http": http_code,
            "ms": ms,
            "created_at": ts,
        })

    await db.ping_history.insert_one(dict(ping_doc))

    upd = {
        "last_ping": ts,
        "last_ping_status": status,
        "last_ping_http": http_code,
        "last_ping_ms": ms,
        "last_ping_error": err,
        "adapter_status": status if status == "CONNECTED" else repo.get("adapter_status", "NOT_CONNECTED"),
    }
    await db.repositories.update_one({"id": repo_id}, {"$set": upd})
    if actor:
        await write_evidence(actor, "registry.ping", "repository", repo_id,
                              input_data={"url": url},
                              output_data={"status": status, "http": http_code, "ms": ms,
                                           "notarized": bool(ping_doc.get("notarization"))})
    ping_doc.pop("_id", None)
    return {"status": status, "http": http_code, "ms": ms, "url": url, "error": err,
            "notarization": ping_doc.get("notarization")}


# --- Cron endpoint (called hourly by .emergent/crons.yml) ---------
@app.post("/api/cron/registry-ping-all")
async def cron_ping_all(request: Request):
    # Cron endpoints must ack 2xx immediately; enqueue/background the actual work.
    import asyncio
    secret = os.environ.get("WEBHOOK_CRON_SECRET", "")
    auth = request.headers.get("Authorization", "")
    if not secret or not auth.startswith("Bearer ") or auth[7:] != secret:
        raise HTTPException(status_code=401, detail="Invalid webhook auth")

    repos = await db.repositories.find({}, {"id": 1, "_id": 0}).to_list(50)

    system_actor = {"id": "cron", "email": "cron@meta-cvln", "role": "system"}

    async def _bg():
        for r in repos:
            try:
                await _ping_repo(r["id"], actor=system_actor)
            except Exception as e:
                log.exception(f"cron ping failed for {r['id']}: {e}")

    asyncio.create_task(_bg())
    return {"ok": True, "scheduled": len(repos)}


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
# 5 versioned contracts — the API contract of the ecosystem
# ------------------------------------------------------------------
@api.get("/contracts")
async def get_contracts(user: dict = Depends(get_current_user)):
    return {"contracts": contracts_catalog(), "count": len(ALL_CONTRACTS)}


@api.get("/contracts/{key}")
async def get_contract(key: str, user: dict = Depends(get_current_user)):
    if key not in ALL_CONTRACTS:
        raise HTTPException(404, f"Unknown contract '{key}'")
    catalog = {c["key"]: c for c in contracts_catalog()}
    return catalog[key]


# ------------------------------------------------------------------
# Typed cross-repo adapters (P1) — one small function per capability
# ------------------------------------------------------------------
class TypedCall(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)


async def _call_repo(repo_key: str, path: str, method: str = "POST",
                      body: Optional[dict] = None) -> dict:
    """Generic typed call: fetch preview_url + auth from Registry, POST/GET."""
    import asyncio
    import requests as _rq
    import time
    repo = await db.repositories.find_one({"key": repo_key})
    if not repo or not repo.get("preview_url"):
        return {"status": "NO_ENDPOINT", "repo": repo_key,
                "hint": f"Configure preview_url for {repo_key} in Registry"}
    url = repo["preview_url"].rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if repo.get("auth_type") == "api_key" and repo.get("api_key"):
        headers["X-API-Key"] = repo["api_key"]
    elif repo.get("auth_type") == "bearer" and repo.get("api_key"):
        headers["Authorization"] = f"Bearer {repo['api_key']}"

    def _do():
        t0 = time.time()
        try:
            if method == "POST":
                r = _rq.post(url, headers=headers, json=body or {}, timeout=10)
            else:
                r = _rq.get(url, headers=headers, timeout=10)
            ms = int((time.time() - t0) * 1000)
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text[:400]}
            return {"http": r.status_code, "ms": ms, "data": data}
        except Exception as e:
            return {"http": None, "ms": int((time.time() - t0) * 1000),
                    "error": str(e)[:200]}

    return await asyncio.to_thread(_do)


@api.post("/adapters/labelos/push_catalogue")
async def labelos_push_catalogue(body: TypedCall, user: dict = Depends(get_current_user)):
    if user["role"] not in ("admin", "cfo", "ops_lead"):
        raise HTTPException(403, "cfo or ops_lead required")
    trace_id = str(uuid.uuid4())
    res = await _call_repo("fms_os", "/api/labelos/push_catalogue",
                            body={**body.inputs, "trace_id": trace_id,
                                   "issuer": "meta-cvln-os"})
    await write_evidence(user, "adapter.labelos.push_catalogue", "adapter", trace_id,
                          input_data=body.inputs, output_data=res)
    return {"trace_id": trace_id, "capability": "labelos.push_catalogue", **res}


@api.post("/adapters/wallet/transaction")
async def wallet_transaction(body: TypedCall, user: dict = Depends(get_current_user)):
    if user["role"] not in ("admin", "cfo"):
        raise HTTPException(403, "cfo required for wallet transactions")
    trace_id = str(uuid.uuid4())
    res = await _call_repo("cvln_wallet", "/api/wallet/transaction",
                            body={**body.inputs, "trace_id": trace_id,
                                   "issuer": "meta-cvln-os"})
    await write_evidence(user, "adapter.wallet.transaction", "adapter", trace_id,
                          input_data=body.inputs, output_data=res, approval="pending")
    return {"trace_id": trace_id, "capability": "wallet.transaction", **res}


@api.post("/adapters/laurentia/briefing")
async def laurentia_briefing(body: TypedCall, user: dict = Depends(get_current_user)):
    trace_id = str(uuid.uuid4())
    res = await _call_repo("laurentia", "/api/briefing",
                            body={**body.inputs, "trace_id": trace_id,
                                   "issuer": "meta-cvln-os"})
    await write_evidence(user, "adapter.laurentia.briefing", "adapter", trace_id,
                          input_data=body.inputs, output_data=res)
    return {"trace_id": trace_id, "capability": "laurentia.briefing", **res}


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

    # Idempotent registry seed for real CVLN source repos
    valid_ids = set()
    _refresh_keys = ("name", "github_url", "branch", "description",
                     "tech_stack", "capabilities", "layer", "role",
                     "adapters_declared", "entity_id", "resolved_questions",
                     "notes", "is_trust_anchor", "preview_url", "auth_type")
    for repo in repositories_docs():
        valid_ids.add(repo["id"])
        insert_only = {k: v for k, v in repo.items() if k not in _refresh_keys}
        set_now = {k: v for k, v in repo.items() if k in _refresh_keys}
        await db.repositories.update_one(
            {"id": repo["id"]},
            {"$setOnInsert": insert_only, "$set": set_now},
            upsert=True,
        )
    # Remove stale repos that are no longer in the registry list
    await db.repositories.delete_many({"id": {"$nin": list(valid_ids)}})


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
