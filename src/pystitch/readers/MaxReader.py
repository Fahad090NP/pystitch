from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..utils.ReadHelper import read_int_8, read_int_24le, read_int_32le, signed24

MAX_SIZE_CONVERSION_RATIO = 1.235


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    f.seek(0xD5, 0)
    stitch_count = read_int_32le(f)
    if stitch_count is None:
        return
    for _ in range(0, stitch_count):
        x = read_int_24le(f)
        _ = read_int_8(f)  # c0 unused
        y = read_int_24le(f)
        c1 = read_int_8(f)
        if x is None or y is None or c1 is None:
            break
        x = signed24(x)  # type: ignore
        y = signed24(y)  # type: ignore
        x *= MAX_SIZE_CONVERSION_RATIO  # type: ignore
        y *= MAX_SIZE_CONVERSION_RATIO  # type: ignore
        out.stitch_abs(x, y)  # type: ignore
    out.end()
