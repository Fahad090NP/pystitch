from typing import BinaryIO, Optional, Any

from .DszReader import z_stitch_encoding_read
from ..core.EmbPattern import EmbPattern


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    f.seek(0x100)
    z_stitch_encoding_read(f, out)
