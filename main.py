#!/usr/bin/env python3
"""Deterministic entry runner: copy entry.png to /output/entry.png."""

from pathlib import Path
import shutil

SRC = Path(__file__).resolve().parent / "entry.png"
DST = Path("/output/entry.png")


def main() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DST)


if __name__ == "__main__":
    main()
