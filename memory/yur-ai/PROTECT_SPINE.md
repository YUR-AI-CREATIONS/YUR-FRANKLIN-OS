# Frozen Spine Protection

- Do **not** edit `spine/neo3/*` or `trinity.py`. They are governance-critical.
- Edits to those paths must be reviewed by the designated owner (see `.github/CODEOWNERS`).
- Keep `TRINITY_GOVERNANCE_SIGNING_SECRET` set on the backend so audit/replay/anchor logs stay signed.
- Use append-only storage for `governance_enforcement.log`, `governance_replay_guard.log`, `governance_agent_anchors.log`, `governance_recovery_tokens.log`.
- If safe mode triggers, stop traffic, verify the audit chain, and recover with a single-use recovery token per the governance module instructions.

Operational reminders
- Backend: `https://yur-ai-api.onrender.com`
- Frontend env: set `VITE_TRINITY_API_URL` to the backend URL; rebuild/redeploy.
- CORS: allow your frontend origin (and localhost for dev) on the backend.
- Supabase: seed the provided JSONs so UI data calls (`/connectors`, `/academy/modules`, `/ledger/*`) return data.

If in doubt: do not change the spine—pause and escalate.
