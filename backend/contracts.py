"""META CVLN OS — 5 versioned contracts.

Every cross-entity call, every routing decision, every emitted event MUST
conform to one of these contracts. Contracts are versioned. Old versions
stay readable so upstream repos can migrate at their own pace.
"""
from typing import Optional, List, Any, Dict, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# ------------------------------------------------------------------
# 1) EVENT — the atomic unit of what happened
# ------------------------------------------------------------------
class Event(BaseModel):
    contract: Literal["event"] = "event"
    version: Literal["1.0"] = "1.0"
    id: str
    trace_id: str
    type: str = Field(..., description="dot.namespaced, e.g. registry.ping, decision.approve")
    source_system: str = Field(..., description="entity_id or repo_key")
    subject_type: Optional[str] = None
    subject_id: Optional[str] = None
    actor: Optional[Dict[str, Any]] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(3, ge=1, le=5)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    signed: bool = False
    signature_b64: Optional[str] = None
    public_key_b64: Optional[str] = None
    timestamp: str


# ------------------------------------------------------------------
# 2) CAPABILITY — what a system can do
# ------------------------------------------------------------------
class Capability(BaseModel):
    contract: Literal["capability"] = "capability"
    version: Literal["1.0"] = "1.0"
    id: str
    name: str
    entity_id: str = Field(..., description="Owning entity, e.g. labelos:fms")
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    allowed_actors: List[str] = Field(default_factory=list, description="roles or agent codes")
    prohibited_actors: List[str] = Field(default_factory=list)
    requires_approval_by: Optional[str] = None
    escalation_to: Optional[str] = None
    p95_latency_ms: Optional[int] = None
    cost_eur: Optional[float] = None
    idempotent: bool = True
    rollback_supported: bool = False
    health: Literal["green", "amber", "red"] = "green"


# ------------------------------------------------------------------
# 3) ROUTING_DECISION — where a request is dispatched
# ------------------------------------------------------------------
class RoutingDecision(BaseModel):
    contract: Literal["routing_decision"] = "routing_decision"
    version: Literal["1.0"] = "1.0"
    id: str
    trace_id: str
    event_id: str
    strategy: Literal["direct", "parallel", "fallback", "degraded"] = "direct"
    selected_capability_id: str
    selected_entity_id: str
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    reason: str
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    decided_at: str


# ------------------------------------------------------------------
# 4) SYSTEM_STATE — the current health of a system
# ------------------------------------------------------------------
class SystemState(BaseModel):
    contract: Literal["system_state"] = "system_state"
    version: Literal["1.0"] = "1.0"
    entity_id: str
    mode: Literal["normal", "degraded", "critical", "offline"] = "normal"
    health: Literal["green", "amber", "red"] = "green"
    uptime_pct_7d: Optional[float] = None
    p95_latency_ms: Optional[int] = None
    error_rate: Optional[float] = None
    active_incidents: int = 0
    last_notarized_at: Optional[str] = None
    last_notarization_did: Optional[str] = None
    observed_at: str


# ------------------------------------------------------------------
# 5) EXECUTION_PLAN — the DAG of what will happen
# ------------------------------------------------------------------
class ExecutionStep(BaseModel):
    step_id: str
    capability_id: str
    entity_id: str
    depends_on: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    requires_human_approval: bool = False
    approver: Optional[str] = None
    rollback_capability_id: Optional[str] = None


class ExecutionPlan(BaseModel):
    contract: Literal["execution_plan"] = "execution_plan"
    version: Literal["1.0"] = "1.0"
    id: str
    trace_id: str
    triggered_by_event_id: str
    steps: List[ExecutionStep]
    strategy: Literal["sequential", "parallel", "conditional"] = "sequential"
    max_duration_s: int = 300
    requires_human_gate: bool = False
    gate_owner_email: Optional[str] = None
    created_at: str


ALL_CONTRACTS = {
    "event": Event,
    "capability": Capability,
    "routing_decision": RoutingDecision,
    "system_state": SystemState,
    "execution_plan": ExecutionPlan,
}


def contracts_catalog():
    """Return JSON-schema catalog for every contract."""
    out = []
    for key, model in ALL_CONTRACTS.items():
        schema = model.model_json_schema()
        out.append({
            "key": key,
            "name": model.__name__,
            "version": schema.get("properties", {}).get("version", {}).get("default", "1.0"),
            "description": model.__doc__ or "",
            "schema": schema,
            "example": _example(key),
        })
    return out


def _example(key: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    if key == "event":
        return {
            "contract": "event", "version": "1.0",
            "id": "evt-...", "trace_id": "trc-...",
            "type": "registry.ping", "source_system": "meta-cvln-os",
            "payload": {"http": 200, "ms": 262}, "priority": 3, "confidence": 1.0,
            "signed": True, "timestamp": now,
        }
    if key == "capability":
        return {
            "contract": "capability", "version": "1.0",
            "id": "cap-labelos-push", "name": "labelos.push_catalogue",
            "entity_id": "labelos:fms",
            "input_schema": {"type": "object", "required": ["items"]},
            "output_schema": {"type": "object", "required": ["accepted", "notarization_id"]},
            "allowed_actors": ["ops_lead", "admin"], "requires_approval_by": "cfo",
            "p95_latency_ms": 220, "idempotent": True, "rollback_supported": True,
            "health": "green",
        }
    if key == "routing_decision":
        return {
            "contract": "routing_decision", "version": "1.0",
            "id": "rd-...", "trace_id": "trc-...", "event_id": "evt-...",
            "strategy": "direct", "selected_capability_id": "cap-laurentia-briefing",
            "selected_entity_id": "laurentia", "candidates": [],
            "reason": "capability match + lowest p95", "confidence": 0.94,
            "decided_at": now,
        }
    if key == "system_state":
        return {
            "contract": "system_state", "version": "1.0",
            "entity_id": "labelos:fms", "mode": "normal", "health": "green",
            "uptime_pct_7d": 100.0, "p95_latency_ms": 417, "error_rate": 0.0,
            "active_incidents": 0, "observed_at": now,
        }
    if key == "execution_plan":
        return {
            "contract": "execution_plan", "version": "1.0",
            "id": "plan-...", "trace_id": "trc-...", "triggered_by_event_id": "evt-...",
            "steps": [
                {"step_id": "s1", "capability_id": "cap-laurentia-briefing", "entity_id": "laurentia",
                 "depends_on": [], "inputs": {"topic": "Q1 review"},
                 "requires_human_approval": False},
                {"step_id": "s2", "capability_id": "cap-labelos-push", "entity_id": "labelos:fms",
                 "depends_on": ["s1"], "inputs": {"items": []},
                 "requires_human_approval": True, "approver": "cfo",
                 "rollback_capability_id": "cap-labelos-rollback"},
            ],
            "strategy": "sequential", "max_duration_s": 300,
            "requires_human_gate": True, "gate_owner_email": "cfo@cvln.local",
            "created_at": now,
        }
    return {}
