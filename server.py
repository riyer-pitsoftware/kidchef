"""Local entrypoint for the zero-dependency KidsChef backend server."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from kidschef_backend import create_server
from kidschef_backend.config import load_env_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the KidsChef local backend server.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000, help="Bind port. Default: 8000")
    parser.add_argument(
        "--base-dir",
        default=str(Path.cwd()),
        help="Base directory for local runtime data. Default: current working directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(args.base_dir)
    env_loaded = load_env_file(base_dir / ".env")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    server = create_server(args.host, args.port, base_dir=Path(args.base_dir))
    try:
        host_label = args.host if args.host != "0.0.0.0" else "localhost"
        print(f"KidsChef demo server ready")
        print(f"Web shell:  http://{host_label}:{args.port}/")
        print(f"API health: http://{host_label}:{args.port}/api/health")
        if env_loaded:
            print(f"Loaded env: {base_dir / '.env'}")
        if args.host == "0.0.0.0":
            print("LAN demo: use this machine's local network IP with the same port on iPhone Safari.")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
