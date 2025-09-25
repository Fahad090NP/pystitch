from typing import Optional, List, Union

def expand(data: Union[bytes, bytearray], uncompressed_size: Optional[int] = None) -> bytearray:
    emb_compress = EmbCompress()
    return emb_compress.decompress(data, uncompressed_size)


def compress(data: Union[bytes, bytearray]) -> bytearray:
    size = len(data)
    return (
        bytearray([(size >> 0) & 0xFF, (size >> 8) & 0xFF, 0x02, 0xA0, 0x01, 0xFE])
        + data
    )


class Huffman:
    def __init__(self, lengths: Optional[List[int]] = None, value: int = 0) -> None:
        self.default_value = value
        self.lengths = lengths
        self.table: Optional[List[int]] = None
        self.table_width = 0

    def build_table(self) -> None:
        """Build an index huffman table based on the lengths. lowest index value wins in a tie."""
        if self.lengths is None:
            return
        self.table_width = max(self.lengths)
        self.table = []
        size = 1 << self.table_width
        for bit_length in range(1, self.table_width + 1):
            size /= 2.0
            for len_index in range(0, len(self.lengths)):
                length = self.lengths[len_index]
                if length == bit_length:
                    self.table += [len_index] * int(size)

    def lookup(self, byte_lookup: int) -> tuple[int, int]:
        """lookup into the index, returns value and length
        must be requested with 2 bytes."""
        if self.table is None:
            return self.default_value, 0
        v = self.table[byte_lookup >> (16 - self.table_width)]
        return v, self.lengths[v]  # type: ignore


class EmbCompress:
    def __init__(self) -> None:
        self.bit_position = 0
        self.input_data: Optional[Union[bytes, bytearray]] = None
        self.block_elements: Optional[int] = None
        self.character_huffman: Optional[Huffman] = None
        self.distance_huffman: Optional[Huffman] = None

    def get_bits(self, start_pos_in_bits: int, length: int) -> int:
        end_pos_in_bits = start_pos_in_bits + length - 1
        start_pos_in_bytes = int(start_pos_in_bits / 8)
        end_pos_in_bytes = int(end_pos_in_bits / 8)
        value = 0
        for i in range(start_pos_in_bytes, end_pos_in_bytes + 1):
            value <<= 8
            try:
                if self.input_data is not None:
                    value |= self.input_data[i] & 0xFF
            except (IndexError, TypeError):
                pass
        unused_bits_right_of_sample = (8 - (end_pos_in_bits + 1) % 8) % 8
        mask_sample_bits = (1 << length) - 1
        original = (value >> unused_bits_right_of_sample) & mask_sample_bits
        return original

    def pop(self, bit_count: int) -> int:
        value = self.peek(bit_count)
        self.slide(bit_count)
        return value

    def peek(self, bit_count: int) -> int:
        return self.get_bits(self.bit_position, bit_count)

    def slide(self, bit_count: int) -> None:
        self.bit_position += bit_count

    def read_variable_length(self):
        m = self.pop(3)
        if m != 7:
            return m
        for _ in range(
            0, 13
        ):  # max read is 16 bit, 3 bits already used. It can't exceed 16-3
            s = self.pop(1)
            if s == 1:
                m += 1
            else:
                break
        return m

    def load_character_length_huffman(self):
        count = self.pop(5)
        if count == 0:
            v = self.pop(5)
            huffman = Huffman(value=v)
        else:
            huffman_code_lengths = [0] * count
            index = 0
            while index < count:
                if index == 3:  # Special index 3, skip up to 3 elements.
                    index += self.pop(2)
                huffman_code_lengths[index] = self.read_variable_length()
                index += 1
            huffman = Huffman(huffman_code_lengths, 8)
            huffman.build_table()
        return huffman

    def load_character_huffman(self, length_huffman: 'Huffman') -> 'Huffman':
        count = self.pop(9)
        if count == 0:
            v = self.pop(9)
            huffman = Huffman(value=v)
        else:
            huffman_code_lengths = [0] * count
            index = 0
            while index < count:
                h = length_huffman.lookup(self.peek(16))  # type: ignore
                c = h[0]  # type: ignore
                self.slide(h[1])  # type: ignore
                if c == 0:  # C == 0, skip 1.
                    c = 1
                    index += c
                elif c == 1:  # C == 1, skip 3 + read(4)
                    c = 3 + self.pop(4)
                    index += c
                elif c == 2:  # C == 2, skip 20 + read(9)
                    c = 20 + self.pop(9)
                    index += c
                else:
                    c -= 2  # type: ignore
                    huffman_code_lengths[index] = c
                    index += 1
            huffman = Huffman(huffman_code_lengths)
            huffman.build_table()
        return huffman

    def load_distance_huffman(self):
        count = self.pop(5)
        if count == 0:
            v = self.pop(5)
            huffman = Huffman(value=v)
        else:
            index = 0
            lengths = [0] * count
            for _ in range(0, count):
                lengths[index] = self.read_variable_length()
                index += 1
            huffman = Huffman(lengths)
            huffman.build_table()
        return huffman

    def load_block(self):
        self.block_elements = self.pop(16)
        character_length_huffman = self.load_character_length_huffman()
        self.character_huffman = self.load_character_huffman(character_length_huffman)  # type: ignore
        self.distance_huffman = self.load_distance_huffman()

    def get_token(self) -> int:
        if self.block_elements <= 0:  # type: ignore
            self.load_block()
        self.block_elements -= 1  # type: ignore
        h = self.character_huffman.lookup(self.peek(16))  # type: ignore
        self.slide(h[1])  # type: ignore
        return h[0]  # type: ignore

    def get_position(self) -> int:
        h = self.distance_huffman.lookup(self.peek(16))  # type: ignore
        self.slide(h[1])  # type: ignore
        if h[0] == 0:  # type: ignore
            return 0
        v = h[0] - 1  # type: ignore
        v = (1 << v) + self.pop(v)  # type: ignore
        return v  # type: ignore

    def decompress(self, input_data: Union[bytes, bytearray], uncompressed_size: Optional[int] = None) -> bytearray:  # type: ignore[misc]
        self.input_data = input_data
        output_data: List[int] = []
        self.block_elements = -1
        bits_total = len(input_data) * 8
        while bits_total > self.bit_position and (
            uncompressed_size is None or len(output_data) <= uncompressed_size
        ):
            character = self.get_token()
            if character <= 255:  # literal.
                output_data.append(character)  # type: ignore
            elif character == 510:
                break  # END
            else:
                length = character - 253  # Min length is 3. 256-253=3.  # type: ignore
                back = self.get_position() + 1
                position = len(output_data) - back  # type: ignore
                if back > length:  # type: ignore
                    # Entire lookback is already within output data.
                    output_data += output_data[position : position + length]  # type: ignore
                else:
                    # Will read & write the same data at some point.
                    for i in range(position, position + length):  # type: ignore
                        output_data.append(output_data[i])
        return bytearray(output_data)


__all__ = ['expand', 'compress', 'Huffman', 'EmbCompress']
