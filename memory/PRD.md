# META CVLN OS — PRD

## Doctrine
DATA → CONTEXT → PREPARATION → HUMAN DECISION → EXECUTION → VERIFICATION → FEEDBACK.
**Integrate before rebuild.** 3 couches séparées : PUBLIC / OS / COMMERCIAL.

## Boucle trust chain complète
REPO → PING → EVENT → SHA-256 → NOTARY (Ed25519, local ou FREKCORE remote) → DID → LEDGER → .FK EXPORT → EXTERNAL VERIFICATION → (bientôt) ANCHOR / FREK-CHAIN

## Format .FK (FREKANSLA FK Object v3)
Toute notarisation est exportable au format `.fk` conforme FREKANSLA :
`fk_version, schema=fk.object.v3, issuer, issued_at, event, provenance[observation→hash→signature], fingerprint(sha256), signature(ed25519), public_key, notary(did, source, chain_ref, anchored_at), verification.method`

## Modules livrés
- 3 couches externes : `/public` (vitrine dense — hero, vision fondateur, FREKCORE focus, 12 entités, partenaires, CTA), `/commercial` (4 offres), `/audit` (ledger public sans auth avec download .fk)
- OS interne : Command Center, Workbench, People/Finance/Legal/Ops/Knowledge, Registry (12 repos + sparkline + FMS answers), Agent Factory, Decision, Evidence, **Notary Ledger** (filtres repo+status+période), **Weekly Report**, CVL Brain

## Automation
- Cron horaire `.emergent/crons.yml` → `/api/cron/registry-ping-all`
- **Cron hebdomadaire Lundi 08:00 UTC** → `/api/cron/weekly-drop-report` — génère rapport 7j, flag <95%, insert alert dans Command Center
- Notarisation Ed25519 avec bridge FREKCORE : `NOTARY_MODE=frekcore` + `FREKCORE_NOTARIZE_URL` bascule instantanément vers `did:frek:*` (contract publié dans server.py `_notarize_via_frekcore`)

## FREKCORE Remote Notary — contrat côté FREKCORE
```
POST {FREKCORE_NOTARIZE_URL}
Authorization: Bearer {FREKCORE_API_KEY}
Body: {"sha256": "<hex>", "issuer": "meta-cvln-os"}
Response: {"signature_b64", "public_key_b64", "did": "did:frek:...",
           "algorithm": "ed25519", "anchored_at", "chain_ref"}
```
Meta CVLN persiste `notary_source: frekcore | local` + `chain_ref` + `anchored_at` sur chaque signature.

## Testé
- FK v3.0 export end-to-end (provenance chain vérifiable)
- Filtres ledger : `?repo_key=production_vault` → 3 résultats
- Weekly cron : 12 repos, 0 flagged, tous 100% uptime, report stocké dans db.reports
- Meta Public : hero, founder quote, .fk sample container, 12 entités, 6 partenaires, CTA

## P1 backlog
- Renseigner `FREKCORE_NOTARIZE_URL` quand endpoint publié (une seule ligne .env)
- Feedback signaler UI
- Adapters typés cross-repo (labelos.push_catalogue, wallet.transaction, laurentia.briefing)

## P2 backlog
- Streaming SSE natif CVL Brain
- OpenTelemetry trace_id cross-repo
- Adaptive Runtime NORMAL/DEGRADED/CRITICAL
- Multi-tenant strict par entity
