#!/usr/bin/env python3
"""news-image-20261122 V1-fresh entrypoint (Python 3.13, standard library only).

Copies the pre-rendered entry image to /output/entry.png. The image was
drawn in this session by render.py (a build-time script kept in this
repository for transparency); this program only copies bytes, so two runs
are byte-identical and it needs no network.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    created = not os.path.isdir(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Guard the gate: the copy must be whole, or the run must fail loudly
    # instead of submitting a truncated file.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise RuntimeError("entry.png copy is incomplete")
    # The output must be readable by every user: file 0644, folder 0755.
    os.chmod(dst, 0o644)
    if created:
        os.chmod(out_dir, 0o755)


if __name__ == "__main__":
    main()
