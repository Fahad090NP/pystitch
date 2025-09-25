from typing import BinaryIO, Optional, Any

from .DstReader import dst_read_stitches
from ..core.EmbPattern import EmbPattern


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    f.seek(0x100)
    dst_read_stitches(f, out, settings)
