from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..threads.EmbThreadPec import get_thread_set
from ..utils.ReadHelper import read_int_8, read_int_24le, read_string_8

JUMP_CODE = 0x10
TRIM_CODE = 0x20
FLAG_LONG = 0x80


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    pec_string = read_string_8(f, 8)  # type: ignore
    # pec_string must equal #PEC0001
    read_pec(f, out)
    out.interpolate_duplicate_color_as_stop()


def read_pec(f: BinaryIO, out: EmbPattern, pes_chart: Optional[Any] = None) -> None:
    f.seek(3, 1)  # LA:
    label = read_string_8(f, 16)  # Label
    if label is not None:
        out.metadata("Name", label.strip())
    f.seek(0xF, 1)  # Dunno, spaces then 0xFF 0x00
    pec_graphic_byte_stride = read_int_8(f)
    pec_graphic_icon_height = read_int_8(f)
    f.seek(0xC, 1)
    color_changes = read_int_8(f)
    if color_changes is None:
        return
    count_colors = color_changes + 1  # PEC uses cc - 1, 0xFF means 0. # type: ignore
    color_bytes = bytearray(f.read(count_colors))  # type: ignore
    threads = []
    map_pec_colors(color_bytes, out, pes_chart, threads)
    f.seek(0x1D0 - color_changes, 1)  # type: ignore
    stitch_block_end_val = read_int_24le(f)
    if stitch_block_end_val is None:
        return
    stitch_block_end = stitch_block_end_val - 5 + f.tell()  # type: ignore
    # The end of this value is already 5 into the stitchblock.

    # 3 bytes, '\x31\xff\xf0', 6 2-byte shorts. 15 total.
    f.seek(0x0F, 1)
    read_pec_stitches(f, out)
    f.seek(stitch_block_end, 0)

    if pec_graphic_byte_stride is not None and pec_graphic_icon_height is not None:
        byte_size = pec_graphic_byte_stride * pec_graphic_icon_height  # type: ignore
        read_pec_graphics(
            f, out, byte_size, pec_graphic_byte_stride, count_colors + 1, threads  # type: ignore
        )


def read_pec_graphics(f: BinaryIO, out: EmbPattern, size: Any, stride: Any, count: Any, values: Any) -> None:
    v = values[:]
    v.insert(0, None)
    for i in range(0, count):
        graphic = bytearray(f.read(size))
        name = "pec_graphic_" + str(i)
        out.metadata(name, (graphic, stride, v[i]))  # type: ignore


def process_pec_colors(colorbytes: Any, out: EmbPattern, values: Any) -> None:
    thread_set = get_thread_set()
    max_value = len(thread_set)
    for byte in colorbytes:
        thread_value = thread_set[byte % max_value]  # type: ignore
        out.add_thread(thread_value)  # type: ignore
        values.append(thread_value)  # type: ignore


def process_pec_table(colorbytes: Any, out: EmbPattern, chart: Any, values: Any) -> None:
    # This is how PEC actually allocates pre-defined threads to blocks.
    thread_set = get_thread_set()
    max_value = len(thread_set)
    thread_map: dict[int, Any] = {}
    for i in range(0, len(colorbytes)):  # type: ignore
        color_index = int(colorbytes[i] % max_value)  # type: ignore
        thread_value = thread_map.get(color_index, None)
        if thread_value is None:
            if len(chart) > 0:  # type: ignore
                thread_value = chart.pop(0)  # type: ignore
            else:
                thread_value = thread_set[color_index]
            thread_map[color_index] = thread_value
        out.add_thread(thread_value)  # type: ignore
        values.append(thread_value)  # type: ignore


def map_pec_colors(colorbytes: Any, out: EmbPattern, chart: Any, values: Any) -> None:
    if chart is None or len(chart) == 0:
        # Reading pec colors.
        process_pec_colors(colorbytes, out, values)

    elif len(chart) >= len(colorbytes):
        # Reading threads in 1 : 1 mode.
        for thread in chart:
            out.add_thread(thread)
            values.append(thread)
    else:
        # Reading tabled mode threads.
        process_pec_table(colorbytes, out, chart, values)


def signed12(b: Any) -> int:
    b &= 0xFFF  # type: ignore
    if b > 0x7FF:  # type: ignore
        return -0x1000 + b  # type: ignore
    else:
        return b  # type: ignore


def signed7(b: Any) -> int:
    if b > 63:  # type: ignore
        return -128 + b  # type: ignore
    else:
        return b  # type: ignore


def read_pec_stitches(f: BinaryIO, out: EmbPattern) -> None:
    while True:
        val1 = read_int_8(f)
        val2 = read_int_8(f)
        if val1 is None or val2 is None or (val1 == 0xFF and val2 == 0x00):
            break
        if val1 == 0xFE and val2 == 0xB0:
            f.seek(1, 1)
            out.color_change(0, 0)
            continue
        jump = False
        trim = False
        if val1 & FLAG_LONG != 0:  # type: ignore
            if val1 & TRIM_CODE != 0:  # type: ignore
                trim = True
            if val1 & JUMP_CODE != 0:  # type: ignore
                jump = True
            code = (val1 << 8) | val2  # type: ignore
            x = signed12(code)  # type: ignore
            val2 = read_int_8(f)
            if val2 is None:
                break
        else:
            x = signed7(val1)  # type: ignore

        if val2 & FLAG_LONG != 0:  # type: ignore
            if val2 & TRIM_CODE != 0:  # type: ignore
                trim = True
            if val2 & JUMP_CODE != 0:  # type: ignore
                jump = True
            val3 = read_int_8(f)
            if val3 is None:
                break
            code = val2 << 8 | val3  # type: ignore
            y = signed12(code)  # type: ignore
        else:
            y = signed7(val2)  # type: ignore
        if jump:
            out.move(x, y)  # type: ignore
        elif trim:
            out.trim()
            out.move(x, y)  # type: ignore
        else:
            out.stitch(x, y)  # type: ignore
    out.end()
