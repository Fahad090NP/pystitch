from math import floor

blank = [
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0xF0,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0F,
    0x08,
    0x00,
    0x00,
    0x00,
    0x00,
    0x10,
    0x04,
    0x00,
    0x00,
    0x00,
    0x00,
    0x20,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x40,
    0x04,
    0x00,
    0x00,
    0x00,
    0x00,
    0x20,
    0x08,
    0x00,
    0x00,
    0x00,
    0x00,
    0x10,
    0xF0,
    0xFF,
    0xFF,
    0xFF,
    0xFF,
    0x0F,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


def get_blank():
    return [m for m in blank]


from typing import List, Any

def create(width: int, height: int) -> List[int]:
    width_bytes = width // 8
    return [0x00] * width_bytes * height


def draw(points: List[Any], graphic: List[int], stride: int = 6) -> None:  # type: ignore[misc]
    for point in points:
        try:
            try:
                graphic_mark_bit(graphic, int(point.x), int(point.y), stride)  # type: ignore[misc]
            except AttributeError:
                graphic_mark_bit(graphic, int(point[0]), int(point[1]), stride)  # type: ignore[misc]
        except IndexError:
            pass


def draw_scaled(extends: Any, points: List[Any], graphic: List[int], stride: int, buffer: int = 5) -> None:  # type: ignore[misc]
    if extends is None:
        draw(points, graphic, stride)
        return
    try:
        left = extends.left
        top = extends.top
        right = extends.right
        bottom = extends.bottom
    except AttributeError:
        left = extends[0]
        top = extends[1]
        right = extends[2]
        bottom = extends[3]

    diagram_width = right - left
    diagram_height = bottom - top

    graphic_width = stride * 8
    graphic_height = len(graphic) / stride

    if diagram_width == 0:
        diagram_width = 1
    if diagram_height == 0:
        diagram_height = 1

    scale_x = (graphic_width - buffer) / float(diagram_width)
    scale_y = (graphic_height - buffer) / float(diagram_height)

    scale = min(scale_x, scale_y)

    cx = (right + left) / 2
    cy = (bottom + top) / 2

    translate_x = -cx
    translate_y = -cy

    translate_x *= scale
    translate_y *= scale

    translate_x += graphic_width / 2
    translate_y += graphic_height / 2

    for point in points:
        try:
            try:
                graphic_mark_bit(
                    graphic,
                    int(floor((point.x * scale) + translate_x)),  # type: ignore
                    int(floor((point.y * scale) + translate_y)),  # type: ignore
                    stride,
                )
            except AttributeError:
                graphic_mark_bit(
                    graphic,
                    int(floor((point[0] * scale) + translate_x)),  # type: ignore
                    int(floor((point[1] * scale) + translate_y)),  # type: ignore
                    stride,
                )
        except IndexError:
            pass


def clear(graphic) -> None:  # type: ignore
    for _ in graphic:  # type: ignore
        pass  # This function appears to be a no-op or placeholder


def graphic_mark_bit(graphic, x, y, stride: int = 6) -> None:  # type: ignore
    """expressly sets the bit in the give graphic object"""
    graphic[(y * stride) + int(x / 8)] |= 1 << (x % 8)  # type: ignore


def graphic_unmark_bit(graphic, x, y, stride: int = 6) -> None:  # type: ignore
    """expressly unsets the bit in the give graphic object"""
    graphic[(y * stride) + int(x / 8)] &= ~(1 << (x % 8))  # type: ignore


def get_graphic_as_string(graphic, one: str = "#", zero: str = " ") -> str:  # type: ignore
    """Prints graphic object in text."""
    stride = 6
    if isinstance(graphic, tuple):
        stride = graphic[1]  # type: ignore
        graphic = graphic[0]  # type: ignore

    if isinstance(graphic, str):
        graphic = bytearray(graphic, encoding='latin-1')  # type: ignore

    list_string = [
        one if (byte >> i) & 1 else zero for byte in graphic for i in range(0, 8)  # type: ignore
    ]
    bit_stride = 8 * stride  # type: ignore
    bit_length = 8 * len(graphic)  # type: ignore
    return "\n".join(
        "".join(list_string[m : m + bit_stride])  # type: ignore
        for m in range(0, bit_length, bit_stride)  # type: ignore
    )


__all__ = [
    'get_blank', 
    'create', 
    'draw', 
    'draw_scaled', 
    'clear', 
    'graphic_mark_bit', 
    'graphic_unmark_bit', 
    'get_graphic_as_string'
]
