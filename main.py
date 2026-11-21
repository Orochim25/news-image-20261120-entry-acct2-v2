#!/usr/bin/env python3
"""news-image-20261120 v4 — acct2 (Orochim25).

Copies the pre-built entry.png (in this repository's root) into
$MAKEFUN_OUTPUT_DIR/entry.png (default /output).

v4: 11 AI photographs (3 heroes + 8 grid scenes) and a world map with
fixed lat/lon dots in the bottom-left corner; 35 verified stories.

Standard library only: no third-party imports, no network.
"""
import hashlib
import os
import shutil
import sys

MAX_BYTES = 1048576


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print("entry.png too large: %d bytes (limit %d)" % (size, MAX_BYTES),
              file=sys.stderr)
        return 1
    sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Verify the copy byte-for-byte before reporting success.
    dst_sha = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    if dst_sha != sha:
        print("copy mismatch: %s != %s" % (dst_sha, sha), file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, sha256 %s)" % (dst, size, sha))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
