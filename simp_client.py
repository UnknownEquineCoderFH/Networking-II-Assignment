from __future__ import annotations

import socket
from argparse import ArgumentParser

from simp import *


def send_message(host: str, port: int, message: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        # Send data
        print(f"Sending data to {host}:{port}")

        client.sendto(message.encode(), (host, port))

        # Receive response
        data, address = client.recvfrom(4096)
        print(f"Received {len(data)} bytes from {address}")

    return 0


def main(host: str, port: int) -> int:
    while True:
        message = input(">>> ")
        send_message(host, port, message)

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="localhost", help="The host to listen on")
    parser.add_argument("--port", type=int, default=8745, help="The port to listen on")

    args = parser.parse_args()

    try:
        raise SystemExit(main(args.host, args.port))
    except KeyboardInterrupt:
        print("Logging out...")
        raise SystemExit(0)
