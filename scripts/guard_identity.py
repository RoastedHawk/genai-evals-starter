#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys


def sh(*args: str) -> str:
    try:
        out = subprocess.check_output(args, text=True).strip()
    except Exception:
        out = ""
    return out


def parse_host(url: str) -> str:
    m = re.match(r"[^@]+@([^:]+):.*", url)
    if m:
        return m.group(1)
    m = re.match(r"https?://([^/]+)/.*", url)
    return m.group(1) if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-host", required=True)
    ap.add_argument("--expect-email", required=True)
    args = ap.parse_args()

    email = sh("git", "config", "--get", "user.email")
    origin = sh("git", "remote", "get-url", "origin")
    host = parse_host(origin)

    ok = True
    if email != args.expect_email:
        print(f"[guard-identity] user.email mismatch: {email!r} != {args.expect_email!r}")
        ok = False
    if host != args.expect_host:
        print(f"[guard-identity] remote host mismatch: {host!r} != {args.expect_host!r}")
        ok = False

    if not ok:
        print("[guard-identity] Refusing to push. Use the correct account or update per-repo config.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

