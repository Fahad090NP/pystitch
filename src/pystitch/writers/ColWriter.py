from typing import BinaryIO, Optional, Dict, Any
from ..core.EmbPattern import EmbPattern
from ..utils.WriteHelper import write_string_utf8

ENCODE = False


def write(pattern: EmbPattern, f: BinaryIO, settings: Optional[Dict[str, Any]] = None) -> None:
    write_string_utf8(f, "%d\r\n" % len(pattern.threadlist))
    index = 0
    for thread in pattern.threadlist:
        write_string_utf8(
            f,
            "%d,%d,%d,%d\r\n"
            % (index, thread.get_red(), thread.get_green(), thread.get_blue()),
        )
        index += 1
