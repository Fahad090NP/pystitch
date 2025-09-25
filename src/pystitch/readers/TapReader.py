from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from .DstReader import dst_read_stitches


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    dst_read_stitches(f, out, settings)
