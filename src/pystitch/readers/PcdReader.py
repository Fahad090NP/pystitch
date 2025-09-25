from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThread import EmbThread
from ..utils.ReadHelper import (
    read_int_8,
    read_int_16le,
    read_int_24be,
    read_int_24le,
    signed24,
)

PC_SIZE_CONVERSION_RATIO = 5.0 / 3.0


def read_pc_file(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    _version = read_int_8(f)
    _hoop_size = read_int_8(f)
    # 0 for PCD,
    # 1 for PCQ (MAXI),
    # 2 for PCS small hoop(80x80),
    # 3 for PCS with large hoop.
    color_count = read_int_16le(f)
    if color_count is None:
        color_count = 0
    for _ in range(0, color_count):
        thread = EmbThread()
        color_val = read_int_24be(f)
        if color_val is not None:
            thread.color = color_val
        out.add_thread(thread)
        f.seek(1, 1)

    _stitch_count = read_int_16le(f)
    while True:
        _c0 = read_int_8(f)
        x_val = read_int_24le(f)
        _c1 = read_int_8(f)
        y_val = read_int_24le(f)
        ctrl = read_int_8(f)
        if ctrl is None or x_val is None or y_val is None:
            break
        x = signed24(x_val)  # type: ignore
        y = -signed24(y_val)  # type: ignore
        x *= PC_SIZE_CONVERSION_RATIO  # type: ignore
        y *= PC_SIZE_CONVERSION_RATIO  # type: ignore
        if ctrl == 0x00:
            out.stitch_abs(x, y)  # type: ignore
            continue
        if ctrl & 0x01:
            out.color_change()
            continue
        if ctrl & 0x04:
            out.move_abs(x, y)  # type: ignore
            continue
        break  # Uncaught Control
    out.end()


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    read_pc_file(f, out)
