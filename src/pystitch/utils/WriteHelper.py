import struct
from typing import BinaryIO, List, Union


def write_int_array_8(stream: BinaryIO, int_array: List[int]) -> None:
    for value in int_array:
        v = bytes(
            bytearray(
                [
                    value & 0xFF,
                ]
            )
        )
        stream.write(v)


def write_int_8(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                value & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_16le(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 0) & 0xFF,
                (value >> 8) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_16be(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 8) & 0xFF,
                (value >> 0) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_24le(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 0) & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_24be(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 0) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_32le(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 0) & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_int_32be(stream: BinaryIO, value: int) -> None:
    v = bytes(
        bytearray(
            [
                (value >> 24) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 0) & 0xFF,
            ]
        )
    )
    stream.write(v)


def write_float_32le(stream: BinaryIO, value: Union[int, float]) -> None:
    stream.write(struct.pack("<f", float(value)))


def write_string(stream: BinaryIO, string: str, encoding: str = "utf8") -> None:
    stream.write(bytes(string, encoding))


def write_string_utf8(stream: BinaryIO, string: str) -> None:
    stream.write(bytes(string, "utf8"))


__all__ = [
    'write_int_array_8', 'write_int_8', 'write_int_16le', 'write_int_16be',
    'write_int_24le', 'write_int_24be', 'write_int_32le', 'write_int_32be',
    'write_float_32le', 'write_string', 'write_string_utf8'
]
