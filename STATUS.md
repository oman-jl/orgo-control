# Nanocloud — Live Status

_Reference blueprint as of 2026-11-06. Live details (URLs, keys, passwords) are set by the owner at deploy time and are intentionally NOT in this repo._

## What's running
- **Orgo computer** (Ubuntu 24.04 LTS, 2 vCPU, 8GB RAM) — running
- **Demo app** (Python HTTP server) running on `localhost:8000`:
  - `GET /` → HTML page
  - `GET /api/health` → `{"status":"ok","hostname":"<host>"}`
- Control works via a full-access API key (bash, screenshot, files all verified).

## Verified results (from live API)
- Full-access key ✅ works
- Computer status ✅ running
- Bash control ✅ works
- Screenshot ✅ works (1920x1080)
- Demo deploy ✅ HTTP 200 + API health OK

## Files on the computer (`/demo`)
- `index.html` — landing page
- `app.py` — Python HTTP server (port 8000)
- `nginx.conf` — reverse-proxy with Basic Auth (port 8088) → desktop (6080) + demo (8000)
- `.htpasswd` — Basic Auth credentials (generated locally by the owner; never committed)
- `tunnel.log`, `tunnel.pid` — cloudflared quick-tunnel runtime

## Public tunnels (live — URLs change on restart)
Each tunnel: `cloudflared` (443) → `nginx` (local listener, Basic Auth) → upstream service.

- **Tunnel A — Orgo.ai dedicated:** fronts `https://www.orgo.ai`. Gateway: nginx (8089, Basic Auth) → www.orgo.ai. Orgo session cookies are domain-bound, so in-proxy login may not persist.
- **Tunnel B — computer UI (desktop + demo):** `/` → noVNC desktop (websockify 6080); `/demo/*` → demo (8000); `/orgo/*` → proxy of www.orgo.ai.
- **Tunnel C — nanobot web UI:** fronts local `127.0.0.1:8765` (nanobot-gateway). Protected only by the tunnel Basic Auth — treat as sensitive.

> NOTE: quick tunnels change URL on process restart — re-read from the tunnel log.

## Control code (in this repo)
- `orgo_client.py` — Orgo API client (no secrets; key read from env)
- `control.py` — CLI: status / provision / screenshot / bash / ssh-enable / deploy-demo / report
- `ARCHITECTURE.md` — design doc
- `demo/` — the demo app (app.py + index.html)

## Blockers / notes
- **Free plan limit:** only 1 computer allowed.
- **ZenDevz:** not usable from a container (no KVM/systemd). Requires a real machine; Bangladesh-only, early alpha.
- **Public exposure:** demo runs on the computer's localhost. Exposing it to the internet needs an explicit tunnel / public-URL feature — owner must approve before opening.

## Safe commands (from this workspace)
```bash
export ORGO_API_KEY=sk_live_...   # full-access key (owner supplied)
python3 control.py status
python3 control.py screenshot --computer <computer-id> --out shot.png
python3 control.py bash --computer <computer-id> --cmd "curl -s http://localhost:8000/api/health"
python3 control.py report
```
