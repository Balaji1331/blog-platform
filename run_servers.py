#!/usr/bin/env python
"""Run the BlogPlatform dev server on port 8000 AND port 8080 at the same time.

    python run_servers.py                 # 127.0.0.1:8000 and 127.0.0.1:8080
    python run_servers.py --host 0.0.0.0  # also reachable from other devices on your network

Press Ctrl+C once to stop both servers.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--ports", nargs="+", default=["8000", "8080"])
    args = parser.parse_args()

    manage = [sys.executable, str(ROOT / "manage.py")]
    # Migrate once up front so the two servers don't race on the SQLite file.
    subprocess.run(manage + ["migrate", "--noinput"], check=True, cwd=ROOT)

    procs = []
    try:
        for port in args.ports:
            print(f"Starting http://{args.host}:{port}/")
            procs.append(subprocess.Popen(manage + ["runserver", f"{args.host}:{port}"], cwd=ROOT))
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    main()
