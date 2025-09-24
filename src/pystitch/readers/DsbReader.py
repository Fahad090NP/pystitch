"""DSB file format reader for embroidery patterns.

This module provides functionality to read DSB embroidery files,
parsing stitch data into an EmbPattern object using the B-stitch encoding format.
"""

from typing import BinaryIO, Optional, Dict, Any

from .DstReader import dst_read_header
from ..core.EmbPattern import EmbPattern


def b_stitch_encoding_read(f: BinaryIO, out: EmbPattern) -> None:
    """Read B-stitch encoded data from DSB file and add stitches to pattern.
    
    Args:
        f: Binary file object to read from
        out: EmbPattern object to add stitches to
    """
    count = 0
    while True:
        count += 1
        byte = bytearray(f.read(3))
        if len(byte) != 3:
            break

        ctrl = byte[0]
        y = -byte[1]
        x = byte[2]

        if ctrl & 0x40 != 0:
            y = -y
        if ctrl & 0x20 != 0:
            x = -x

        if (ctrl & 0b11111) == 0:
            out.stitch(x, y)  # type: ignore
            continue
        if (ctrl & 0b11111) == 1:
            out.move(x, y)  # type: ignore
            continue
        if ctrl == 0xF8:
            break
        if ctrl == 0xE7:
            out.trim()  # type: ignore
            continue
        if ctrl == 0xE8:
            out.stop()  # type: ignore
            continue
        if 0xE9 <= ctrl < 0xF8:
            needle = ctrl - 0xE8
            out.needle_change(needle)  # type: ignore
            continue
        break  # Uncaught Control
    out.end()  # type: ignore


def read(f: BinaryIO, out: EmbPattern,
         settings: Optional[Dict[str, Any]] = None) -> None:
    """Read DSB embroidery file and populate pattern with stitches.
    
    Args:
        f: Binary file object to read from
        out: EmbPattern object to populate with stitch data
        settings: Optional dictionary of reader settings (unused in DSB format)
    """
    # settings parameter is part of the reader interface but unused for DSB format
    _ = settings  # Acknowledge parameter to avoid unused argument warning
    dst_read_header(f, out)
    b_stitch_encoding_read(f, out)
