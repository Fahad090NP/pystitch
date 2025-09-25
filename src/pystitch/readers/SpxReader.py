from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..utils.ReadHelper import read_int_8, read_int_16be, signed8, signed16


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    f.seek(0x11E, 1)
    while True:
        b = bytearray(f.read(2))
        if len(b) != 2:
            break
        dy = -signed16(read_int_16be(f))  # type: ignore
        dx = signed16(read_int_16be(f))  # type: ignore
        c = signed8(read_int_8(f))  # type: ignore
        dy -= c  # type: ignore
        b = bytearray(f.read(2))
        if len(b) != 2:
            break
        out.stitch(dx, dy)  # type: ignore
