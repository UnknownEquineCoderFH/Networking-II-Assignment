from __future__ import annotations

import time
import socket
from argparse import ArgumentParser

from dataclasses import field

from simp import *


@dataclass
class Chat:
    users: tuple[User, User]
    host: str
    port: int
    connection: socket.socket | None = None

    def __enter__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.bind((self.host, self.port))
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()


@dataclass
class Server:
    users: list[User] = field(default_factory=list)
    host: str = "localhost"
    port: int = 5000

    def run(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind((self.host, self.port))

            print(f"Server listening on {self.host}:{self.port}...")

            while True:
                data, address = server.recvfrom(4096)

                decoded_message = Message.from_bytes(data)

                print(f"Received {len(data)} bytes from {address}")
                print(f"Message: {decoded_message}")

                match decoded_message.data:
                    case "commands":
                        server.sendto("Commands: users, <username>".encode(), address)
                    case "users":
                        server.sendto(f"Users: {self.users}".encode(), address)
                    case username if username.isdecimal():
                        server.sendto(f"Connecting with user {username}".encode(), address)
                    case _:
                        server.sendto("Invalid command".encode(), address)

        return 0


    def chat(self, users: tuple[User, User], port: int) -> Chat:
        # Remove the users from the waiting list
        for user in users:
            self.users.remove(user)

        return Chat(users, host=self.host, port=port)
    
    def join(self, user: User) -> Server:
        # TODO!
        self.users.append(user)
        return self


def main(host: str, port: int) -> int:
    # Create a UDP socket
    server = Server(host=host, port=port)

    return server.run()


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
