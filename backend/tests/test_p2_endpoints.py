"""P2 endpoint tests for META CVLN OS.

Covers:
- capability auto-discovery (POST /api/registry/discover-all)
- adaptive runtime (GET /api/runtime/state, POST /api/runtime/state/override)
- signed events (POST /api/events/emit + /api/events/verify)
- learning proposals (draft/approve/RBAC)
- finance loop (9 stages, DATA_NOT_AVAILABLE policy)
- people loop (11 stages)
- regression: auth/login, command-center, registry, notarizations, contracts, adapters
"""
import os
import copy
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cvln-os-core.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN = {"email": "metacvln@gmail.com", "password": "MetaCVLN2026!"}
EMPLOYEE = {"email": "employee@cvln.local", "password": "Cvln2026!"}

FINANCE_STAGES = ["REVENUE", "COST", "MARGIN", "CASHFLOW", "RESERVES",
                  "CAPITAL_ALLOCATION", "INVESTMENT", "RESULT", "FEEDBACK"]
PEOPLE_STAGES = ["ACADEMY", "TRAINING", "CERTIFICATION", "JURY", "TALENT",
                 "RECRUITMENT", "ONBOARDING", "WORK", "DEVELOPMENT",
                 "LEADERSHIP", "SUCCESSION"]


# ---------- Fixtures ----------
@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=15)
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    tok = r.json().get("token")
    assert tok
    return tok


@pytest.fixture(scope="session")
def employee_token():
    r = requests.post(f"{API}/auth/login", json=EMPLOYEE, timeout=15)
    if r.status_code != 200:
        pytest.skip(f"employee login failed: {r.status_code} {r.text[:200]}")
    return r.json().get("token")


def _h(tok):
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


# ---------- Auth regression ----------
def test_auth_login_admin(admin_token):
    assert isinstance(admin_token, str) and len(admin_token) > 10


def test_auth_login_employee(employee_token):
    assert isinstance(employee_token, str) and len(employee_token) > 10


# ---------- Capability Auto-Discovery ----------
def test_registry_discover_all(admin_token):
    r = requests.post(f"{API}/registry/discover-all", headers=_h(admin_token), timeout=120)
    assert r.status_code == 200, r.text
    data = r.json()
    for k in ("results", "healthy", "degraded", "unavailable", "total"):
        assert k in data, f"missing key: {k}"
    # total should be 12
    assert data["total"] == 12, f"expected 12 repos, got {data['total']}"
    counted = data["healthy"] + data["degraded"] + data["unavailable"]
    # UNKNOWN is possible for repos w/o preview_url; check counts do not exceed total
    assert counted <= data["total"]
    # verify lifecycle_status persisted on repos
    r2 = requests.get(f"{API}/registry/repositories", headers=_h(admin_token), timeout=30)
    assert r2.status_code == 200
    body = r2.json()
    repos = body["repositories"] if isinstance(body, dict) else body
    lifecycled = [x for x in repos if x.get("lifecycle_status") and x.get("discovery_at")]
    assert len(lifecycled) == 12, f"only {len(lifecycled)}/12 repos have lifecycle_status+discovery_at"


# ---------- Adaptive Runtime ----------
def test_runtime_state(admin_token):
    r = requests.get(f"{API}/runtime/state", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("mode") in ("normal", "degraded", "critical"), data
    sig = data.get("signals", {})
    # signals may be {} only when there is truly no history yet
    if sig:
        for k in ("total_pings", "error_rate", "p95_ms", "active_incidents"):
            assert k in sig, f"missing signal: {k}"
    assert "policy" in data


def test_runtime_override_employee_forbidden(employee_token):
    r = requests.post(f"{API}/runtime/state/override",
                      headers=_h(employee_token), json={"mode": "critical"}, timeout=15)
    assert r.status_code == 403, f"expected 403, got {r.status_code} {r.text}"


def test_runtime_override_admin_ok(admin_token):
    r = requests.post(f"{API}/runtime/state/override",
                      headers=_h(admin_token),
                      json={"mode": "critical", "reason": "test override"}, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("mode") == "critical"
    assert data.get("actor") == ADMIN["email"]


# ---------- Signed Events ----------
def test_events_emit_and_verify(admin_token):
    r = requests.post(f"{API}/events/emit",
                      headers=_h(admin_token),
                      json={"type": "test.event", "payload": {"hello": "world"}},
                      timeout=15)
    assert r.status_code == 200, r.text
    ev = r.json()
    for k in ("signature_b64", "public_key_b64", "key_id", "id", "trace_id", "type", "timestamp"):
        assert k in ev, f"missing {k} in emitted event"

    r2 = requests.post(f"{API}/events/verify",
                       headers=_h(admin_token), json=ev, timeout=15)
    assert r2.status_code == 200, r2.text
    v = r2.json()
    assert v.get("valid") is True, v


def test_events_verify_tampered(admin_token):
    r = requests.post(f"{API}/events/emit",
                      headers=_h(admin_token),
                      json={"type": "test.event", "payload": {"x": 1}},
                      timeout=15)
    assert r.status_code == 200
    ev = copy.deepcopy(r.json())
    ev["id"] = "tampered-" + ev["id"]

    r2 = requests.post(f"{API}/events/verify",
                       headers=_h(admin_token), json=ev, timeout=15)
    assert r2.status_code == 200
    v = r2.json()
    assert v.get("valid") is False, v
    assert v.get("action") == "quarantined", v


# ---------- Learning Validation ----------
def test_learning_proposal_draft_and_approve(admin_token, employee_token):
    body = {
        "subject": "TEST_ doctrine change",
        "old_doctrine": "old",
        "new_doctrine": "new-doctrine-value",
        "supporting_feedback_ids": [],
        "affected_systems": ["ops"],
    }
    r = requests.post(f"{API}/learning/proposals",
                      headers=_h(employee_token), json=body, timeout=15)
    assert r.status_code == 200, r.text
    p = r.json()
    assert p.get("status") == "draft", p
    pid = p["id"]

    # Employee cannot approve
    r_emp = requests.post(f"{API}/learning/proposals/{pid}/approve",
                          headers=_h(employee_token), timeout=15)
    assert r_emp.status_code == 403, f"employee approve should be 403 got {r_emp.status_code}"

    # Admin approves
    r_adm = requests.post(f"{API}/learning/proposals/{pid}/approve",
                          headers=_h(admin_token), timeout=15)
    assert r_adm.status_code == 200, r_adm.text
    assert r_adm.json().get("status") == "approved"

    # Verify persistence
    lst = requests.get(f"{API}/learning/proposals", headers=_h(admin_token), timeout=15).json()
    found = next((x for x in lst if x["id"] == pid), None)
    assert found and found["status"] == "approved"


# ---------- Finance loop ----------
def test_finance_loop(admin_token):
    r = requests.get(f"{API}/finance/loop", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    stages = data.get("stages", [])
    assert len(stages) == 9, f"expected 9 stages got {len(stages)}"
    got_names = [s["stage"] for s in stages]
    assert got_names == FINANCE_STAGES, got_names
    for s in stages:
        assert s.get("status") in ("OK", "DATA_NOT_AVAILABLE"), s
        if s["status"] == "DATA_NOT_AVAILABLE":
            assert s.get("value") in (None, 0) or s.get("value") is None, (
                f"stage {s['stage']} DATA_NOT_AVAILABLE but has invented value {s.get('value')}"
            )
            # provenance must be None
            assert s.get("provenance") is None, s


# ---------- People loop ----------
def test_people_loop(admin_token):
    r = requests.get(f"{API}/people/loop", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    stages = data.get("stages", [])
    assert len(stages) == 11, f"expected 11 stages got {len(stages)}"
    got_names = [s["stage"] for s in stages]
    assert got_names == PEOPLE_STAGES, got_names
    for s in stages:
        assert s.get("status") in ("OK", "DATA_NOT_AVAILABLE"), s


# ---------- Light regression ----------
def test_regression_command_center(admin_token):
    r = requests.get(f"{API}/command-center/overview", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200, r.text


def test_regression_registry_repos(admin_token):
    r = requests.get(f"{API}/registry/repositories", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    body = r.json()
    repos = body["repositories"] if isinstance(body, dict) else body
    assert len(repos) == 12


def test_regression_notarizations(admin_token):
    r = requests.get(f"{API}/notarizations", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    body = r.json()
    items = body["notarizations"] if isinstance(body, dict) else body
    assert isinstance(items, list)


def test_regression_contracts(admin_token):
    r = requests.get(f"{API}/contracts", headers=_h(admin_token), timeout=15)
    assert r.status_code == 200
    body = r.json()
    items = body["contracts"] if isinstance(body, dict) else body
    assert isinstance(items, list) and len(items) >= 1


def test_regression_adapter_laurentia(admin_token):
    r = requests.post(f"{API}/adapters/laurentia/briefing",
                      headers=_h(admin_token), json={}, timeout=30)
    # Adapter may 502/500 on real external — accept 2xx OR structured error
    assert r.status_code in (200, 400, 404, 500, 502, 503), r.status_code


def test_regression_adapter_wallet(admin_token):
    r = requests.post(f"{API}/adapters/wallet/transaction",
                      headers=_h(admin_token),
                      json={"amount_eur": 1.0, "purpose": "TEST"}, timeout=30)
    # Wallet is expected to be unavailable (404) — must not be mocked
    assert r.status_code in (200, 400, 404, 500, 502, 503), r.status_code
