#!/usr/bin/env python3
"""Create the GitHub Release for DS-SELF-GOVERNANCE-001 using a GCM-supplied token.

No `gh` CLI required. Token is obtained from git-credential-manager and never printed.
"""
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/001-self-governance"
REPO = "samirhosninet/Digital-State"
TAG = "v1.5-self-governance"
COMMIT = subprocess.run(
    ["git", "rev-parse", f"{TAG}^{{}}"], capture_output=True, text=True
).stdout.strip()


def get_token() -> str:
    out = subprocess.run(
        ["git", "credential-manager", "get"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        if line.lower().startswith("password="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("no password from GCM")


def main():
    token = get_token()
    body = (EV / "RELEASE_BODY.md").read_text(encoding="utf-8")
    payload = {
        "tag_name": TAG,
        "target_commitish": COMMIT,
        "name": "Digital State Self-Governance Event DS-SELF-GOVERNANCE-001",
        "body": body,
        "draft": False,
        "prerelease": False,
    }
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            print("RELEASE_CREATED id=%s html_url=%s" % (data.get("id"), data.get("html_url")))
    except urllib.error.HTTPError as e:
        print("HTTPError", e.code, e.read().decode("utf-8")[:800])


if __name__ == "__main__":
    main()
