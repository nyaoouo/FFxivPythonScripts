import ctypes
import functools
import struct
import typing

if typing.TYPE_CHECKING:
    from fps.utils.sqpack import SqPack


def inc_ptr(ptr: 'ctypes.pointer', n):
    return ctypes.cast(ctypes.cast(ptr, ctypes.c_void_p).value + n * ctypes.sizeof(ptr._type_), type(ptr))


def bisect_utf16(v, buf: 'ctypes.pointer[ctypes.c_uint16]', left, right):
    while left < right:
        mid = (left + right) // 2
        t = buf[mid]
        if t < v:
            left = mid + 1
        else:
            right = mid
    t = buf[left]
    if t != v: raise StopIteration
    return left


class VulgarNode(ctypes.Structure):
    _fields_ = [
        ('mode', ctypes.c_uint32),
        ('size', ctypes.c_uint32),
        ('chain', ctypes.c_uint32),
        ('offset', ctypes.c_uint32),
    ]


class VulgarMap(ctypes.Structure):
    header: 'VulgarHeader'
    idx: int
    _pack_ = 1
    _fields_ = [
        ('unicode_map_offset', ctypes.c_uint32),
        ('chain_node_offset', ctypes.c_uint32),
        ('single_char_offset', ctypes.c_uint32),
        ('string_offset', ctypes.c_uint32),
        ('nodes_offset', ctypes.c_uint32),
        ('unk1', ctypes.c_uint32),
        ('unk2', ctypes.c_uint32),
        ('unk3', ctypes.c_uint32),
        ('unk4', ctypes.c_uint32),
        ('unk5', ctypes.c_uint32),
        ('use_replace', ctypes.c_uint32),
        ('unicode_map_high', ctypes.c_uint16 * 256),
    ]

    _a_data = property(lambda self: ctypes.addressof(self) + ctypes.sizeof(self))

    @functools.cached_property
    def p_unicode_map(self):
        return ctypes.cast(self._a_data + self.unicode_map_offset, ctypes.POINTER(ctypes.c_uint16))

    @functools.cached_property
    def p_chain_node(self):
        return ctypes.cast(self._a_data + self.chain_node_offset, ctypes.POINTER(ctypes.c_uint16))

    @functools.cached_property
    def p_single_char(self):
        return ctypes.cast(self._a_data + self.single_char_offset, ctypes.POINTER(ctypes.c_uint16))

    @functools.cached_property
    def p_string(self):
        return ctypes.cast(self._a_data + self.string_offset, ctypes.POINTER(ctypes.c_uint16))

    @functools.cached_property
    def p_nodes(self):
        return ctypes.cast(self._a_data + self.nodes_offset, ctypes.POINTER(VulgarNode))

    def _find_node(self, node: VulgarNode, buf: 'ctypes.pointer[ctypes.c_uint16]', size):
        next_node_idx: int
        match node.mode:
            case 0:
                if (single_char := inc_ptr(self.p_single_char, node.offset // 2))[0] == 0: return 0
                i = 0
                while True:
                    code_src: int = buf[i]
                    if not (code_src and self.header.is_unicode_ignore(code_src)): break
                    i += 1
                    if i >= size: raise StopIteration
                if self.use_replace:
                    code_src = self.header.get_unicode_replace(code_src)
                j = bisect_utf16(code_src, single_char, 0, node.size - 1)
                if node.chain and (next_node_idx := self.p_chain_node[node.chain + j]):
                    i += self._find_node(self.p_nodes[next_node_idx], inc_ptr(buf, i + 1), size - i - 1)
                return i + 1
            case 1:
                p_dst = inc_ptr(self.p_string, node.offset // 2)
                i = j = 0
                while code_dst := p_dst[j]:
                    if self.header.is_unicode_ignore(code_src := buf[i]):
                        i += 1
                        continue
                    if i >= size or not self.same_code(code_src, code_dst): raise StopIteration
                    i += 1
                    j += 1
                if node.chain and (next_node_idx := self.p_chain_node[node.chain]):
                    i += self._find_node(self.p_nodes[next_node_idx], inc_ptr(buf, i), size - i)
                return i
            case _:
                raise ValueError(f'Unknown mode: {node.mode}')

    def _find(self, buf: 'ctypes.pointer[ctypes.c_uint16]', size):
        first_code = buf[0]
        if self.use_replace:
            first_code = self.header.get_unicode_replace(first_code)
        if not (key := self.unicode_map_high[first_code >> 8]):
            return -1
        if not (node_idx := self.p_unicode_map[(key << 8) | (first_code & 0xff)]):
            return -1
        try:
            return self._find_node(self.p_nodes[node_idx], inc_ptr(buf, 1), size - 1)
        except StopIteration:
            return -1

    def _replace(self, buf: 'ctypes.pointer[ctypes.c_uint16]', size, replacement: int):
        if self.idx >= 3: return 1
        check_buf = (ctypes.c_uint16 * size)()
        p_check_buf = ctypes.cast(check_buf, ctypes.POINTER(ctypes.c_uint16))
        ctypes.memmove(p_check_buf, buf, size * ctypes.sizeof(ctypes.c_uint16))
        i = 0
        while i < size:
            code = check_buf[i]
            if self.header.is_unicode_ignore(code):
                i += 1
                continue
            if self.idx == 2 and (res := self.header._find(4, inc_ptr(p_check_buf, i), size - i)) != -1:
                i += res
                continue
            if (res := self._find(inc_ptr(p_check_buf, i), size - i)) == -1:
                i += 1
                continue
            if self.idx == 2: return 0
            res += 1
            for j in range(i, i + res):
                buf[j] = replacement
            i += res
        return 0

    @classmethod
    def from_header(cls, header: 'VulgarHeader', idx: int):
        if header.map_offsets[idx] == 0: return None
        obj = cls.from_address(ctypes.addressof(header) + header.map_offsets[idx])
        obj.header = header
        obj.idx = idx
        return obj

    def same_code(self, c1, c2):
        if self.use_replace:
            c1 = self.header.get_unicode_replace(c1)
            c2 = self.header.get_unicode_replace(c2)
        return c1 == c2

    def iter_node(self, node: VulgarNode):
        match node.mode:
            case 0:
                if (single_char := inc_ptr(self.p_single_char, node.offset // 2))[0] == 0: return
                for i in range(node.size):
                    if node.chain and (next_node_idx := self.p_chain_node[node.chain + i]):
                        for prefix in self.iter_node(self.p_nodes[next_node_idx]):
                            yield chr(single_char[i]) + prefix
                    else:
                        yield chr(single_char[i])
            case 1:
                p_dst = inc_ptr(self.p_string, node.offset // 2)
                end = 0
                while p_dst[end]: end += 1
                string = struct.pack(f'{end}H', *p_dst[:end]).decode('utf-16')
                if node.chain and (next_node_idx := self.p_chain_node[node.chain]):
                    for prefix in self.iter_node(self.p_nodes[next_node_idx]):
                        yield string + prefix
                else:
                    yield string
            case _:
                raise ValueError(f'Unknown mode: {node.mode}')

    def iter(self):
        for high in range(256):
            if not (key := self.unicode_map_high[high]): continue
            for low in range(256):
                if not (node_idx := self.p_unicode_map[(key << 8) | low]): continue
                first = chr((high << 8) | low)
                for prefix in self.iter_node(self.p_nodes[node_idx]):
                    yield first + prefix


class VulgarHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('unk1', ctypes.c_uint32),
        ('replacement', ctypes.c_uint32),
        ('unk2', ctypes.c_uint32),
        ('unicode_ignore_map', ctypes.c_uint32 * 8192),
        ('unicode_replace_high_map', ctypes.c_uint8 * 256),
        ('unk3', ctypes.c_uint32),
        ('map_offsets', ctypes.c_uint32 * 5),
    ]

    def _find(self, idx: int, buf: 'ctypes.pointer[ctypes.c_uint16]', size):
        if not (v_map := self.get_map(idx)): return -1
        return v_map.find(buf, size)

    def _replace(self, buf: ctypes.POINTER(ctypes.c_uint16), size, replacement: int):
        for i in range(3):
            if v_map := self.get_map(i):
                v_map._replace(buf, size, replacement)

    def replace(self, string: str, replacement: str | int = None):
        if replacement is None:
            replacement = self.replacement
        elif isinstance(replacement, str):
            replacement = ord(replacement)
        raw = string.encode('utf-16') + b'\0\0'
        size = len(raw) // 2
        buf = (ctypes.c_uint16 * size).from_buffer_copy(raw)
        self._replace(ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint16)), size, replacement)
        return struct.pack(f'{size}H', *buf).decode('utf-16')[:-1]

    @functools.cached_property
    def replacement_map(self):
        return ctypes.cast(ctypes.addressof(self) + ctypes.sizeof(self), ctypes.POINTER(ctypes.c_uint16))

    def get_map(self, index) -> VulgarMap:
        if '_map_cache' not in self.__dict__:
            self._map_cache = [VulgarMap.from_header(self, i) for i in range(5)]
        return self._map_cache[index]

    def is_unicode_ignore(self, code: int):
        if code == 0x20 or code == 0xa or code == 0xd: return True
        return self.unicode_ignore_map[code >> 5] & (1 << (code & 0x1f))

    def get_unicode_replace(self, code: int):
        if not (idx := self.unicode_replace_high_map[code >> 8]): return code
        return self.replacement_map[((idx - 1) << 8) | (code & 0xff)]

    @classmethod
    def from_sqpack(cls, sqpack: 'SqPack'):
        return VulgarHeader.from_buffer(sqpack.get_file("common/VulgarWordsFilter.dic").data_buffer)

    @classmethod
    def from_sqpack_party(cls, sqpack: 'SqPack'):
        return VulgarHeader.from_buffer(sqpack.get_file("common/VulgarWordsFilter_party.dic").data_buffer)

    def words(self):
        return self.get_map(0).iter()


def test():
    from fps.utils.sqpack import SqPack
    sqpack = SqPack(r'D:\game\ff14_sd\game')
    vug = VulgarHeader.from_sqpack_party(sqpack)
    # vug = VulgarHeader.from_sqpack(sqpack)
    print(vug.replace('魔大./陆练习生', '*'))
    # for word in vug.words(): print(word)


if __name__ == '__main__':
    test()
