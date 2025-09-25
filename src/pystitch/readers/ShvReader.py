import math
from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..core.EmbConstant import *
from ..threads.EmbThreadShv import get_thread_set
from ..utils.ReadHelper import (
    read_int_8,
    read_int_16be,
    read_int_32be,
    read_string_8,
    signed8,
    signed16,
)


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    in_jump = False
    f.seek(0x56, 1)  # header text
    length = read_int_8(f)
    if length is not None:
        out.metadata("name", read_string_8(f, length))

    design_width = read_int_8(f)
    design_height = read_int_8(f)

    if design_width is not None and design_height is not None:
        skip = math.ceil(design_height / 2.0) * design_width
        f.seek(4 + int(skip), 1)
    color_count = read_int_8(f)
    f.seek(18, 1)
    threads = get_thread_set()
    stitch_per_color: dict[int, Optional[int]] = {}
    if color_count is not None:
        for i in range(color_count):
            stitch_count = read_int_32be(f)
            color_code = read_int_8(f)
            if color_code is not None:
                thread = threads[color_code % len(threads)]
                out.add_thread(thread)
            stitch_per_color[i] = stitch_count
            f.seek(9, 1)
    f.seek(-2, 1)

    stitches_since_stop = 0
    current_color_index = 0
    try:
        max_stitches = stitch_per_color[current_color_index]
    except (IndexError, KeyError):
        max_stitches = 0
    while True:
        flags = STITCH
        if in_jump:
            flags = JUMP
        b0 = read_int_8(f)
        b1 = read_int_8(f)
        if b1 is None:
            break
        if max_stitches is not None and stitches_since_stop >= max_stitches:
            out.color_change()
            stitches_since_stop = 0
            current_color_index += 1
            try:
                max_stitches = stitch_per_color[current_color_index]
            except KeyError:
                max_stitches = 0xFFFFFFFF
        if b0 == 0x80:
            stitches_since_stop += 1
            if b1 == 3:
                continue
            elif b1 == 2:
                in_jump = False
                continue
            elif b1 == 1:
                stitches_since_stop += 2
                sx_val = read_int_16be(f)
                sy_val = read_int_16be(f)
                if sx_val is not None and sy_val is not None:
                    sx = signed16(sx_val)  # type: ignore
                    sy = signed16(sy_val)  # type: ignore
                    in_jump = True
                    out.move(sx, sy)  # type: ignore
                continue
        if b0 is not None:
            dx = signed8(b0)  # type: ignore
            dy = signed8(b1)  # type: ignore
            stitches_since_stop += 1
            out.add_stitch_relative(flags, dx, dy)  # type: ignore
    out.end()
