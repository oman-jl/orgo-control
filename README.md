# Orgo Control

Python control stack for the [Orgo.ai](https://www.orgo.ai) Cloud PC platform — provision computers, run bash, take screenshots, enable SSH, and deploy a demo app.

## Files
- `orgo_client.py` — clean Orgo API client (Bearer token from env, **no secrets in code**).
- `control.py` — CLI: `status` / `provision` / `screenshot` / `bash` / `ssh-enable` / `deploy-demo` / `report`.
- `demo/` — a minimal demo app (`app.py` Python HTTP server on port 8000 + `index.html` landing page).
- `ARCHITECTURE.md` — design doc for how the whole stack fits together.
- `STATUS.md` — reference live-status blueprint (creds anonymized).

## Setup
```bash
export ORGO_API_KEY=sk_live_...   # owner-supplied, full access
python3 -m venv .venv && . .venv/bin/activate
pip install requests
```

## Usage
```bash
python3 control.py status
python3 control.py screenshot --computer <computer-id> --out shot.png
python3 control.py bash --computer <computer-id> --cmd "hostname"
python3 control.py ssh-enable --computer <computer-id>
python3 control.py deploy-demo --computer <computer-id>
python3 control.py report
```

> Keys, computer IDs and tunnel URLs are environment/owner-supplied — never hardcoded.
