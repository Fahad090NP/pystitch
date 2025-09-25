from typing import BinaryIO, Optional, Any

from ..core.EmbPattern import EmbPattern
from ..utils.ReadHelper import read_int_8, read_int_16be, read_int_24be, signed24

PC_SIZE_CONVERSION_RATIO = 5.0 / 3.0


def read_pc_file(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    pcm_threads: list[dict[str, int | str]] = [
        {"color": 0x000000, "description": "PCM Color 1"},
        {"color": 0x000080, "description": "PCM Color 2"},
        {"color": 0x0000FF, "description": "PCM Color 3"},
        {"color": 0x008080, "description": "PCM Color 4"},
        {"color": 0x00FFFF, "description": "PCM Color 5"},
        {"color": 0x800080, "description": "PCM Color 6"},
        {"color": 0xFF00FF, "description": "PCM Color 7"},
        {"color": 0x800000, "description": "PCM Color 8"},
        {"color": 0xFF0000, "description": "PCM Color 9"},
        {"color": 0x008000, "description": "PCM Color 10"},
        {"color": 0x00FF00, "description": "PCM Color 11"},
        {"color": 0x808000, "description": "PCM Color 12"},
        {"color": 0xFFFF00, "description": "PCM Color 13"},
        {"color": 0x808080, "description": "PCM Color 14"},
        {"color": 0xC0C0C0, "description": "PCM Color 15"},
        {"color": 0xFFFFFF, "description": "PCM Color 16"},
    ]

    f.seek(2, 0)

    colors = read_int_16be(f)
    if colors is None:
        return  # File is blank.
    for _ in range(0, colors):
        color_index = read_int_16be(f)
        if color_index is not None:
            thread = pcm_threads[color_index % len(pcm_threads)]
            out.add_thread(thread)

    _stitch_count = read_int_16be(f)
    while True:
        x_val = read_int_24be(f)
        _c0 = read_int_8(f)
        y_val = read_int_24be(f)
        _c1 = read_int_8(f)
        ctrl = read_int_8(f)
        if ctrl is None or x_val is None or y_val is None:
            break
        x = signed24(x_val)  # type: ignore
        y = -signed24(y_val)  # type: ignore
        x *= PC_SIZE_CONVERSION_RATIO  # type: ignore
        y *= PC_SIZE_CONVERSION_RATIO  # type: ignore
        if ctrl == 0x00:
            out.stitch_abs(x, y)  # type: ignore
            continue
        if ctrl & 0x01:
            out.color_change()
            continue
        if ctrl & 0x04:
            out.move_abs(x, y)  # type: ignore
            continue
        break  # Uncaught Control
    out.end()


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    read_pc_file(f, out)
