from __future__ import annotations

from argparse import ArgumentParser

from simp import *


def main(username: str, host: str, port: int) -> int:
    user = User(username, host, port)

    user.connect()

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="localhost", help="The host to listen on")
    parser.add_argument("--port", type=int, default=8745, help="The port to listen on")

    args = parser.parse_args()

    username = input("Enter your username: ")

    try:
        raise SystemExit(main(username, args.host, args.port))
    except KeyboardInterrupt:
        print("Logging out...")
        raise SystemExit(0)
