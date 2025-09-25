from typing import BinaryIO, Optional, Dict, Any

from ..core.EmbPattern import EmbPattern
from ..utils.EmbFunctions import *
from ..utils.WriteHelper import write_string_utf8

TENTH_MM_PER_INCH = 254


def write(pattern: EmbPattern, stream: BinaryIO, settings: Optional[Dict[str, Any]] = None) -> None:
    write_string_utf8(stream, "c s\n")

    stitches = pattern.stitches
    xx = 0
    yy = 0

    # Start point = (0, 0)
    pattern.translate(-pattern.stitches[0][0], -pattern.stitches[0][1])

    for stitch in stitches:
        # 4 to convert 1/10mm to 1/40mm.
        x = stitch[0] / TENTH_MM_PER_INCH
        y = stitch[1] / TENTH_MM_PER_INCH
        data = stitch[2] & COMMAND_MASK
        dx = x - xx
        dy = y - yy
        xx += dx
        yy += dy
        if data == STITCH:
            write_string_utf8(stream, f'p X{xx:.4f} Y{-yy:.4f}\n')
        elif data == JUMP:
            write_string_utf8(stream, f'p X{xx:.4f} Y{-yy:.4f}\n')
