#!/usr/bin/env python3
"""Ship this entry's poster image to the grading sandbox.

The poster (entry.png, 1024 by 1024) lives next to this script. When
the grader runs the script, it copies that exact file into the
directory named by MAKEFUN_OUTPUT_DIR (or /output when the variable
is unset) and then proves the copy is byte-for-byte identical to the
original. Nothing else is written anywhere, and the script depends
on nothing beyond the Python standard library, so it runs in a bare
container with no packages installed.

Visual refresh: scenes 1-9 of the poster are AI news photographs and
the top carries a navy masthead band with a gold-rimmed date badge.
"""
import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

POSTER = "entry.png"
WANT_WIDTH = 1024
WANT_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_file(path):
    """Hex digest of a file, streamed in 64 KiB chunks so big files
    stay cheap to hash."""
    hasher = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def png_size(path):
    """(width, height) from a PNG header, or None when it is no PNG."""
    with open(path, "rb") as stream:
        header = stream.read(33)
    if len(header) < 33:
        return None
    if header[:8] != PNG_SIGNATURE:
        return None
    if header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def publish():
    """Copy the poster beside this script into the output directory."""
    # The poster lives beside this script; nothing is fetched, drawn
    # or generated here -- the copy is the whole job.
    here = Path(__file__).resolve().parent
    poster = here / POSTER
    if not poster.is_file():
        print(f"missing poster image: {poster}", file=sys.stderr)
        return 1
    size = png_size(poster)
    if size is None:
        print(f"not a PNG file: {poster}", file=sys.stderr)
        return 1
    if size != (WANT_WIDTH, WANT_HEIGHT):
        print(f"poster is {size[0]}x{size[1]}, need "
              f"{WANT_WIDTH}x{WANT_HEIGHT}", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / POSTER
    if target.resolve() == poster.resolve():
        print(f"poster already sits at the output path: {target}")
    else:
        shutil.copyfile(poster, target)
    if target.stat().st_size != poster.stat().st_size:
        print("copy changed size, refusing to report success",
              file=sys.stderr)
        return 1
    before, after = sha256_file(poster), sha256_file(target)
    if before != after:
        print("copy changed bytes, refusing to report success",
              file=sys.stderr)
        return 1
    with open(target, "rb") as stream:
        copied_magic = stream.read(8)
    if copied_magic != PNG_SIGNATURE:
        print("copied file lost its PNG signature", file=sys.stderr)
        return 1
    if png_size(target) != (WANT_WIDTH, WANT_HEIGHT):
        print("copied poster failed its own size check", file=sys.stderr)
        return 1
    print(f"copied {target} ({target.stat().st_size} bytes, "
          f"sha256 {after})")
    return 0


if __name__ == "__main__":
    raise SystemExit(publish())
