from __future__ import annotations

import socket

from enum import IntFlag, StrEnum, auto
from dataclasses import dataclass

from typing import Protocol, TypeVar, Generic, Type as T


Self = TypeVar("Self")


class BytesConvertible(Protocol):
    def into_bytes(self) -> bytes:
        ...

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        ...


B = TypeVar("B", bound=BytesConvertible)


class parse(Generic[B]):
    def __new__(cls, data: bytes, length: int, t: T[B], /) -> tuple[bytes, B]:
        return data[length:], t.from_bytes(data[:length])


class Type(IntFlag):
    CONTROL = auto()
    CHAT = auto()

    def into_bytes(self) -> bytes:
        return self.value.to_bytes(1, "big")

    @classmethod
    def from_bytes(cls, data: bytes) -> Type:
        return cls(int.from_bytes(data, "big"))


class Operation(IntFlag):
    ERR = 0x1
    SYN = 0x2
    ACK = 0x4
    FIN = 0x8

    def __str__(self) -> str:
        return self.name

    def into_bytes(self) -> bytes:
        return self.value.to_bytes(1, "big")

    @classmethod
    def from_bytes(cls, data: bytes) -> Operation:
        return cls(int.from_bytes(data, "big"))


class Sequence(IntFlag):
    RE = auto()
    NORE = auto()

    def into_bytes(self) -> bytes:
        return self.value.to_bytes(1, "big")

    @classmethod
    def from_bytes(cls, data: bytes) -> Sequence:
        return cls(int.from_bytes(data, "big"))


class Command(StrEnum):
    HELP = auto()
    LIST = auto()
    CHAT = auto()

    @property
    def arg_num(self) -> int:
        match self:
            case Command.HELP:
                return 0
            case Command.LIST:
                return 0
            case Command.CHAT:
                return 1

    @classmethod
    def try_from(cls, command: str) -> Command | None:
        try:
            return cls(command)
        except ValueError:
            return None


@dataclass
class Header:
    type: Type
    operation: Operation
    sequence: Sequence
    user: str
    length: int

    def into_bytes(self) -> bytes:
        return (
            self.type.into_bytes()
            + self.operation.into_bytes()
            + self.sequence.into_bytes()
            + self.user.encode()
            + self.length.to_bytes(4, "big")
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> Header:
        data, _type = parse[Type](data, 1, Type)
        data, _operation = parse[Operation](data, 1, Operation)
        data, _sequence = parse[Sequence](data, 1, Sequence)
        _user, data = data[:32].decode(), data[32:]
        _length = int.from_bytes(data[:4], "big")
        return cls(_type, _operation, _sequence, _user, _length)


@dataclass
class Message:
    header: Header
    data: str

    @property
    def is_control(self) -> bool:
        return self.header.type == Type.CONTROL

    @property
    def is_chat(self) -> bool:
        return self.header.type == Type.CHAT

    @property
    def operation(self) -> Operation:
        return self.header.operation

    @property
    def type(self) -> Type:
        return self.header.type

    def into_bytes(self) -> bytes:
        return self.header.into_bytes() + self.data.encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> Message:
        _header = Header.from_bytes(data[:39])
        _data = data[39:].decode()
        return cls(_header, _data)

    @classmethod
    def chat(cls, content: str, user: str, *, resend: bool = False) -> Message:
        # pad and crop the user str to be exactly 32 bytes
        user = user.ljust(32, "\0")[:32]

        _header = Header(
            Type.CHAT,
            Operation.ERR,
            Sequence.RE if resend else Sequence.NORE,
            user,
            len(content),
        )

        return cls(_header, content)

    @classmethod
    def control(
        cls, user: str, operation: Operation, *, resend: bool = False, message: str = ""
    ) -> Message:
        # pad and crop the user str to be exactly 32 bytes
        user = user.ljust(32, "\0")[:32]

        if operation != Operation.ERR and message:
            raise ValueError(
                "[SIMP ERROR]: Message can only be set for ERR operations!"
            )

        _header = Header(
            Type.CONTROL,
            operation,
            Sequence.RE if resend else Sequence.NORE,
            user,
            len(message),
        )

        return cls(_header, message)


@dataclass
class User:
    name: str
    host: str = "localhost"
    port: int = 5000

    def connect(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            print(f"Connecting to {self.host}:{self.port}")

            while (content := input(f"[{self.name}]: ")) != "quit":
                coded_message = Message.chat(content, self.name)

                client.sendto(coded_message.into_bytes(), (self.host, self.port))

                response, address = client.recvfrom(4096)

                print(f"Received {len(response)} bytes from {address}")

                print(f"{response.decode()}")
            else:
                exit_message = Message.control(self.name, Operation.FIN)
                client.sendto(exit_message.into_bytes(), (self.host, self.port))

        return 0

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, User):
            return self.name == __o.name
        return False

    def establish_handshake(self):
        # TODO!
        ...
