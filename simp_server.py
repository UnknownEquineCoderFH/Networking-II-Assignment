from __future__ import annotations

import time
import socket
from argparse import ArgumentParser

from simp import *


def main(host: str, port: int) -> int:
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        # Bind the socket to the port
        server.bind((host, port))

        print(f"Listening on {host}:{port}...")

        # Receive data
        while True:
            # print("Waiting to receive message")

            data, address = server.recvfrom(4096)

            print(f"Received {len(data)} bytes from {address}")

            if data:
                sent = server.sendto(data, address)
                print(f"Sent {sent} bytes back to {address}")

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="localhost", help="The host to listen on")
    parser.add_argument("--port", type=int, default=8745, help="The port to listen on")

    args = parser.parse_args()

    try:
        raise SystemExit(main(args.host, args.port))
    except KeyboardInterrupt:
        print("Exiting...")
        time.sleep(1)
        raise SystemExit(0)
