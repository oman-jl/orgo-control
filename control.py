#!/usr/bin/env python3
"""
Nanocloud — unified control CLI for the Personal AI Cloud.

Usage:
    python3 control.py status
    python3 control.py provision --name agent-1 --cpu 1 --ram 4
    python3 control.py screenshot --computer <id> --out shot.png
    python3 control.py bash --computer <id> --cmd "ls -la"
    python3 control.py ssh-enable --computer <id>
    python3 control.py deploy-demo --computer <id>
    python3 control.py report

Config: reads ORGO_API_KEY from the environment. No secrets in code.
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap

from orgo_client import OrgoClient, OrgoError

DEMO_HTML = textwrap.dedent(
    """\
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Nanocloud Demo</title></head>
      <body style="font-family:sans-serif;background:#0f172a;color:#e2e8f0;
                   display:grid;place-items:center;height:100vh;margin:0">
        <div style="text-align:center">
          <h1>🐈 Nanocloud Demo</h1>
          <p>Deployed from the Nanocloud control system.</p>
          <p id="status">…</p>
        </div>
        <script>
          fetch('/api/health').then(r=>r.json()).then(d=>{
            document.getElementById('status').textContent =
              'API OK — ' + JSON.stringify(d);
          });
        </script>
      </body>
    </html>
    """
)

DEMO_APP = textwrap.dedent(
    """\
    import json, os
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/api/health'):
                body = json.dumps({"status": "ok", "app": "nanocloud-demo"}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            body = open('/demo/index.html','rb').read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    if __name__ == '__main__':
        HTTPServer(('0.0.0.0', 8000), H).serve_forever()
    """
)


def get_client() -> OrgoClient:
    return OrgoClient()


def cmd_status(c: OrgoClient, _args):
    ws = c.list_workspaces()
    print(json.dumps({"workspaces": ws}, indent=2))


def cmd_provision(c: OrgoClient, args):
    ws = c.list_workspaces()
    if not ws:
        print("No workspace found. Creating one...")
        created = c.create_workspace("personal-ai-cloud")
        ws = [created]
    workspace_id = ws[0]["id"]
    comp = c.create_computer(
        workspace_id=workspace_id,
        name=args.name,
        cpu=args.cpu,
        ram=args.ram,
        os_name=args.os,
        billing_mode="hourly",
    )
    print("Computer created:")
    print(json.dumps(comp, indent=2))
    print("\nWaiting for it to become ready...")
    final = c.wait_ready(comp.get("id"))
    print(json.dumps(final, indent=2))


def cmd_screenshot(c: OrgoClient, args):
    out = c.screenshot(args.computer, args.out)
    print(f"Screenshot saved to {out}")


def cmd_bash(c: OrgoClient, args):
    res = c.bash(args.computer, args.cmd)
    print(json.dumps(res, indent=2))


def cmd_ssh(c: OrgoClient, args):
    res = c.ssh_enable(args.computer)
    print(json.dumps(res, indent=2))


def cmd_deploy_demo(c: OrgoClient, args):
    """Deploy a tiny demo website + API onto an Orgo computer."""
    cid = args.computer
    print("Preparing demo files on the computer...")
    c.bash(cid, "mkdir -p /demo")
    c.upload_file(cid, "/dev/stdin", "/demo/index.html") if False else None
    # Write files via bash heredoc to avoid stdin issues.
    import tempfile, os
    for fname, content in (("index.html", DEMO_HTML), ("app.py", DEMO_APP)):
        tmp = tempfile.mktemp()
        with open(tmp, "w") as fh:
            fh.write(content)
        c.upload_file(cid, tmp, f"/demo/{fname}")
        os.unlink(tmp)
    print("Starting demo server on port 8000...")
    print(json.dumps(c.bash(cid, "nohup python3 /demo/app.py >/demo/server.log 2>&1 & echo started"), indent=2))
    print(json.dumps(c.bash(cid, "sleep 1 && curl -s http://localhost:8000/api/health"), indent=2))
    print("Public/persistent URL depends on your Orgo/network setup. To expose via a tunnel you can run cloudflared on the computer.")
    print("Demo files are at /demo on the computer.")


def cmd_report(c: OrgoClient, _args):
    ws = c.list_workspaces()
    computers = []
    for w in ws:
        for comp in c.list_computers(w["id"]):
            computers.append(comp)
    print(json.dumps({"workspaces": ws, "computers": computers}, indent=2))


def main():
    p = argparse.ArgumentParser(description="Nanocloud control CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sp = sub.add_parser("provision")
    sp.add_argument("--name", required=True)
    sp.add_argument("--cpu", type=int, default=1)
    sp.add_argument("--ram", type=int, default=4)
    sp.add_argument("--os", default="linux")
    sp.set_defaults(func=cmd_provision)

    sp = sub.add_parser("screenshot")
    sp.add_argument("--computer", required=True)
    sp.add_argument("--out", default="shot.png")
    sp.set_defaults(func=cmd_screenshot)

    sp = sub.add_parser("bash")
    sp.add_argument("--computer", required=True)
    sp.add_argument("--cmd", required=True)
    sp.set_defaults(func=cmd_bash)

    sp = sub.add_parser("ssh-enable")
    sp.add_argument("--computer", required=True)
    sp.set_defaults(func=cmd_ssh)

    sp = sub.add_parser("deploy-demo")
    sp.add_argument("--computer", required=True)
    sp.set_defaults(func=cmd_deploy_demo)

    sub.add_parser("report").set_defaults(func=cmd_report)

    args = p.parse_args()
    try:
        c = get_client()
    except OrgoError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    args.func(c, args)


if __name__ == "__main__":
    main()
