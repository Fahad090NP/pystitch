"""
DST file format writer for embroidery patterns.

This module provides functionality to write embroidery patterns to DST (Tajima) format files.
DST is a popular embroidery format used by Tajima and other embroidery machines.
The writer handles header generation, thread information, and stitch data encoding.
"""

from typing import BinaryIO, Optional, Dict, Any

from ..core.EmbConstant import (
    COMMAND_MASK, STITCH, JUMP, TRIM, STOP, END, COLOR_CHANGE,
    SEQUIN_MODE, SEQUIN_EJECT, CONTINGENCY_SEQUIN_UTILIZE
)
from ..core.EmbPattern import EmbPattern
from ..utils.WriteHelper import write_string_utf8  # type: ignore

SEQUIN_CONTINGENCY = CONTINGENCY_SEQUIN_UTILIZE
FULL_JUMP = False
ROUND = True
MAX_JUMP_DISTANCE = 121
MAX_STITCH_DISTANCE = 121

PPMM = 10
DSTHEADERSIZE = 512

def bit(b: int) -> int:
    return 1 << b

def encode_record(x: int, y: int, flags: int) -> bytes:
    y = -y  # flips the coordinate y space.
    b0 = 0
    b1 = 0
    b2 = 0
    if flags == JUMP or flags == SEQUIN_EJECT:
        b2 += bit(7)  # jumpstitch 10xxxx11
    if flags == STITCH or flags == JUMP or flags == SEQUIN_EJECT:
        b2 += bit(0)
        b2 += bit(1)
        if x > 40:
            b2 += bit(2)
            x -= 81
        if x < -40:
            b2 += bit(3)
            x += 81
        if x > 13:
            b1 += bit(2)
            x -= 27
        if x < -13:
            b1 += bit(3)
            x += 27
        if x > 4:
            b0 += bit(2)
            x -= 9
        if x < -4:
            b0 += bit(3)
            x += 9
        if x > 1:
            b1 += bit(0)
            x -= 3
        if x < -1:
            b1 += bit(1)
            x += 3
        if x > 0:
            b0 += bit(0)
            x -= 1
        if x < 0:
            b0 += bit(1)
            x += 1
        if x != 0:
            raise ValueError(
                "The dx value given to the writer exceeds maximum allowed."
            )
        if y > 40:
            b2 += bit(5)
            y -= 81
        if y < -40:
            b2 += bit(4)
            y += 81
        if y > 13:
            b1 += bit(5)
            y -= 27
        if y < -13:
            b1 += bit(4)
            y += 27
        if y > 4:
            b0 += bit(5)
            y -= 9
        if y < -4:
            b0 += bit(4)
            y += 9
        if y > 1:
            b1 += bit(7)
            y -= 3
        if y < -1:
            b1 += bit(6)
            y += 3
        if y > 0:
            b0 += bit(7)
            y -= 1
        if y < 0:
            b0 += bit(6)
            y += 1
        if y != 0:
            raise ValueError(
                "The dy value given to the writer exceeds maximum allowed."
            )
    elif flags == COLOR_CHANGE:
        b2 = 0b11000011
    elif flags == STOP:
        b2 = 0b11000011
    elif flags == END:
        b2 = 0b11110011
    elif flags == SEQUIN_MODE:
        b2 = 0b01000011
    return bytes(bytearray([b0, b1, b2]))

def write(pattern: EmbPattern, f: BinaryIO,
          settings: Optional[Dict[str, Any]] = None) -> None:
    extended_header = False
    trim_at = 3
    if settings is not None:
        extended_header = settings.get(
            "extended header", extended_header
        )  # deprecated, use version="extended"
        version = settings.get("version", "default")
        if version == "extended":
            extended_header = True
        trim_at = settings.get("trim_at", trim_at)
    bounds = pattern.bounds()  # type: ignore

    name = pattern.get_metadata("name", "Untitled")  # type: ignore

    write_string_utf8(f, f"LA:{str(name):<16}\r")  # type: ignore
    write_string_utf8(f, f"ST:{pattern.count_stitches():7d}\r")  # type: ignore
    color_count = (pattern.count_color_changes()  # type: ignore
                   + pattern.count_stitch_commands(STOP))  # type: ignore
    write_string_utf8(f, f"CO:{color_count:3d}\r")  # type: ignore
    write_string_utf8(f, f"+X:{abs(float(bounds[2])):5d}\r")  # type: ignore
    write_string_utf8(f, f"-X:{abs(float(bounds[0])):5d}\r")  # type: ignore
    write_string_utf8(f, f"+Y:{abs(float(bounds[3])):5d}\r")  # type: ignore
    write_string_utf8(f, f"-Y:{abs(float(bounds[1])):5d}\r")  # type: ignore
    ax = 0
    ay = 0
    if len(pattern.stitches) > 0:  # type: ignore
        last = len(pattern.stitches) - 1  # type: ignore
        ax = int(float(pattern.stitches[last][0]))  # type: ignore
        ay = -int(float(pattern.stitches[last][1]))  # type: ignore
    if ax >= 0:
        write_string_utf8(f, f"AX:+{ax:5d}\r")  # type: ignore
    else:
        write_string_utf8(f, f"AX:-{abs(ax):5d}\r")  # type: ignore
    if ay >= 0:
        write_string_utf8(f, f"AY:+{ay:5d}\r")  # type: ignore
    else:
        write_string_utf8(f, f"AY:-{abs(ay):5d}\r")  # type: ignore
    write_string_utf8(f, f"MX:+{0:5d}\r")  # type: ignore
    write_string_utf8(f, f"MY:+{0:5d}\r")  # type: ignore
    write_string_utf8(f, f"PD:{'******':6s}\r")  # type: ignore
    if extended_header:
        author = pattern.get_metadata("author")  # type: ignore
        if author is not None:
            write_string_utf8(f, f"AU:{str(author)}\r")  # type: ignore
        meta_copyright = pattern.get_metadata("copyright")  # type: ignore
        if meta_copyright is not None:
            write_string_utf8(f, f"CP:{str(meta_copyright)}\r")  # type: ignore
        if len(pattern.threadlist) > 0:  # type: ignore
            for thread in pattern.threadlist:  # type: ignore
                thread_info = f"TC:{str(thread.hex_color())},{str(thread.description)},{str(thread.catalog_number)}\r"  # type: ignore
                write_string_utf8(f, thread_info)  # type: ignore
    f.write(b"\x1a")
    for _ in range(f.tell(), DSTHEADERSIZE):
        f.write(b"\x20")  # space

    stitches = pattern.stitches  # type: ignore
    xx = 0
    yy = 0
    for stitch in stitches:  # type: ignore
        x = float(stitch[0])  # type: ignore
        y = float(stitch[1])  # type: ignore
        data = int(stitch[2]) & COMMAND_MASK  # type: ignore
        dx = int(round(x - xx))
        dy = int(round(y - yy))

        xx += dx
        yy += dy
        if data == TRIM:
            delta = -4
            f.write(encode_record(-delta // 2, -delta // 2, JUMP))
            for _ in range(1, trim_at - 1):
                f.write(encode_record(delta, delta, JUMP))
                delta = -delta
            f.write(encode_record(delta // 2, delta // 2, JUMP))
        else:
            f.write(encode_record(dx, dy, data))
