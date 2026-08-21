#!/usr/bin/env python3
"""
Publish luxun-skill to GitHub. Idempotent: verify token -> create repo -> push.

Usage:
  python tools/publish.py                      # token from $GH_TOKEN or ~/.git-credentials
  python tools/publish.py --token ghp_xxx      # explicit classic PAT
  python tools/publish.py --dry-run            # verify token + repo state, do not push

The GitHub REST calls use TLS 1.2 + certifi (portable in sandboxed Windows shells
whose schannel certificate store is unavailable). The push uses `git` with the
OpenSSL TLS backend and the same CA file.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import certifi

API = "https://api.github.com"
DEFAULT_REPO = "luxun-skill"


def resolve_token(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if env:
        return env
    cred = Path.home() / ".git-credentials"
    if cred.exists():
        for line in cred.read_text(encoding="utf-8", errors="replace").splitlines():
            if "github.com" not in line:
                continue
            after = line.strip().split("//", 1)[1]
            return after.split("@", 1)[0].split(":", 1)[1]
    raise SystemExit("no token found: pass --token, set GH_TOKEN, or add ~/.git-credentials")


def http_json(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=certifi.where())
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "luxun-skill-publish",
            "Content-Type": "application/json" if body is not None else "text/plain",
        },
    )
    try:
        with urllib.request.urlopen(req, context=context, timeout=30) as r:
            payload = json.load(r) if r.status != 204 else {}
            return r.status, payload
    except urllib.error.HTTPError as e:
        try:
            payload = json.load(e)
        except Exception:
            payload = {}
        return e.code, payload


def ca_path() -> str:
    return certifi.where()


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    cmd = ["git", "-c", "http.sslBackend=openssl", "-c", f"http.sslCAInfo={ca_path()}", *args]
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish luxun-skill to GitHub")
    parser.add_argument("--token", help="GitHub PAT (classic: repo scope, or fine-grained: Contents R/W)")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Repository name")
    parser.add_argument("--public", action="store_true", help="Create public repo (default)")
    parser.add_argument("--private", action="store_true", help="Create private repo")
    parser.add_argument("--dry-run", action="store_true", help="Verify token + repo state without pushing")
    parser.add_argument("--push-only", action="store_true",
                        help="Skip REST API entirely: user creates the empty repo on github.com first, "
                             "then this script only sets origin and pushes (robust in TLS-restricted environments)")
    args = parser.parse_args()

    token = resolve_token(args.token)
    repo_dir = Path(__file__).resolve().parent.parent

    if args.push_only:
        # Robust path: user created the empty repo on github.com; no REST API involved.
        owner_env = os.environ.get("GH_OWNER") or os.environ.get("GITHUB_ACTOR") or "yh-liao-07"
        owner = owner_env
        print(f"INFO  push-only mode → pushing to {owner}/{args.repo} (create the empty repo on github.com first)")
        if args.dry_run:
            print("INFO  dry-run: no changes made")
            return
        # Bare URL — credentials come from the local store (~/.git-credentials via
        # credential.helper=store) or from `git credential approve`; never embed
        # a token in .git/config or in process arguments.
        remote = f"https://github.com/{owner}/{args.repo}.git"
        git("remote", "remove", "origin", cwd=repo_dir)
        r = git("remote", "add", "origin", remote, cwd=repo_dir)
        if r.returncode != 0:
            print("FAIL  remote add:", r.stderr.strip())
            sys.exit(1)
        r = git("push", "-u", "origin", "main", cwd=repo_dir)
        if r.returncode != 0:
            print("FAIL  push:", r.stderr.strip())
            sys.exit(1)
        print(f"PASS  pushed main -> https://github.com/{owner}/{args.repo}")
        return

    # 1. verify token
    status, who = http_json("GET", "/user", token)
    if status != 200:
        print(f"FAIL  token rejected ({status}): {who.get('message', 'unknown')}")
        print("      generate a fresh PAT (classic 'repo' scope, or fine-grained with Contents R/W)")
        print("      then: python tools/publish.py --token <new-token>")
        print("      (or create the empty repo on github.com and use: python tools/publish.py --push-only)")
        sys.exit(1)
    owner = who["login"]
    print(f"PASS  token ok for @{owner}")

    # 2. repo state
    status, existing = http_json("GET", f"/repos/{owner}/{args.repo}", token)
    if status == 200:
        print(f"INFO  repo {owner}/{args.repo} already exists (skip create)")
    elif status == 404:
        if args.dry_run:
            print(f"INFO  (dry-run) would create {owner}/{args.repo} (public={not args.private})")
        else:
            body = {
                "name": args.repo,
                "description": "Distilled Lu Xun writing skill — plain-style narration, irony, short-sentence rhythm. Built with the dot-skill engine.",
                "public": not args.private,
                "has_issues": True,
                "has_wiki": True,
            }
            status, created = http_json("POST", "/user/repos", token, body)
            if status not in (200, 201):
                print(f"FAIL  repo create returned {status}: {created.get('message', '')}")
                sys.exit(1)
            print(f"PASS  created {owner}/{args.repo}")
    else:
        print(f"FAIL  repo check returned {status}: {existing.get('message', '')}")
        sys.exit(1)

    if args.dry_run:
        print("INFO  dry-run: no changes made")
        return

    # 3. push
    remote = f"https://github.com/{owner}/{args.repo}.git"
    git("remote", "remove", "origin", cwd=repo_dir)
    r = git("remote", "add", "origin", remote, cwd=repo_dir)
    if r.returncode != 0:
        print("FAIL  remote add:", r.stderr.strip())
        sys.exit(1)
    r = git("push", "-u", "origin", "main", cwd=repo_dir)
    if r.returncode != 0:
        print("FAIL  push:", r.stderr.strip())
        sys.exit(1)
    print(f"PASS  pushed main -> https://github.com/{owner}/{args.repo}")


if __name__ == "__main__":
    main()