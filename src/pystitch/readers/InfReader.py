from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThread import EmbThread
from ..utils.ReadHelper import read_int_16be, read_int_32be


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    _ = read_int_32be(f)  # u0 unused
    _ = read_int_32be(f)  # u1 unused
    _ = read_int_32be(f)  # u2 unused
    number_of_colors = read_int_32be(f)
    if number_of_colors is not None:
        for j in range(0, number_of_colors):
            length_raw = read_int_16be(f)
            if length_raw is None:
                break
            length = length_raw - 2  # 2 bytes of the length.
            byte_data = bytearray(f.read(length))
            if len(byte_data) != length:
                break
            red = byte_data[2]
            green = byte_data[3]
            blue = byte_data[4]
            thread = EmbThread()
            thread.set_color(red, green, blue)
            byte_data = byte_data[7:]
            for j in range(0, len(byte_data)):
                b = byte_data[j]
                if b == 0:
                    thread.description = byte_data[:j].decode("utf8")
                    byte_data = byte_data[j + 1 :]
                    break
            for j in range(0, len(byte_data)):
                b = byte_data[j]
                if b == 0:
                    thread.chart = byte_data[:j].decode("utf8")
                    break
            out.add_thread(thread)
