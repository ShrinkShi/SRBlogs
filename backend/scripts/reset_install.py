from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.install_service import ensure_base_data_dirs, install_lock_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reset SRBlogs installation state.")
    parser.add_argument("--wipe-data", action="store_true", help="Delete all backend/data content. Requires --yes.")
    parser.add_argument("--yes", action="store_true", help="Confirm destructive --wipe-data operation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lock = install_lock_path()
    data_dir = lock.parent

    if args.wipe_data:
        if not args.yes:
            print("--wipe-data is destructive and requires --yes.", file=sys.stderr)
            return 2
        resolved = data_dir.resolve()
        if resolved == resolved.parent or not str(resolved).replace("\\", "/").endswith("/data"):
            print(f"Refuse to wipe suspicious data directory: {resolved}", file=sys.stderr)
            return 2
        if data_dir.exists():
            shutil.rmtree(data_dir)
        ensure_base_data_dirs()
        print(f"Installation state and business data wiped under {data_dir}.")
        return 0

    if lock.exists():
        lock.unlink()
        print(f"Removed install lock: {lock}")
    else:
        print(f"Install lock is already absent: {lock}")
    print("Business data was preserved. Visit /install to run the installer again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
