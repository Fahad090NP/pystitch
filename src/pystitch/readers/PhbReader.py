from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThreadPec import get_thread_set
from .PecReader import read_pec_stitches
from ..utils.ReadHelper import read_int_8, read_int_16le, read_int_32le


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    # should start #PHB0003
    f.seek(0x71, 0)
    color_count = read_int_16le(f)
    threadset = get_thread_set()
    if color_count is not None:
        for _ in range(0, color_count):
            thread_idx = read_int_8(f)
            if thread_idx is not None:
                out.add_thread(threadset[thread_idx % len(threadset)])

    file_offset = 0x52

    f.seek(0x54, 0)
    offset_val = read_int_32le(f)
    if offset_val is not None:
        file_offset += offset_val

        f.seek(file_offset, 0)
        offset_val2 = read_int_32le(f)
        if offset_val2 is not None:
            file_offset += offset_val2 + 2

            f.seek(file_offset, 0)
            offset_val3 = read_int_32le(f)
            if offset_val3 is not None:
                file_offset += offset_val3

                f.seek(file_offset + 14, 0)

                color_count2 = read_int_8(f)
                # 10 bytes unknown, PEC extends.
                if color_count2 is not None:
                    f.seek(color_count2 + 0x15, 1)

                    read_pec_stitches(f, out)
                    out.interpolate_duplicate_color_as_stop()
