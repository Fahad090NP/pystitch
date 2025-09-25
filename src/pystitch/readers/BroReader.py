from typing import BinaryIO, Optional, Any
from ..core.EmbPattern import EmbPattern
from ..utils.ReadHelper import read_int_8, read_int_16le, signed8, signed16

# Do you even embroider .bro?


def read_bro_stitches(f: BinaryIO, out: EmbPattern) -> None:
    count = 0
    while True:
        count += 1
        b = bytearray(f.read(2))
        if len(b) != 2:
            break
        if b[0] != 0x80:
            out.stitch(signed8(b[0]), -signed8(b[1]))  # type: ignore
            continue
        control = read_int_8(f)
        if control is None:
            break
        if control == 0x00:
            continue
        if control == 0x02:
            break
        if control == 0xE0:
            break
        if control == 0x7E:
            x_val = read_int_16le(f)
            y_val = read_int_16le(f)
            if x_val is not None and y_val is not None:
                x = signed16(x_val)  # type: ignore
                y = signed16(y_val)  # type: ignore
                out.move(x, -y)  # type: ignore
            continue
        if control == 0x03:
            x_val = read_int_16le(f)
            y_val = read_int_16le(f)
            if x_val is not None and y_val is not None:
                x = signed16(x_val)  # type: ignore
                y = signed16(y_val)  # type: ignore
                out.move(x, -y)  # type: ignore
            continue
        if 0xE0 < control < 0xF0:
            needle = control - 0xE0
            out.needle_change(needle)
            x_val = read_int_16le(f)
            y_val = read_int_16le(f)
            if x_val is not None and y_val is not None:
                x = signed16(x_val)  # type: ignore
                y = signed16(y_val)  # type: ignore
                out.move(x, -y)  # type: ignore
            continue
        break  # Uncaught Control
    out.end()


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    f.seek(0x100, 0)
    read_bro_stitches(f, out)
