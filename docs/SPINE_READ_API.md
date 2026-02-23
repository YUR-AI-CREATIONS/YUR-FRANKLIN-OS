# Spine Read API (Shared Spine with Read Tokens)

These endpoints expose a read-only view of the Spine for external consumers without sharing your main credentials. Writes/anchors remain protected elsewhere.

## Env Vars (manage via Doppler/Render)
- `SPINE_URL` — external spine base URL (Render)
- `SPINE_ROOT_HASH` — optional root hash/anchor
- `SPINE_READ_TOKENS` — comma-separated read tokens issued per tenant/user

## Endpoints
- `GET /api/lithium/spine/status`  
  Headers: `Authorization: Bearer <read_token>` or `x-spine-read-token: <read_token>`  
  Returns spine URL and root hash (read-only).

- `GET /api/lithium/spine/ledger/{ref}`  
  Headers: same as above  
  Returns a pointer with `ref`, `url`, and `root_hash`. Ledger content is hosted on the external spine.

## Notes
- If `SPINE_READ_TOKENS` is empty, the read token check is skipped (not recommended for production).
- Keep write/anchor operations behind your internal protected endpoints; these routes are read-only pointers.***
