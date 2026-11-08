#!/usr/bin/env python3
"""
Nanocloud — Orgo AI API client.
Wraps the Orgo HTTP API (https://www.orgo.ai/api).

Official API reference: https://docs.orgo.ai/api-reference/introduction
Auth: Bearer token (ORGO_API_KEY).

This module contains NO secrets. Read the key from the environment.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional

import requests

BASE_URL = "https://www.orgo.ai/api"


class OrgoError(RuntimeError):
    pass


class OrgoClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.environ.get("ORGO_API_KEY")
        if not self.api_key:
            raise OrgoError(
                "ORGO_API_KEY is not set. Create one at https://www.orgo.ai/api-keys "
                "and export it: export ORGO_API_KEY=sk_live_..."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{BASE_URL}{path}"
        kwargs.setdefault("timeout", self.timeout)
        r = self.session.request(method, url, **kwargs)
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text[:300]
            raise OrgoError(f"{method} {path} -> {r.status_code}: {detail}")
        if r.status_code == 204:
            return {}
        return r.json()

    # ---- Workspaces ----
    def list_workspaces(self) -> list[dict]:
        return self._request("GET", "/workspaces").get("workspaces", [])

    def create_workspace(self, name: str) -> dict:
        return self._request("POST", "/workspaces", json={"name": name})

    # ---- Computers ----
    def list_computers(self, workspace_id: Optional[str] = None) -> list[dict]:
        # Computers are exposed as "desktops" under the workspace object.
        if workspace_id:
            ws = self._request("GET", f"/workspaces/{workspace_id}")
            return ws.get("desktops", [])
        out = []
        for ws in self.list_workspaces():
            out.extend(ws.get("desktops", []))
        return out

    def create_computer(
        self,
        workspace_id: str,
        name: str,
        cpu: int = 1,
        ram: int = 4,
        os_name: str = "linux",
        billing_mode: str = "hourly",
    ) -> dict:
        payload = {
            "workspace_id": workspace_id,
            "name": name,
            "os": os_name,
            "cpu": cpu,
            "ram": ram,
            "billing_mode": billing_mode,
        }
        return self._request("POST", "/computers", json=payload)

    def get_computer(self, computer_id: str) -> dict:
        return self._request("GET", f"/computers/{computer_id}")

    def start(self, computer_id: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/start")

    def stop(self, computer_id: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/stop")

    def restart(self, computer_id: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/restart")

    def delete(self, computer_id: str) -> dict:
        return self._request("DEL", f"/computers/{computer_id}")

    def resize(self, computer_id: str, cpu: int = None, ram: int = None) -> dict:
        payload = {}
        if cpu is not None:
            payload["cpu"] = cpu
        if ram is not None:
            payload["ram"] = ram
        return self._request("PATCH", f"/computers/{computer_id}/resize", json=payload)

    # ---- Control / screen ----
    def screenshot(self, computer_id: str, path: str) -> str:
        r = self.session.get(
            f"{BASE_URL}/computers/{computer_id}/screenshot", timeout=self.timeout
        )
        if r.status_code != 200:
            raise OrgoError(f"screenshot -> {r.status_code}")
        with open(path, "wb") as fh:
            fh.write(r.content)
        return path

    def bash(self, computer_id: str, command: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/bash", json={"command": command})

    def python(self, computer_id: str, code: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/exec", json={"code": code})

    def click(self, computer_id: str, x: int, y: int) -> dict:
        return self._request("POST", f"/computers/{computer_id}/click", json={"x": x, "y": y})

    def type_text(self, computer_id: str, text: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/type", json={"text": text})

    def key(self, computer_id: str, key: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/key", json={"key": key})

    def wait(self, computer_id: str, ms: int) -> dict:
        return self._request("POST", f"/computers/{computer_id}/wait", json={"ms": ms})

    # ---- Files ----
    def list_files(self, computer_id: str) -> list[dict]:
        return self._request("GET", f"/computers/{computer_id}/files").get("files", [])

    def upload_file(self, computer_id: str, local_path: str, remote_path: str) -> dict:
        with open(local_path, "rb") as fh:
            r = self.session.post(
                f"{BASE_URL}/computers/{computer_id}/files/upload",
                params={"path": remote_path},
                files={"file": fh},
                timeout=self.timeout,
            )
        if r.status_code >= 400:
            raise OrgoError(f"upload -> {r.status_code}: {r.text[:200]}")
        return r.json()

    def download_file(self, computer_id: str, remote_path: str, local_path: str) -> str:
        r = self.session.get(
            f"{BASE_URL}/computers/{computer_id}/files/download",
            params={"path": remote_path},
            timeout=self.timeout,
        )
        if r.status_code != 200:
            raise OrgoError(f"download -> {r.status_code}")
        with open(local_path, "wb") as fh:
            fh.write(r.content)
        return local_path

    # ---- SSH ----
    def ssh_enable(self, computer_id: str) -> dict:
        return self._request("POST", f"/computers/{computer_id}/ssh")

    def ssh_settings(self, computer_id: str) -> dict:
        return self._request("GET", f"/computers/{computer_id}/ssh")

    def vnc_password(self, computer_id: str) -> str:
        d = self._request("GET", f"/computers/{computer_id}/vnc-password")
        return d.get("password", "")

    # ---- Health / operator ----
    def health(self, computer_id: str) -> dict:
        return self._request("GET", f"/computers/{computer_id}/health")

    # ---- Wait for computer to be ready ----
    def wait_ready(self, computer_id: str, timeout_s: int = 180) -> dict:
        deadline = time.time() + timeout_s
        last = {}
        while time.time() < deadline:
            last = self.get_computer(computer_id)
            if last.get("status") in ("running", "ready", "active"):
                return last
            time.sleep(5)
        raise OrgoError(f"computer {computer_id} not ready within {timeout_s}s: {last}")
