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

    @property
    def usernames(self) -> str:
        return "\n".join(f"{i + 1}) {user.name}" for i, user in enumerate(self.users))

    def run(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            server.bind((self.host, self.port))

            print(f"Server listening on {self.host}:{self.port}...")

            while True:
                data, address = server.recvfrom(4096)

                decoded_message = Message.from_bytes(data)

                username = decoded_message.header.user
                user = User(username, address[0], address[1])

                response = self.handle_message(user, decoded_message)

                server.sendto(response.encode(), address)

        return 0

    def handle_message(self, user: User, message: Message) -> str:
        self.add_user(user)
        match message.type:
            case Type.CHAT:
                command, *args = message.data.strip().split(" ")
                return self.handle_command(user, command, *args)
            case Type.CONTROL:
                return self.handle_control(user, message.operation)

    def add_user(self, user: User) -> None:
        if not any(user == u for u in self.users):
            self.users.append(user)

    def handle_command(self, user: User, command: str, *args: str) -> str:
        match Command.try_from(command):
            case Command.HELP:
                return "Commands: help, list, chat <user>"
            case Command.LIST:
                return f"Users:\n{self.usernames}"
            case Command.CHAT if len(args) == 1:
                selected_user = self.users[int(args[0]) - 1]

                if user == selected_user:
                    return "You cannot chat with yourself"

                return f"Connecting with user {selected_user.name}"
                # TODO: CREATE A CHAT

            case _:
                return f"Unknown command, try running `help` for more information"

    def handle_control(self, user: User, operation: Operation) -> str:
        match operation:
            case Operation.FIN:
                self.users.remove(user)
                return f"User {user.name} has disconnected"
            case op:
                return f"Invalid command, {op}"

    def chat(self, users: tuple[User, User], port: int) -> Chat:
        # Remove the users from the waiting list
        for user in users:
            self.users.remove(user)

        return Chat(users, host=self.host, port=port)


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
