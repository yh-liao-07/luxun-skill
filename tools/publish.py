#!/usr/bin/env python3
"""
Publish luxun-skill to GitHub. Idempotent: verify token -> create repo -> push.

Usage:
  python tools/publish.py                      # token from $GH_TOKEN or ~/.git-credentials
  python tools/publish.py --token ghp_xxx      # explicit classic PAT
  python tools/publish.py --push-only          # skip REST API: user created the repo on github.com first
  python tools/publish.py --dry-run            # verify token + repo state, do not push

Security notes:
- The token is never embedded in .git/config or in git's process arguments.
- For pushes with an explicit --token, a temporary GIT_ASKPASS helper is used
  and deleted immediately after the push (sandbox-safe: no ~/.git-credentials
  write is required).
- The remote URL is always bare (https://github.com/OWNER/REPO.git); credentials
  come from the askpass helper or the local credential store.

REST calls use TLS 1.2 + certifi, because sandboxed Windows shells frequently
cannot access the schannel certificate store; api.github.com is flaky there, so
requests are retried. The push itself uses `git` with the OpenSSL TLS backend
and the same CA file.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import certifi

API = "https://api.github.com"
DEFAULT_REPO = "luxun-skill"
DEFAULT_OWNER = "yh-liao-07"
MAX_API_ATTEMPTS = 5


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


def build_ssl_context() -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=certifi.where())
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    return context


def http_json(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    """Delegate to node tools/gh_api.mjs — Node's TLS reaches api.github.com reliably.

    Retried (short backoff) because the network layer occasionally resets
    connections even for node.
    """
    script = Path(__file__).resolve().parent / "gh_api.mjs"
    body_json = json.dumps(body, ensure_ascii=False) if body is not None else ""
    for attempt in range(1, MAX_API_ATTEMPTS + 1):
        try:
            result = subprocess.run(
                ["node", str(script), method, path, token, body_json],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0 or not result.stdout.strip():
                raise RuntimeError(result.stderr.strip() or "empty node output")
            payload = json.loads(result.stdout.strip())
            return int(payload["status"]), payload["payload"]
        except (subprocess.TimeoutExpired, OSError, RuntimeError, json.JSONDecodeError) as e:
            if attempt < MAX_API_ATTEMPTS:
                time.sleep(1.5 * attempt)
            else:
                raise
    raise RuntimeError("unreachable")


def ca_path() -> str:
    return certifi.where()


def git_base_cmd(*args: str) -> list[str]:
    return ["git", "-c", "http.sslBackend=openssl", "-c", f"http.sslCAInfo={ca_path()}", *args]


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    cmd = [*git_base_cmd(), *args]
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def git_push_explicit_token(repo_dir: Path, owner: str, token: str) -> subprocess.CompletedProcess:
    """Push with a token via a temporary GIT_ASKPASS helper.

    The helper prints the owner for the "Username" prompt and the token for the
    "Password" prompt. It is deleted immediately after the push, so the token
    never lands in .git/config or in git's own argv.
    """
    askpass = repo_dir / ".tmp-askpass.py"
    askpass.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "prompt = (sys.argv[1] if len(sys.argv) > 1 else '').lower()\n"
        f"if 'username' in prompt:\n    print({owner!r})\n"
        f"else:\n    print({token!r})\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["GIT_ASKPASS"] = str(askpass)
    cmd = [
        *git_base_cmd(),
        "-c", "credential.helper=",
        "push", "-u", "origin", "main",
    ]
    result = subprocess.run(cmd, cwd=repo_dir, text=True, capture_output=True, env=env)
    askpass.unlink(missing_ok=True)
    return result


def push(repo_dir: Path, owner: str, token: str | None, repo_name: str, repo_exists: bool) -> None:
    remote = f"https://github.com/{owner}/{repo_name}.git"
    r = git("remote", "remove", "origin", cwd=repo_dir)
    r = git("remote", "add", "origin", remote, cwd=repo_dir)
    if r.returncode != 0:
        print("FAIL  remote add:", r.stderr.strip())
        sys.exit(1)
    if token is not None:
        result = git_push_explicit_token(repo_dir, owner, token)
    else:
        result = git("push", "-u", "origin", "main", cwd=repo_dir)
    if result.returncode != 0:
        print("FAIL  push:", result.stderr.strip())
        sys.exit(1)
    print(f"PASS  pushed main -> https://github.com/{owner}/{repo_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish luxun-skill to GitHub")
    parser.add_argument("--token", help="GitHub PAT (classic repo, or fine-grained Contents R/W)")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Repository name")
    parser.add_argument("--owner", default=os.environ.get("GH_OWNER", DEFAULT_OWNER), help="Repository owner (default: yh-liao-07)")
    parser.add_argument("--public", action="store_true", help="Create public repo (default)")
    parser.add_argument("--private", action="store_true", help="Create private repo")
    parser.add_argument("--dry-run", action="store_true", help="Verify token + repo state without pushing")
    parser.add_argument(
        "--push-only",
        action="store_true",
        help="Skip REST API entirely: user created the empty repo on github.com first; only set origin and push",
    )
    args = parser.parse_args()

    token = resolve_token(args.token)
    repo_dir = Path(__file__).resolve().parent.parent

    if args.push_only:
        print(f"INFO  push-only mode -> pushing to {args.owner}/{args.repo}")
        if args.dry_run:
            print("INFO  dry-run: no changes made")
            return
        push(repo_dir, args.owner, token, args.repo, repo_exists=True)
        return

    # 1. verify token
    status, who = http_json("GET", "/user", token)
    if status != 200:
        print(f"FAIL  token rejected ({status}): {who.get('message', 'unknown')}")
        print("      generate a fresh PAT (classic 'repo' scope, or fine-grained Contents R/W)")
        print("      then: python tools/publish.py --token <new-token>")
        print("      (or create the empty repo on github.com and use: python tools/publish.py --push-only)")
        sys.exit(1)
    owner = who["login"]
    print(f"PASS  token ok for @{owner}")

    # 2. repo state
    status, existing = http_json("GET", f"/repos/{owner}/{args.repo}", token)
    if status == 200:
        print(f"INFO  repo {owner}/{args.repo} already exists (skip create)")
        repo_exists = True
    elif status == 404:
        repo_exists = False
        if args.dry_run:
            print(f"INFO  (dry-run) would create {owner}/{args.repo} (public={not args.private})")
        else:
            body = {
                "name": args.repo,
                "description": (
                    "Distilled Lu Xun writing skill — plain-style narration, irony, "
                    "short-sentence rhythm, restrained cold prose. Built with the dot-skill engine."
                ),
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
    push(repo_dir, owner, token, args.repo, repo_exists)


if __name__ == "__main__":
    main()