from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from .ExpReader import read_exp_stitches
from ..utils.ReadHelper import read_int_32le


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    # File starts with STX
    f.seek(0x0C, 1)
    _ = read_int_32le(f)  # color_start_position unused
    _ = read_int_32le(f)  # dunno_block_start_position unused
    stitch_start_position = read_int_32le(f)
    if stitch_start_position is not None:
        f.seek(stitch_start_position, 0)
        read_exp_stitches(f, out)
