from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThread import EmbThread
from ..utils.ReadHelper import (
    read_int_8,
    read_int_16be,
    read_int_24be,
    read_int_32be,
    read_signed,
    read_string_8,
    read_string_16,
)


def read_vp3_string_16(stream: BinaryIO) -> Optional[str]:
    # Reads the header strings which are 16le numbers of size followed by
    # utf-16 text
    string_length = read_int_16be(stream)
    if string_length is None:
        return None
    return read_string_16(stream, string_length)  # type: ignore


def read_vp3_string_8(stream: BinaryIO) -> Optional[str]:
    # Reads the body strings which are 16be numbers followed by utf-8 text
    string_length = read_int_16be(stream)
    if string_length is None:
        return None
    return read_string_8(stream, string_length)  # type: ignore


def skip_vp3_string(stream: BinaryIO) -> None:
    string_length = read_int_16be(stream)
    if string_length is None:
        return
    stream.seek(string_length, 1)


def signed32(b: int) -> int:
    b &= 0xFFFFFFFF
    if b > 0x7FFFFFFF:
        return -0x100000000 + b
    else:
        return b


def signed16(b0: int, b1: int) -> int:
    b0 &= 0xFF
    b1 &= 0xFF
    b = (b0 << 8) | b1
    if b > 0x7FFF:
        return -0x10000 + b
    else:
        return b


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    _b = f.read(6)
    # magic code: %vsm%\0
    skip_vp3_string(f)  # "Produced by     Software Ltd"
    f.seek(7, 1)
    skip_vp3_string(f)  # "" comments and note string.
    f.seek(32, 1)
    center_x_val = read_int_32be(f)
    center_y_val = read_int_32be(f)
    if center_x_val is None or center_y_val is None:
        return
    center_x = signed32(center_x_val) / 100
    center_y = -(signed32(center_y_val) / 100)
    f.seek(27, 1)
    skip_vp3_string(f)  # ""
    f.seek(24, 1)
    skip_vp3_string(f)  # "Produced by     Software Ltd"
    count_colors = read_int_16be(f)
    if count_colors is None:
        return
    for i in range(0, count_colors):
        vp3_read_colorblock(f, out, center_x, center_y)
        if (i + 1) < count_colors:  # Don't add the color change on the final read.
            out.color_change()
    out.end()


def vp3_read_colorblock(f: BinaryIO, out: EmbPattern, center_x: float, center_y: float) -> None:
    _bytescheck = f.read(3)  # \x00\x05\x00
    distance_to_next_block_050 = read_int_32be(f)
    if distance_to_next_block_050 is None:
        return
    block_end_position = distance_to_next_block_050 + f.tell()

    start_pos_x_val = read_int_32be(f)
    start_pos_y_val = read_int_32be(f)
    if start_pos_x_val is None or start_pos_y_val is None:
        return
    start_position_x = signed32(start_pos_x_val) / 100
    start_position_y = -(signed32(start_pos_y_val) / 100)
    abs_x = start_position_x + center_x
    abs_y = start_position_y + center_y
    if abs_x != 0 and abs_y != 0:
        out.move_abs(abs_x, abs_y)
    thread = vp3_read_thread(f)
    out.add_thread(thread)
    f.seek(15, 1)
    _bytescheck = f.read(3)  # \x0A\xF6\x00
    stitch_byte_length = block_end_position - f.tell()
    stitch_bytes = read_signed(f, stitch_byte_length)  # type: ignore
    i = 0
    while i < len(stitch_bytes) - 1:  # type: ignore
        x = stitch_bytes[i]  # type: ignore
        y = stitch_bytes[i + 1]  # type: ignore
        i += 2
        if (x & 0xFF) != 0x80:  # type: ignore
            out.stitch(x, y)  # type: ignore
            continue
        if y == 0x01:  # type: ignore
            x = signed16(stitch_bytes[i], stitch_bytes[i + 1])  # type: ignore
            i += 2
            y = signed16(stitch_bytes[i], stitch_bytes[i + 1])  # type: ignore
            i += 2
            out.stitch(x, y)  # type: ignore
            i += 2
            # Final element is typically 0x80 0x02, this is skipped regardless of its value.
        elif y == 0x02:  # type: ignore
            # This is only seen after 80 01 and should have been skipped. Has no known effect.
            pass
        elif y == 0x03:  # type: ignore
            out.trim()


def vp3_read_thread(f: BinaryIO) -> EmbThread:
    thread = EmbThread()
    colors = read_int_8(f)
    _transition = read_int_8(f)
    if colors is not None:
        for _ in range(0, colors):
            color_val = read_int_24be(f)
            if color_val is not None:
                thread.color = color_val
            _parts = read_int_8(f)
            _color_length = read_int_16be(f)
    _thread_type = read_int_8(f)
    _weight = read_int_8(f)
    thread.catalog_number = read_vp3_string_8(f)  # type: ignore
    thread.description = read_vp3_string_8(f)  # type: ignore
    thread.brand = read_vp3_string_8(f)  # type: ignore
    return thread
