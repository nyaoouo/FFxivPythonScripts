import zlib
from pathlib import Path
from typing import IO, Type, TYPE_CHECKING
from .structure import *

if TYPE_CHECKING:
    from .. import Pack


def compute_hash_32(s: str | bytes):
    if isinstance(s, str): s = s.encode('utf-8')
    return ~zlib.crc32(s.lower()) & 0xFFFFFFFF


class FileInfo:
    def __init__(self, _dir: 'Directory', info: HashTableElem_Hash64 | HashTableElem_Hash32):
        self.dir = _dir
        self.info = info
        self.offset = self.info.block_offset << 7
        self.key = info.hash_hoge
        if _dir.index.is_index1:
            self.hash = self.key & 0xFFFFFFFF
        else:
            self.hash = self.key
            self.key &= _dir.hash << 32
        self._name = b'file_hash_%d' % self.hash
        self.full_path = b'%s/file_hash_%d' % (self.dir.path, self.hash)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str | bytes):
        if isinstance(name, str): name = name.encode('utf-8')
        self._name = name
        self.full_path = b'%s/%s' % (self.dir.path, name)

    def __repr__(self):
        return f'FileIndex({self.full_path})'

    def __hash__(self):
        return self.key

    def __eq__(self, other):
        if isinstance(other, FileInfo): return other.key == self.key
        return self.key == other


class Directory:
    files: dict[int, FileInfo] = {}

    def __init__(self, index: 'Index', info: DirectoryIndexInfo):
        self.index = index
        self.info = info
        self.hash = info.dir_hash
        self._path = b'dir_hash_%d' % self.hash

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str | bytes):
        if isinstance(path, str):
            path = path.encode('utf-8')
        if path != self._path:
            self._path = path
            for file in self.files.values():
                file.full_path = b'%s/%s' % (path, file.name)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if isinstance(other, Directory): return other.hash == self.hash
        if isinstance(other, int): return other == self.hash
        return False

    def __repr__(self):
        return f'Directory({self._path.decode()})'

    def build_files(self, stream: IO[bytes], index_data_type: Type[HashTableElem_Hash64 | HashTableElem_Hash32], start_pos=0):
        if not self.info.size: return
        stream.seek(start_pos + self.info.offset)
        el_size = index_data_type._size_
        self.files = {}
        for _ in range(self.info.size // el_size):
            file = FileInfo(self, ctype.cdata_from_buffer_copy(stream.read(el_size), index_data_type))
            self.files[file.hash] = file
        return self

    def get_file(self, name_or_hash: str | bytes | int) -> FileInfo:
        if isinstance(name_or_hash, int):
            return self.files[name_or_hash]
        if isinstance(name_or_hash, str):
            name_or_hash = name_or_hash.encode('utf-8')
        file = self.files[compute_hash_32(name_or_hash)]
        file.name = name_or_hash
        return file


class Index:
    """
    Class representing the data inside a *.index file.
    """
    synonyms: dict[int, SynonymTableElem_Hash32 | SynonymTableElem_Hash64] = {}
    dirs: dict[int, Directory] = {}
    files: dict[int, FileInfo] = {}

    def __init__(self,pack:'Pack', path_or_stream: IO[bytes] | str | Path):
        self.pack = pack
        if isinstance(path_or_stream, (str, Path)):
            with open(path_or_stream, 'rb') as stream:
                self._load(stream)
        else:
            self._load(path_or_stream)

    def _load(self, stream: IO[bytes]):
        start_pos = stream.tell()
        self.version_info = ctype.cdata_from_buffer_copy(stream.read(ctype.sizeof(VersionInfo)), VersionInfo)
        assert self.version_info.magic_str == b'SqPack', Exception(f'version_info magic_str not pair, got {self.version_info.magic_str}')
        assert self.version_info.size == VersionInfo._size_, Exception('version_info size not pair')
        self.index_file_info = ctype.cdata_from_buffer_copy(stream.read(ctype.sizeof(IndexFileInfo)), IndexFileInfo)
        self.is_index1 = self.index_file_info.index_type != 2

        if self.index_file_info.synonym_data_size:
            self.synonyms = {}
            synonym_type = SynonymTableElem_Hash64 if self.is_index1 else SynonymTableElem_Hash32
            stream.seek(start_pos + self.index_file_info.synonym_data_offset)
            el_size = ctype.sizeof(synonym_type)
            for _ in range(self.index_file_info.synonym_data_size // el_size):
                synonym = ctype.cdata_from_buffer_copy(stream.read(el_size), synonym_type)
                self.synonyms[synonym.hash_hoge] = synonym

        if self.index_file_info.dir_index_data_size:
            self.dirs = {}
            el_size = ctype.sizeof(DirectoryIndexInfo)
            stream.seek(start_pos + self.index_file_info.dir_index_data_offset)
            for _ in range(self.index_file_info.dir_index_data_size // el_size):
                _dir = Directory(self, ctype.cdata_from_buffer_copy(stream.read(el_size), DirectoryIndexInfo))
                self.dirs[_dir.hash] = _dir

        if self.dirs:
            self.files = {}
            index_data_type = HashTableElem_Hash64 if self.is_index1 else HashTableElem_Hash32
            for _dir in self.dirs.values():
                _dir.build_files(stream, index_data_type, start_pos)
                for file in _dir.files.values():
                    self.files[file.key] = file

    def get_directory(self, name_or_hash: str | bytes | int) -> Directory:
        # raise KeyError if not found
        if isinstance(name_or_hash, int):
            return self.dirs[name_or_hash]
        if isinstance(name_or_hash, str):
            name_or_hash = name_or_hash.encode('utf-8')
        # assert b'/' not in name_or_hash, Exception('invalid directory name')
        dir_ = self.dirs[compute_hash_32(name_or_hash)]
        dir_.path = name_or_hash
        return dir_

    def get_file(self, name_or_hash: str | bytes | int | tuple[str | bytes | int, ...]) -> FileInfo:
        # raise KeyError if not found
        if isinstance(name_or_hash, tuple):
            dir_key, file_key = name_or_hash
            return self.get_directory(dir_key).get_file(file_key)
        if isinstance(name_or_hash, int):
            return self.files[name_or_hash]
        if isinstance(name_or_hash, str):
            name_or_hash = name_or_hash.encode('utf-8')
        dir_key, file_key = name_or_hash.rsplit(b'/', 1)
        return self.get_directory(dir_key).get_file(file_key)
