#!/usr/bin/env python3
import sys
from pathlib import Path


src_path = Path(__file__).resolve().parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from aweswitch.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
