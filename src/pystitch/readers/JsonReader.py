from typing import BinaryIO, Optional, Any

from ..utils.EmbFunctions import get_command_dictionary
from ..core.EmbPattern import EmbPattern
from ..threads.EmbThread import EmbThread


def decoded_command(command_dict: Any, name: Any) -> Any:
    split = name.split(" ")  # type: ignore
    command = command_dict[split[0]]  # type: ignore
    for sp in split[1:]:  # type: ignore
        if sp[0] == "n":  # type: ignore
            needle = int(sp[1:])  # type: ignore
            command |= (needle + 1) << 16  # type: ignore
        if sp[0] == "o":  # type: ignore
            order = int(sp[1:])  # type: ignore
            command |= (order + 1) << 24  # type: ignore
        if sp[0] == "t":  # type: ignore
            thread = int(sp[1:])  # type: ignore
            command |= (thread + 1) << 8  # type: ignore
    return command  # type: ignore


def read(f: BinaryIO, out: EmbPattern, settings: Optional[Any] = None) -> None:
    import json

    json_object = json.load(f)  # type: ignore
    command_dict = get_command_dictionary()
    stitches = json_object["stitches"]  # type: ignore
    extras = json_object["extras"]  # type: ignore
    threadlist = json_object["threadlist"]  # type: ignore
    for t in threadlist:  # type: ignore
        color = t["color"]  # type: ignore
        thread = EmbThread(color)  # type: ignore
        thread.description = t["description"]  # type: ignore
        thread.catalog_number = t["catalog_number"]  # type: ignore
        thread.details = t["details"]  # type: ignore
        thread.brand = t["brand"]  # type: ignore
        thread.chart = t["chart"]  # type: ignore
        thread.weight = t["weight"]  # type: ignore
        out.add_thread(thread)  # type: ignore
    for s in stitches:  # type: ignore
        out.stitches.append([s[0], s[1], decoded_command(command_dict, s[2])])  # type: ignore
    out.extras.update(extras)  # type: ignore
