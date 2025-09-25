from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThread import EmbThread
from ..utils.ReadHelper import read_int_8


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    while True:
        red = read_int_8(f)
        green = read_int_8(f)
        blue = read_int_8(f)
        if blue is None or red is None or green is None:
            return
        f.seek(1, 1)
        thread = EmbThread()
        thread.set_color(red, green, blue)
        out.add_thread(thread)
