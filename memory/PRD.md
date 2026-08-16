# META CVLN OS — PRD

## Doctrine
DATA → CONTEXT → PREPARATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK
**Integrate before rebuild. Doctrine of layers: PUBLIC / OS / COMMERCIAL — jamais mélangés.**

## Boucle trust chain (livrée)
REPO → PING → EVENT → SHA-256 → NOTARY (Ed25519 local Meta CVLN) → DID → LEDGER → .FREK.JSON EXPORT → EXTERNAL VERIFICATION
Prochaine étape: bridge FREKCORE remote (P1) → ANCHOR / FREK-CHAIN

## 3 couches META CVLN (séparation stricte)
- **Meta CVLN Public** (`/public`) — vitrine publique dark violet, hero "One ecosystem. Many intelligences.", grille des 12 entités connected+notarized, liens vers /audit et /commercial. Aucune donnée interne.
- **Meta CVLN OS** (`/` post-login) — l'OS interne : Command Center, Workbench, People/Finance/Legal/Ops/Knowledge, Registry, Agent Factory, Decision, Evidence, Notary Ledger, CVL Brain
- **Meta CVLN Commercial** (`/commercial`) — offres Starter/Pro/Enterprise/On-Premise, gold accent
- **Meta CVLN Audit** (`/audit`) — trust chain publique read-only, 31 notarisations signées Ed25519, export `.frek.json` client-side sans auth

## Registry (12 repos CONNECTED)
frekcore, frekansla, cvln_agent_factory, laurentia, cvl_academy, kiltikonet, gala_cook_food, fms_os (labelos:fms), cvln_wallet, cvln_command_center, factory_ops, production_vault — tous ping automatique horaire.

## Notary
- Keypair Ed25519 stocké dans `db.system_keys`, DID `did:meta-cvln:413ba83ba91ff0ac`
- **P0 Signature Export livré** — `GET /api/notarizations/{id}/export` renvoie un artefact `.frek.json` conforme FREK v0.4 : event + fingerprint(sha256) + signature(ed25519) + public_key + notary(did/algorithm) + metadata + verification hint
- **P2 Auditor Public View livré** — `GET /api/public/notarizations` (sans auth) + page `/audit` avec download par ligne

## Testé
Ledger 31 signatures, export `.frek.json` conforme, public route accessible sans token, verify renvoie VALID, cron 12/12 CONNECTED.

## P1 backlog restant
- Bridge FREKCORE Remote Notary (contrat à publier) → did:frek:*
- Ledger Filter par repo + période
- Weekly Drop Report (email lundi 9h)
- Adapters typés cross-repo (labelos.push_catalogue, wallet.transaction, laurentia.briefing)
