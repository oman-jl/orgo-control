# Nanocloud — Personal AI Cloud Architecture

**Status:** Planning/build — live provisioning blocked on credentials (see blockers).

## Purpose
One integrated, manageable Personal AI Cloud split across two platforms:

- **Orgo AI** — the *AI agent computer* (desktop, browser, terminal, agent runtime).
- **ZenDevz Cloud** — general-purpose VMs (app/db/API hosting), *when* a KVM host is available.

## Diagram

```
        ┌─────────────────────────────────────────────────────────┐
        │   YOUR PHONE (management surface)                        │
        │   browser → Nanocloud control CLI / dashboard            │
        └───────────────┬─────────────────────────┬───────────────┘
                        │ ORGO_API_KEY            │ zctl / console
                        ▼                         ▼
        ┌───────────────────────────┐  ┌───────────────────────────┐
        │  ORGO AI (managed cloud)  │  │  ZENDEVZ (your hardware)  │
        │  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │
        │  │ Workspace           │  │  │  │ Install zctl agent  │  │
        │  │   └─ Computer (VM)  │  │  │  │ (KVM + systemd)    │  │
        │  │       • Desktop      │  │  │  │  └─ VM (krab.*)    │  │
        │  │       • Browser      │  │  │  │       root SSH      │  │
        │  │       • Terminal     │  │  │  │       subdomain     │  │
        │  │       • Agent        │  │  │  └─────────────────────┘  │
        │  └─────────────────────┘  │  └───────────────────────────┘
        └───────────────────────────┘
        Control: raw HTTP API (Bearer)     Control: zctl CLI / console
        Endpoints: /api/computers/...      This host: NOT usable (no KVM/systemd)
```

## Per-platform findings (verified from official docs)

### Orgo AI — verified
- Base URL `https://www.orgo.ai/api`, auth `Authorization: Bearer $ORGO_API_KEY`.
- Free account: `$5` starting credit; free signup + API-key creation; one Medium
  Linux computer runs by the hour on that credit. Paid plans needed for more/size.
- API covers: workspaces, computers (create/get/update/resize/delete/start/stop/
  restart), screenshot, mouse/keyboard, bash/python exec, files upload/download,
  SSH enable + settings, VNC password, health, templates, workflows.
- CLI / MCP SDKs exist (docs.orgo.ai).

### ZenDevz — verified
- Model: *bring-your-own-hardware*. `zctl` installs on YOUR Linux/macOS machine
  (requires **KVM** + **systemd**). Your VMs run on your own box or the shared pool.
- Free (no card): VM create/run, root SSH, one subdomain/VM. One shared VM
  contributed back per private VM. Bangladesh-only, early alpha — NOT production-ready.
- This container **cannot** host the agent: no usable `/dev/kvm`, no systemd
  (PID 1 is init.sh). So ZenDevz compute is **blocked here** — it needs your real machine.

## Control surface (in this repo)
- `orgo_client.py` — clean Orgo API wrapper (no secrets).
- `control.py` — unified CLI: status / provision / screenshot / bash / ssh-enable /
  deploy-demo / report.
- `requirements.txt` — `requests` (only).

## Security notes
- No secrets in code. All keys come from env or CLI.
- Never publish API keys. Least-privilege API key scopes.
- No public port exposure on the local container. SSH only via platform-native, restricted routes.

## Blockers / required approvals
1. **NEEDS YOUR ACTION:** Orgo API key (`https://www.orgo.ai/api-keys`) → `export ORGO_API_KEY=sk_live_...`
2. **BLOCKED (host):** ZenDevz agent cannot run in this container (no KVM/systemd).
   Needs your real KVM machine (or explicit approval to provision a paid KVM VPS).
3. **NEEDS YOUR APPROVAL:** anything paid (Orgo paid plan, or a VPS).
