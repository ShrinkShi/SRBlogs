from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import get_settings
from app.services.admin_credentials import hash_admin_password
from app.services.install_service import update_process_environment, validate_password, write_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reset SRBlogs administrator credentials.")
    parser.add_argument("--username", default="", help="New administrator username. Defaults to current config or admin.")
    parser.add_argument("--password", default="", help="New password. If omitted, prompts without echo.")
    parser.add_argument("--env-file", default="", help="backend.env path. Defaults to ENV_FILE or /etc/srblogs/backend.env.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file
    get_settings.cache_clear()
    settings = get_settings()

    username = (args.username or settings.admin_username or "admin").strip()
    password = args.password or getpass.getpass("New admin password: ")
    if not args.password:
        confirm = getpass.getpass("Confirm admin password: ")
        if password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            return 2

    validate_password(username, password)
    values = {
        "ADMIN_USERNAME": username,
        "ADMIN_PASSWORD_HASH": hash_admin_password(password),
    }
    target = write_env(values)
    update_process_environment(values)
    print(f"Admin credentials updated in {target}. Restart srblogs-backend to refresh long-running processes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
