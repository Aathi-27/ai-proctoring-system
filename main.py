#!/usr/bin/env python3
"""
Audio VAD Pipeline - Main entry point
"""
import argparse
from src.api import run_server
from src.config import HOST, PORT, DEBUG


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Audio VAD Pipeline Server")
    parser.add_argument("--host", default=HOST, help="Host address")
    parser.add_argument("--port", type=int, default=PORT, help="Port number")
    parser.add_argument("--debug", action="store_true", default=DEBUG, help="Enable debug mode")

    args = parser.parse_args()

    print(f"Starting Audio VAD Pipeline Server on {args.host}:{args.port}")
    run_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
