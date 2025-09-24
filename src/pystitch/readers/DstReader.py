"""DST file format reader for embroidery patterns.

This module provides functionality to read DST (Tajima) embroidery files,
parsing both header information and stitch data into an EmbPattern object.
DST is a popular embroidery format used by Tajima and other embroidery machines."""

from typing import BinaryIO, Optional, Dict, Any

from ..core.EmbPattern import EmbPattern

def getbit(b: int, pos: int) -> int:
    return (b >> pos) & 1

def decode_dx(b0: int, b1: int, b2: int) -> int:
    x = 0
    x += getbit(b2, 2) * (+81)
    x += getbit(b2, 3) * (-81)
    x += getbit(b1, 2) * (+27)
    x += getbit(b1, 3) * (-27)
    x += getbit(b0, 2) * (+9)
    x += getbit(b0, 3) * (-9)
    x += getbit(b1, 0) * (+3)
    x += getbit(b1, 1) * (-3)
    x += getbit(b0, 0) * (+1)
    x += getbit(b0, 1) * (-1)
    return x

def decode_dy(b0: int, b1: int, b2: int) -> int:
    y = 0
    y += getbit(b2, 5) * (+81)
    y += getbit(b2, 4) * (-81)
    y += getbit(b1, 5) * (+27)
    y += getbit(b1, 4) * (-27)
    y += getbit(b0, 5) * (+9)
    y += getbit(b0, 4) * (-9)
    y += getbit(b1, 7) * (+3)
    y += getbit(b1, 6) * (-3)
    y += getbit(b0, 7) * (+1)
    y += getbit(b0, 6) * (-1)
    return -y

def process_header_info(out: EmbPattern, prefix: str, value: str) -> None:
    if prefix == "LA":
        out.metadata("name", value)  # type: ignore
    elif prefix == "AU":
        out.metadata("author", value)  # type: ignore
    elif prefix == "CP":
        out.metadata("copyright", value)  # type: ignore
    elif prefix == "TC":
        values = [x.strip() for x in value.split(",")]
        thread_dict = {"hex": values[0], "description": values[1], "catalog": values[2]}
        out.add_thread(thread_dict)  # type: ignore
    else:
        out.metadata(prefix, value)  # type: ignore

def dst_read_header(f: BinaryIO, out: EmbPattern) -> None:
    header = f.read(512)
    start = 0
    for i, element in enumerate(header):
        if (
            element == 13 or element == 10
        ):  # 13 =='\r', 10 = '\n'
            end = i
            data = header[start:end]
            start = end
            try:
                line = data.decode("utf8").strip()
                if len(line) > 3:
                    process_header_info(out, line[0:2].strip(), 
                                       line[3:].strip())
            except UnicodeDecodeError:  # Non-utf8 information. See #83
                continue

def dst_read_stitches(f: BinaryIO, out: EmbPattern, 
                     settings: Optional[Dict[str, Any]] = None) -> None:
    sequin_mode = False
    while True:
        byte = bytearray(f.read(3))
        if len(byte) != 3:
            break
        dx = decode_dx(byte[0], byte[1], byte[2])
        dy = decode_dy(byte[0], byte[1], byte[2])
        if byte[2] & 0b11110011 == 0b11110011:
            break
        elif byte[2] & 0b11000011 == 0b11000011:
            out.color_change(dx, dy)  # type: ignore
        elif byte[2] & 0b01000011 == 0b01000011:
            out.sequin_mode(dx, dy)  # type: ignore
            sequin_mode = not sequin_mode
        elif byte[2] & 0b10000011 == 0b10000011:
            if sequin_mode:
                out.sequin_eject(dx, dy)  # type: ignore
            else:
                out.move(dx, dy)  # type: ignore
        else:
            out.stitch(dx, dy)  # type: ignore
    out.end()  # type: ignore

    count_max = 3
    clipping = True
    trim_distance = None
    if settings is not None:
        count_max = settings.get("trim_at", count_max)
        trim_distance = settings.get("trim_distance", trim_distance)
        clipping = settings.get("clipping", clipping)
    if trim_distance is not None:
        trim_distance *= 10  # Pixels per mm. Native units are 1/10 mm.
    out.interpolate_trims(count_max, trim_distance, clipping)  # type: ignore

def read(f: BinaryIO, out: EmbPattern, 
         settings: Optional[Dict[str, Any]] = None) -> None:
    dst_read_header(f, out)
    dst_read_stitches(f, out, settings)
