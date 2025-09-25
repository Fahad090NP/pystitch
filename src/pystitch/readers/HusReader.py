from typing import BinaryIO, Optional, Any

from ..utils.EmbCompress import expand
from ..core.EmbPattern import EmbPattern
from ..threads.EmbThreadHus import get_thread_set
from ..utils.ReadHelper import read_int_16le, read_int_32le, read_string_8, signed8, signed16


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    _ = read_int_32le(f)  # magic_code unused
    number_of_stitches = read_int_32le(f)
    number_of_colors = read_int_32le(f)

    extend_pos_x = read_int_16le(f)
    _ = signed16(extend_pos_x) if extend_pos_x is not None else None  # extend_pos_x unused
    extend_pos_y = read_int_16le(f)
    _ = signed16(extend_pos_y) if extend_pos_y is not None else None  # extend_pos_y unused
    extend_neg_x = read_int_16le(f)
    _ = signed16(extend_neg_x) if extend_neg_x is not None else None  # extend_neg_x unused
    extend_neg_y = read_int_16le(f)
    _ = signed16(extend_neg_y) if extend_neg_y is not None else None  # extend_neg_y unused

    command_offset = read_int_32le(f)
    x_offset = read_int_32le(f)
    y_offset = read_int_32le(f)

    _ = read_string_8(f, 8)  # string_value unused

    _ = read_int_16le(f)  # unknown_16_bit unused

    hus_thread_set = get_thread_set()
    if number_of_colors is not None:
        for i in range(0, number_of_colors):
            index = read_int_16le(f)
            if index is not None:
                out.add_thread(hus_thread_set[index])
    
    if command_offset is not None and x_offset is not None and y_offset is not None:
        f.seek(command_offset, 0)
        command_compressed = bytearray(f.read(x_offset - command_offset))
        f.seek(x_offset, 0)
        x_compressed = bytearray(f.read(y_offset - x_offset))
        f.seek(y_offset, 0)
        y_compressed = bytearray(f.read())

        if number_of_stitches is not None:
            command_decompressed = expand(command_compressed, number_of_stitches)
            x_decompressed = expand(x_compressed, number_of_stitches)
            y_decompressed = expand(y_compressed, number_of_stitches)

            stitch_count = min(
                len(command_decompressed), len(x_decompressed), len(y_decompressed)
            )

            for i in range(0, stitch_count):
                cmd = command_decompressed[i]
                x = signed8(x_decompressed[i])
                y = -signed8(y_decompressed[i])
                if cmd == 0x80:  # STITCH
                    out.stitch(x, y)
                elif cmd == 0x81:  # JUMP
                    out.move(x, y)
                elif cmd == 0x84:  # COLOR_CHANGE
                    out.color_change(x, y)
                elif cmd == 0x88:  # TRIM
                    if x != 0 or y != 0:
                        out.move(x, y)
                    out.trim()
                elif cmd == 0x90:  # END
                    break
                else:  # UNMAPPED COMMAND
                    break
    out.end()
