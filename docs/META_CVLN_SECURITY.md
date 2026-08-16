# META CVLN OS — Security Snapshot (P2)

## Data at rest
- MongoDB: `db.system_keys` contient la clé privée Ed25519 du notary (base64) — **NOT ENCRYPTED at rest (dev)**
- `db.users.password_hash` — **bcrypt** ✓
- `db.repositories.api_key` — plaintext dans le doc, **jamais retourné à l'API** (`{"api_key": 0}` projection)
- `db.feedback`, `db.decisions`, `db.evidence` — plaintext

## Data in transit
- Toutes les routes `/api/*` derrière l'ingress HTTPS (Emergent)
- Cookies `SameSite=none; Secure`
- Bearer JWT signé HS256, secret via `.env`

## Authentication
- JWT Bearer (`JWT_SECRET`) via `Authorization` header
- HttpOnly cookie fallback (`SameSite=none; Secure`)
- Password: bcrypt

## Authorization
- RBAC via `require_role("admin")` — utilisé pour override runtime, learning approve
- `authority_scope` par utilisateur (module ownership)
- Adapters: RBAC explicit (wallet.transaction → cfo/admin only; labelos.push_catalogue → ops_lead+)

## Signing
- Notary Ed25519 keypair persisté dans `db.system_keys`
- Ping notarizations + signed_events tous signés
- Vérification exposée via `/api/notarizations/{id}/verify` et `/api/events/verify`

## Gaps (explicit)
| Item | Status |
|---|---|
| Encryption at rest MongoDB | MISSING |
| Notary private key encryption | MISSING (base64 en clair dans db.system_keys) |
| Repository API keys encryption | MISSING (plaintext) |
| Secrets management (Vault) | MISSING |
| Key rotation | MISSING |
| Multi-tenant strict par entity | PARTIAL (RBAC ✓, tenant_id doc-level ✗) |
| Anomaly detection | MISSING |
| Incident response runbook | MISSING |
| Separation of duties | PARTIAL |

## Priorité immédiate
1. Chiffrer `db.system_keys.private_b64` avec une clé dérivée d'un secret ENV (Fernet)
2. Chiffrer `db.repositories.api_key` de la même façon
3. Passer les JWTs à RS256 avec une clé privée signature (au lieu de HS256)
