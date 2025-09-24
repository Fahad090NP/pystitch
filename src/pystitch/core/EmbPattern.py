import os
from typing import Any, Dict, List, Union, Tuple, cast

from ..utils.EmbEncoder import Transcoder as Normalizer
from ..utils.EmbFunctions import encode_thread_change, decode_embroidery_command
from ..threads.EmbThread import EmbThread
from .EmbConstant import (
    COMMAND_MASK, NO_COMMAND, STITCH, JUMP, TRIM, STOP, END,
    COLOR_CHANGE, NEEDLE_SET, SEQUIN_MODE, SEQUIN_EJECT,
    SEW_TO, NEEDLE_AT, STITCH_BREAK, SEQUENCE_BREAK, COLOR_BREAK,
    MATRIX_TRANSLATE, MATRIX_SCALE, MATRIX_ROTATE, FRAME_EJECT
)


class EmbPattern:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Note: kwargs parameter is part of the interface but not currently used
        _ = kwargs  # Acknowledge parameter to avoid unused argument warning
        self.stitches: List[Any] = []
        self.threadlist: List[Any] = []
        self.extras: Dict[str, Any] = {}
        # filename, name, category, author, keywords, comments, are typical
        self._previousX: float = 0.0
        self._previousY: float = 0.0
        len_args = len(args)
        if len_args >= 1:
            arg0 = args[0]
            if isinstance(arg0, EmbPattern):
                self.stitches = arg0.stitches[:]
                self.threadlist = arg0.threadlist[:]
                self.extras.update(arg0.extras)
                self._previousX = arg0._previousX
                self._previousY = arg0._previousY
                return
            else:
                raise TypeError("expected first argument to be an EmbPattern")

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EmbPattern):
            return False
        if self.stitches != other.stitches:
            return False
        if self.threadlist != other.threadlist:
            return False
        if self.extras != other.extras:
            return False
        return True

    def __str__(self) -> str:
        if "name" in self.extras:
            return "EmbPattern %s (commands: %3d, threads: %3d)" % (
                self.extras["name"],
                len(self.stitches),
                len(self.threadlist),
            )
        return "EmbPattern (commands: %3d, threads: %3d)" % (
            len(self.stitches),
            len(self.threadlist),
        )

    def __len__(self) -> int:
        return len(self.stitches)

    def __getitem__(self, item: Any) -> Any:
        if isinstance(item, str):
            return self.extras[item]
        return self.stitches[item]

    def __setitem__(self, key: Any, value: Any) -> None:
        if isinstance(key, str):
            self.extras[key] = value
        else:
            self.stitches[key] = value

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo: Any) -> 'EmbPattern':
        return self.copy()

    def __iadd__(self, other: Any) -> 'EmbPattern':
        if isinstance(other, EmbPattern):
            self.add_pattern(other)
        elif isinstance(other, EmbThread) or isinstance(other, str):
            self.add_thread(other)
            for i in range(0, len(self.stitches)):
                data = self.stitches[i][2] & COMMAND_MASK
                if data == STITCH or data == SEW_TO or data == NEEDLE_AT:
                    self.color_change()
                    break  # Only add color change if stitching exists.
        elif isinstance(other, int):
            self.add_command(other)
        elif isinstance(other, (list, tuple)):  # tuple or list
            other_seq = cast(Union[List[Any], Tuple[Any, ...]], other)
            if len(other_seq) == 0:
                return self
            v = other_seq[0]
            if isinstance(v, (list, tuple)):  # tuple or list of tuple or lists
                for item in other_seq:
                    item_seq = cast(Union[List[Any], Tuple[Any, ...]], item)
                    x = cast(float, item_seq[0])
                    y = cast(float, item_seq[1])
                    try:
                        cmd = cast(int, item_seq[2])
                    except IndexError:
                        cmd = STITCH
                    self.add_stitch_absolute(cmd, x, y)
            elif isinstance(v, complex):  # tuple or list of complex
                for item in other_seq:
                    complex_item = cast(complex, item)
                    x = complex_item.real
                    y = complex_item.imag
                    self.add_stitch_absolute(STITCH, x, y)
            elif isinstance(v, (int, float)):  # tuple or list of numbers.
                i = 0
                ie = len(other_seq)
                while i < ie:
                    x = cast(float, other_seq[i])
                    y = cast(float, other_seq[i + 1])
                    self.add_stitch_absolute(STITCH, x, y)
                    i += 2
            elif isinstance(v, str):
                self.extras[v] = other[1]
        else:
            raise ValueError()
        return self

    def __add__(self, other: Any) -> 'EmbPattern':
        p = self.copy()
        p.add_pattern(other)
        return p

    def __radd__(self, other: Any) -> 'EmbPattern':
        p = other.copy()
        p.add_pattern(self)
        return p

    def copy(self) -> 'EmbPattern':
        emb_pattern = EmbPattern()
        emb_pattern.stitches = self.stitches[:]
        emb_pattern.threadlist = self.threadlist[:]
        emb_pattern.extras.update(self.extras)
        emb_pattern._previousX = self._previousX  # pyright: ignore[reportPrivateUsage]
        emb_pattern._previousY = self._previousY  # pyright: ignore[reportPrivateUsage]
        return emb_pattern

    def clear(self) -> None:
        self.stitches = []
        self.threadlist = []
        self.extras = {}
        self._previousX = 0
        self._previousY = 0

    def move(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Move dx, dy"""
        if position is None:
            self.add_stitch_relative(JUMP, dx, dy)
        else:
            self.insert_stitch_relative(position, JUMP, dx, dy)

    def move_abs(self, x: float, y: float, position: Any = None) -> None:
        """Move absolute x, y"""
        if position is None:
            self.add_stitch_absolute(JUMP, x, y)
        else:
            self.insert(position, JUMP, x, y)

    def stitch(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Stitch dx, dy"""
        if position is None:
            self.add_stitch_relative(STITCH, dx, dy)
        else:
            self.insert_stitch_relative(position, STITCH, dx, dy)

    def stitch_abs(self, x: float, y: float, position: Any = None) -> None:
        """Stitch absolute x, y"""
        if position is None:
            self.add_stitch_absolute(STITCH, x, y)
        else:
            self.insert(position, STITCH, x, y)

    def stop(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Stop dx, dy"""
        if position is None:
            self.add_stitch_relative(STOP, dx, dy)
        else:
            self.insert_stitch_relative(position, STOP, dx, dy)

    def trim(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Trim dx, dy"""
        if position is None:
            self.add_stitch_relative(TRIM, dx, dy)
        else:
            self.insert_stitch_relative(position, TRIM, dx, dy)

    def color_change(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Color Change dx, dy"""
        if position is None:
            self.add_stitch_relative(COLOR_CHANGE, dx, dy)
        else:
            self.insert_stitch_relative(position, COLOR_CHANGE, dx, dy)

    def needle_change(self, needle: int = 0, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Needle change, needle, dx, dy"""
        cmd = encode_thread_change(NEEDLE_SET, None, needle)
        if position is None:
            self.add_stitch_relative(cmd, dx, dy)
        else:
            self.insert_stitch_relative(position, cmd, dx, dy)

    def sequin_eject(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Eject Sequin dx, dy"""
        if position is None:
            self.add_stitch_relative(SEQUIN_EJECT, dx, dy)
        else:
            self.insert_stitch_relative(position, SEQUIN_EJECT, dx, dy)

    def sequin_mode(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """Eject Sequin dx, dy"""
        if position is None:
            self.add_stitch_relative(SEQUIN_MODE, dx, dy)
        else:
            self.insert_stitch_relative(position, SEQUIN_MODE, dx, dy)

    def end(self, dx: float = 0, dy: float = 0, position: Any = None) -> None:
        """End Design dx, dy"""
        if position is None:
            self.add_stitch_relative(END, dx, dy)
        else:
            self.insert_stitch_relative(position, END, dx, dy)

    def add_thread(self, thread: Any) -> None:
        """Adds thread to design.
        Note: this has no effect on stitching and can be done at any point."""
        if isinstance(thread, EmbThread):
            self.threadlist.append(thread)
        else:
            thread_object = EmbThread()
            thread_object.set(thread)  # type: ignore[misc]
            self.threadlist.append(thread_object)

    def metadata(self, name: str, data: Any) -> None:
        """Adds select metadata to design.
        Note: this has no effect on stitching and can be done at any point."""
        self.extras[name] = data

    def get_metadata(self, name: str, default: Any = None) -> Any:
        return self.extras.get(name, default)

    def bounds(self) -> tuple[float, float, float, float]:
        """Returns the bounds of the stitch data:
        min_x, min_y, max_x, max_y"""
        min_x = float("inf")
        min_y = float("inf")
        max_x = -float("inf")
        max_y = -float("inf")

        for stitch in self.stitches:
            if stitch[0] > max_x:
                max_x = stitch[0]
            if stitch[0] < min_x:
                min_x = stitch[0]
            if stitch[1] > max_y:
                max_y = stitch[1]
            if stitch[1] < min_y:
                min_y = stitch[1]
        return min_x, min_y, max_x, max_y

    extends = bounds
    extents = bounds

    def count_stitch_commands(self, command: int) -> int:
        count = 0
        for stitch in self.stitches:
            flags = stitch[2] & COMMAND_MASK
            if flags == command:
                count += 1
        return count

    def count_color_changes(self) -> int:
        return self.count_stitch_commands(COLOR_CHANGE)

    def count_needle_sets(self) -> int:
        return self.count_stitch_commands(NEEDLE_SET)

    def count_stitches(self) -> int:
        return len(self.stitches)

    def count_threads(self) -> int:
        return len(self.threadlist)

    @staticmethod
    def get_random_thread() -> EmbThread:
        thread = EmbThread()
        thread.set("random")  # type: ignore[misc]
        thread.description = "Random"
        return thread

    def get_thread_or_filler(self, index: int) -> EmbThread:
        if len(self.threadlist) <= index:
            return self.get_random_thread()
        else:
            return self.threadlist[index]

    def get_thread(self, index: int) -> EmbThread:
        return self.threadlist[index]

    def get_match_commands(self, command: int) -> Any:
        for stitch in self.stitches:
            flags = stitch[2] & COMMAND_MASK
            if flags == command:
                yield stitch

    def get_as_stitchblock(self) -> Any:
        stitchblock: List[Any] = []
        thread = self.get_thread_or_filler(0)
        thread_index = 1
        for stitch in self.stitches:
            flags = stitch[2] & COMMAND_MASK
            if flags == STITCH:
                stitchblock.append(stitch)
            else:
                if len(stitchblock) > 0:
                    yield (stitchblock, thread)
                    stitchblock = []
                if flags == COLOR_CHANGE:
                    thread = self.get_thread_or_filler(thread_index)
                    thread_index += 1
        if len(stitchblock) > 0:
            yield (stitchblock, thread)

    def get_as_command_blocks(self) -> Any:
        last_pos = 0
        last_command = NO_COMMAND
        for pos, stitch in enumerate(self.stitches):
            command = stitch[2] & COMMAND_MASK
            if command == last_command or last_command == NO_COMMAND:
                last_command = command
                continue
            last_command = command
            yield self.stitches[last_pos:pos]
            last_pos = pos
        yield self.stitches[last_pos:]

    def get_as_colorblocks(self) -> Any:
        """
        Returns a generator for colorblocks. Color blocks defined with color_breaks will have
        the command omitted whereas color blocks delimited with color_change will end with the
        color_change command, and if delimited with needle_set, the blocks will begin the new
        color block with the needle_set.
        """
        thread_index = 0
        colorblock_start = 0

        for pos, stitch in enumerate(self.stitches):
            command = stitch[2] & COMMAND_MASK
            if command == COLOR_BREAK:
                if colorblock_start != pos:
                    thread = self.get_thread_or_filler(thread_index)
                    thread_index += 1
                    yield self.stitches[colorblock_start:pos], thread
                colorblock_start = pos + 1
                continue
            if command == COLOR_CHANGE:
                thread = self.get_thread_or_filler(thread_index)
                thread_index += 1
                yield self.stitches[colorblock_start : pos + 1], thread
                colorblock_start = pos + 1
                continue
            if command == NEEDLE_SET and colorblock_start != pos:
                thread = self.get_thread_or_filler(thread_index)
                thread_index += 1
                yield self.stitches[colorblock_start:pos], thread
                colorblock_start = pos
                continue

        if colorblock_start != len(self.stitches):
            thread = self.get_thread_or_filler(thread_index)
            yield self.stitches[colorblock_start:], thread

    def get_as_stitches(self) -> Any:
        """pos, x, y, command, v1, v2, v3"""
        for pos, stitch in enumerate(self.stitches):
            decode = decode_embroidery_command(stitch[2])
            command = decode[0]
            thread = decode[1]
            needle = decode[2]
            order = decode[3]
            yield pos, stitch[0], stitch[1], command, thread, needle, order

    def get_unique_threadlist(self) -> set[Any]:
        return set(self.threadlist)

    def get_singleton_threadlist(self) -> List[Any]:
        singleton: List[Any] = []
        last_thread = None
        for thread in self.threadlist:
            if thread != last_thread:
                singleton.append(thread)
            last_thread = thread
        return singleton

    def move_center_to_origin(self) -> None:
        extends = self.bounds()
        cx = round((extends[2] + extends[0]) / 2.0)
        cy = round((extends[3] + extends[1]) / 2.0)
        self.translate(-cx, -cy)

    def translate(self, dx: float, dy: float) -> None:
        for stitch in self.stitches:
            stitch[0] += dx
            stitch[1] += dy

    def transform(self, matrix: Any) -> None:
        for stitch in self.stitches:
            matrix.apply(stitch)

    def fix_color_count(self) -> None:
        """Ensure that there are threads for all color blocks."""
        thread_index = 0
        init_color = True
        for stitch in self.stitches:
            data = stitch[2] & COMMAND_MASK
            if data == STITCH or data == SEW_TO or data == NEEDLE_AT:
                if init_color:
                    thread_index += 1
                    init_color = False
            elif data == COLOR_CHANGE or data == COLOR_BREAK or data == NEEDLE_SET:
                init_color = True
        while len(self.threadlist) < thread_index:
            self.add_thread(self.get_thread_or_filler(len(self.threadlist)))

    def add_stitch_absolute(self, cmd: int, x: float = 0, y: float = 0) -> None:
        """Add a command at the absolute location: x, y"""
        self.stitches.append([x, y, cmd])
        self._previousX = x
        self._previousY = y

    def add_stitch_relative(self, cmd: int, dx: float = 0, dy: float = 0) -> None:
        """Add a command relative to the previous location"""
        x = self._previousX + dx
        y = self._previousY + dy
        self.add_stitch_absolute(cmd, x, y)

    def insert_stitch_relative(self, position: Any, cmd: int, dx: float = 0, dy: float = 0) -> None:
        """Insert a relative stitch into the pattern. The stitch is relative to the stitch before it.
        If inserting at position 0, it's relative to 0,0. If appending, add is called, updating the positioning.
        """
        if position < 0:
            position += len(self.stitches)  # I need positive positions.
        if position == 0:
            self.stitches.insert(0, [dx, dy, cmd])  # started (0,0)
        elif (
            position == len(self.stitches) or position is None
        ):  # This is properly just an add.
            self.add_stitch_relative(cmd, dx, dy)
        elif 0 < position < len(self.stitches):
            p = self.stitches[position - 1]
            x = p[0] + dx
            y = p[1] + dy
            self.stitches.insert(position, [x, y, cmd])

    def insert(self, position: int, cmd: int, x: float = 0, y: float = 0) -> None:
        """Insert a stitch or command"""
        self.stitches.insert(position, [x, y, cmd])

    def prepend_command(self, cmd: int, x: float = 0, y: float = 0) -> None:
        """Prepend a command, without treating parameters as locations"""
        self.stitches.insert(0, [x, y, cmd])

    def add_command(self, cmd: int, x: float = 0, y: float = 0) -> None:
        """Add a command, without treating parameters as locations
        that require an update"""
        self.stitches.append([x, y, cmd])

    def add_block(self, block: Any, thread: Any = None) -> None:
        if thread is not None:
            self.add_thread(thread)
        if block is None:
            return

        if isinstance(block, (list, tuple)):
            block_seq = cast(Union[List[Any], Tuple[Any, ...]], block)
            if len(block_seq) == 0:
                return
            v = block_seq[0]
            if isinstance(v, (list, tuple)):
                for item in block_seq:
                    item_seq = cast(Union[List[Any], Tuple[Any, ...]], item)
                    x = cast(float, item_seq[0])
                    y = cast(float, item_seq[1])
                    try:
                        cmd = cast(int, item_seq[2])
                    except IndexError:
                        cmd = STITCH
                    self.add_stitch_absolute(cmd, x, y)
            elif isinstance(v, complex):
                for item in block_seq:
                    complex_item = cast(complex, item)
                    x = complex_item.real
                    y = complex_item.imag
                    self.add_stitch_absolute(STITCH, x, y)
            elif isinstance(v, (int, float)):
                i = 0
                ie = len(block_seq)
                while i < ie:
                    x = cast(float, block_seq[i])
                    y = cast(float, block_seq[i + 1])
                    self.add_stitch_absolute(STITCH, x, y)
                    i += 2
        self.add_command(COLOR_BREAK)

    def add_stitchblock(self, stitchblock: Any) -> None:
        threadlist = self.threadlist
        block = stitchblock[0]
        thread = stitchblock[1]
        if len(threadlist) == 0 or thread is not threadlist[-1]:
            threadlist.append(thread)
            self.add_stitch_relative(COLOR_BREAK)
        else:
            self.add_stitch_relative(SEQUENCE_BREAK)

        for stitch in block:
            try:
                self.add_stitch_absolute(stitch.command, stitch.x, stitch.y)
            except AttributeError:
                self.add_stitch_absolute(stitch[2], stitch[0], stitch[1])

    def add_pattern(self, pattern: Any, dx: Any = None, dy: Any = None, sx: Any = None, sy: Any = None, rotate: Any = None) -> None:
        """
        add_pattern merges the given pattern with the current pattern. It accounts for some edge conditions but
        not all of them.

        If there is an end command on the current pattern, that is removed.
        If the color ending the current pattern is equal to the color starting the next those color blocks are merged.
        Any prepended thread change command to the merging pattern is suppressed.

        :param pattern: pattern to add to current pattern
        :param dx: position change of the added pattern x
        :param dy: position change of the added pattern y
        :param sx: scale of the added pattern x
        :param sy: scale of the added pattern y
        :param rotate: rotation of the added pattern
        :return:
        """
        if isinstance(pattern, str):
            pattern = EmbPattern(pattern)
        if self.stitches[-1][2] == END:
            self.stitches = self.stitches[:-1]  # Remove END, if exists
        if dx is not None or dy is not None:
            if dx is None:
                dx = 0
            if dy is None:
                dy = 0
            self.add_command(MATRIX_TRANSLATE, dx, dy)
        if sx is not None or sx is not None:
            if sx is None:
                sx = sy
            if sy is None:
                sy = sx
            self.add_command(MATRIX_SCALE, sx, sy)
        if rotate is not None:
            self.add_command(MATRIX_ROTATE, rotate)
        # Add the new thread only if it's different from the last one
        self.fix_color_count()

        if len(pattern.threadlist) > 0:
            if pattern.threadlist[0] == self.threadlist[-1]:
                self.threadlist.extend(pattern.threadlist[1:])
            else:
                self.threadlist.extend(pattern.threadlist)
                self.color_change()
        join_position = len(self.stitches)
        self.stitches.extend(pattern.stitches)

        for i in range(join_position, len(self.stitches)):
            data = self.stitches[i][2] & COMMAND_MASK
            if data == STITCH or data == SEW_TO or data == NEEDLE_AT:
                break
            elif data == COLOR_CHANGE or data == COLOR_BREAK or data == NEEDLE_SET:
                self.stitches[i][2] = NO_COMMAND
        self.extras.update(pattern.extras)

    def interpolate_duplicate_color_as_stop(self) -> None:
        """Processes a pattern replacing any duplicate colors in the threadlist as a stop."""
        thread_index = 0
        init_color = True
        last_change = None
        for position, stitch in enumerate(self.stitches):
            data = stitch[2] & COMMAND_MASK
            if data == STITCH or data == SEW_TO or data == NEEDLE_AT:
                if init_color:
                    try:
                        if (
                            last_change is not None
                            and thread_index != 0
                            and self.threadlist[thread_index - 1]
                            == self.threadlist[thread_index]
                        ):
                            del self.threadlist[thread_index]
                            self.stitches[last_change][2] = STOP
                        else:
                            thread_index += 1
                    except IndexError:  # Non-existent threads cannot double
                        return
                    init_color = False
            elif data == COLOR_CHANGE or data == COLOR_BREAK or data == NEEDLE_SET:
                init_color = True
                last_change = position

    def interpolate_stop_as_duplicate_color(self, thread_change_command: int = COLOR_CHANGE) -> None:
        """Processes a pattern replacing any stop as a duplicate color, and color_change
        or another specified thread_change_command"""
        thread_index = 0
        for position, stitch in enumerate(self.stitches):
            data = stitch[2] & COMMAND_MASK
            if data == STITCH or data == SEW_TO or data == NEEDLE_AT:
                continue
            elif data == COLOR_CHANGE or data == COLOR_BREAK or data == NEEDLE_SET:
                thread_index += 1
            elif data == STOP:
                try:
                    self.threadlist.insert(thread_index, self.threadlist[thread_index])
                    self.stitches[position][2] = thread_change_command
                    thread_index += 1
                except IndexError:  # There are no colors to duplicate
                    return

    def interpolate_frame_eject(self) -> None:
        """Processes a pattern replacing jump-stop-jump/jump-stop-end sequences with FRAME_EJECT."""
        mode = 0
        stop_x = None
        stop_y = None
        sequence_start_position = None
        position = 0
        ie = len(self.stitches)
        while position < ie:
            stitch = self.stitches[position]
            data = stitch[2] & COMMAND_MASK
            if (
                data == STITCH
                or data == SEW_TO
                or data == NEEDLE_AT
                or data == COLOR_CHANGE
                or data == COLOR_BREAK
                or data == NEEDLE_SET
            ):
                if mode == 3 and sequence_start_position is not None:
                    del self.stitches[sequence_start_position:position]
                    position = sequence_start_position
                    self.stitches.insert(position, [stop_x, stop_y, FRAME_EJECT])
                    ie = len(self.stitches)
                mode = 0
            elif data == JUMP:
                if mode == 2:
                    mode = 3
                if mode == 0:
                    sequence_start_position = position
                    mode = 1
            elif data == STOP:
                if mode == 1:
                    mode = 2
                    stop_x = stitch[0]
                    stop_y = stitch[1]
            position += 1
        if mode >= 2 and sequence_start_position is not None:  # Frame_eject at end.
            del self.stitches[sequence_start_position:position]
            position = sequence_start_position
            self.stitches.insert(position, [stop_x, stop_y, FRAME_EJECT])

    def interpolate_trims(
        self, jumps_to_require_trim: Any = None, distance_to_require_trim: Any = None, clipping: bool = True
    ) -> None:
        """Processes a pattern adding trims according to the given criteria."""
        i = -1
        ie = len(self.stitches) - 1

        x = 0
        y = 0
        jump_count = 0
        jump_start = 0
        jump_dx = 0
        jump_dy = 0
        jumping = False
        trimmed = True
        while i < ie:
            i += 1
            stitch = self.stitches[i]
            dx = stitch[0] - x
            dy = stitch[1] - y
            x = stitch[0]
            y = stitch[1]
            command = stitch[2] & COMMAND_MASK
            if command == STITCH or command == SEQUIN_EJECT:
                trimmed = False
                jumping = False
            elif command == COLOR_CHANGE or command == NEEDLE_SET or command == TRIM:
                trimmed = True
                jumping = False
            if command == JUMP:
                if not jumping:
                    jump_dx = 0
                    jump_dy = 0
                    jump_count = 0
                    jump_start = i
                    jumping = True
                jump_count += 1
                jump_dx += dx
                jump_dy += dy
                if not trimmed:
                    if (
                        jump_count == jumps_to_require_trim
                        or distance_to_require_trim is not None
                        and (
                            abs(jump_dy) > distance_to_require_trim
                            or abs(jump_dx) > distance_to_require_trim
                        )
                    ):
                        self.trim(position=jump_start)
                        jump_start += 1  # We inserted a position, start jump has moved.
                        i += 1
                        ie += 1
                        trimmed = True
                if (
                    clipping and jump_dx == 0 and jump_dy == 0
                ):  # jump displacement is 0, clip trim command.
                    del self.stitches[jump_start : i + 1]
                    i = jump_start - 1
                    ie = len(self.stitches) - 1

    def get_pattern_interpolate_trim(self, jumps_to_require_trim: Any) -> 'EmbPattern':
        """Gets a processed pattern with untrimmed jumps merged
        and trims added if merged jumps are beyond the given value.
        The expectation is that it has core commands and not
        middle-level commands"""
        new_pattern = EmbPattern()
        i = -1
        ie = len(self.stitches) - 1
        count = 0
        trimmed = True
        while i < ie:
            i += 1
            stitch = self.stitches[i]
            command = stitch[2] & COMMAND_MASK
            if command == STITCH or command == SEQUIN_EJECT:
                trimmed = False
            elif command == COLOR_CHANGE or command == NEEDLE_SET or command == TRIM:
                trimmed = True
            if trimmed or stitch[2] != JUMP:
                new_pattern.add_stitch_absolute(stitch[2], stitch[0], stitch[1])
                continue
            while i < ie and command == JUMP:
                i += 1
                stitch = self.stitches[i]
                command = stitch[2]
                count += 1
            if command != JUMP:
                i -= 1
            stitch = self.stitches[i]
            if count >= jumps_to_require_trim:
                new_pattern.trim()
            count = 0
            new_pattern.add_stitch_absolute(stitch[2], stitch[0], stitch[1])
        new_pattern.threadlist.extend(self.threadlist)
        new_pattern.extras.update(self.extras)
        return new_pattern

    def get_pattern_merge_jumps(self) -> 'EmbPattern':
        """Returns a pattern with all multiple jumps merged."""
        new_pattern = EmbPattern()
        i = -1
        ie = len(self.stitches) - 1
        stitch_break = False
        while i < ie:
            i += 1
            stitch = self.stitches[i]
            command = stitch[2] & COMMAND_MASK
            if command == JUMP:
                if stitch_break:
                    continue
                new_pattern.add_command(STITCH_BREAK)
                stitch_break = True
                continue
            new_pattern.add_stitch_absolute(stitch[2], stitch[0], stitch[1])
        new_pattern.threadlist.extend(self.threadlist)
        new_pattern.extras.update(self.extras)
        return new_pattern

    def get_stable_pattern(self) -> 'EmbPattern':
        """Gets a stabilized version of the pattern."""
        stable_pattern = EmbPattern()
        for stitchblock in self.get_as_stitchblock():
            stable_pattern.add_stitchblock(stitchblock)
        stable_pattern.extras.update(self.extras)
        return stable_pattern

    def get_normalized_pattern(self, encode_settings: Any = None) -> 'EmbPattern':
        """Encodes pattern typically for saving."""
        normal_pattern = EmbPattern()
        transcoder = Normalizer(encode_settings)
        transcoder.transcode(self, normal_pattern)
        return normal_pattern

    def append_translation(self, x: float, y: float) -> None:
        """Appends translation to the pattern.
        All commands will be translated by the given amount,
        including absolute location commands."""
        self.add_stitch_relative(MATRIX_TRANSLATE, x, y)

    @staticmethod
    def get_extension_by_filename(filename: str) -> str:
        """extracts the extension from a filename"""
        return os.path.splitext(filename)[1][1:]

    @staticmethod
    def read_embroidery(reader: Any, f: Any, settings: Any = None, pattern: Any = None) -> Any:
        """Reads fileobject or filename with reader."""
        if reader is None:
            return None
        if pattern is None:
            pattern = EmbPattern()

        if isinstance(f, str):
            text_mode = False
            try:
                text_mode = reader.READ_FILE_IN_TEXT_MODE
            except AttributeError:
                pass
            if text_mode:
                try:
                    with open(f, "r", encoding='utf-8', errors='ignore') as stream:
                        reader.read(stream, pattern, settings)
                        stream.close()
                except IOError:
                    pass
            else:
                with open(f, "rb") as stream:
                    reader.read(stream, pattern, settings)
        else:
            reader.read(f, pattern, settings)
        return pattern


    @staticmethod
    def write_embroidery(writer: Any, pattern: Any, stream: Any, settings: Any = None) -> None:
        if pattern is None:
            return
        if settings is None:
            settings = {}
        else:
            settings = settings.copy()
        try:
            encode = writer.ENCODE
        except AttributeError:
            encode = True

        if settings.get("encode", encode):
            if not ("max_jump" in settings):
                try:
                    settings["max_jump"] = writer.MAX_JUMP_DISTANCE
                except AttributeError:
                    pass
            if not ("max_stitch" in settings):
                try:
                    settings["max_stitch"] = writer.MAX_STITCH_DISTANCE
                except AttributeError:
                    pass
            if not ("full_jump" in settings):
                try:
                    settings["full_jump"] = writer.FULL_JUMP
                except AttributeError:
                    pass
            if not ("round" in settings):
                try:
                    settings["round"] = writer.ROUND
                except AttributeError:
                    pass
            if not ("writes_speeds" in settings):
                try:
                    settings["writes_speeds"] = writer.WRITES_SPEEDS
                except AttributeError:
                    pass
            if not ("sequin_contingency" in settings):
                try:
                    settings["sequin_contingency"] = writer.SEQUIN_CONTINGENCY
                except AttributeError:
                    pass
            if not ("thread_change_command" in settings):
                try:
                    settings["thread_change_command"] = writer.THREAD_CHANGE_COMMAND
                except AttributeError:
                    pass
            if not ("explicit_trim" in settings):
                try:
                    settings["explicit_trim"] = writer.EXPLICIT_TRIM
                except AttributeError:
                    pass
            if not ("translate" in settings):
                try:
                    settings["translate"] = writer.TRANSLATE
                except AttributeError:
                    pass
            if not ("scale" in settings):
                try:
                    settings["scale"] = writer.SCALE
                except AttributeError:
                    pass
            if not ("rotate" in settings):
                try:
                    settings["rotate"] = writer.ROTATE
                except AttributeError:
                    pass
            pattern = pattern.get_normalized_pattern(settings)

        if isinstance(stream, str):
            text_mode = False
            try:
                text_mode = writer.WRITE_FILE_IN_TEXT_MODE
            except AttributeError:
                pass
            if text_mode:
                with open(stream, "w", encoding='utf-8') as stream:
                    writer.write(pattern, stream, settings)
            else:
                with open(stream, "wb") as stream:
                    writer.write(pattern, stream, settings)
        else:
            writer.write(pattern, stream, settings)
