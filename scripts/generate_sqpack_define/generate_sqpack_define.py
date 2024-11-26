import io
import json
import pathlib
import re

from fps.utils.sqpack import SqPack
from fps.utils.sqpack.exd import Sheet

cwd = pathlib.Path(__file__).parent
saint_coinach_path = cwd / 'SaintCoinach'
saint_coinach_define_path = saint_coinach_path / 'SaintCoinach' / 'Definitions'


class IndentPusher:
    def __init__(self, writer: 'IndentWriter'):
        self.writer = writer

    def __enter__(self):
        self.writer.level += self.writer.indent

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.writer.level -= self.writer.indent


class IndentWriter:
    def __init__(self, start_indent=0, indent=4):
        self.indent = indent
        self.level = start_indent
        self.buf = io.StringIO()
        self.is_new_line = True

    def push(self):
        return IndentPusher(self)

    def write(self, s: str):
        *lines, last = s.split('\n')
        for line in lines:
            if line:
                if self.is_new_line:
                    self.buf.write(' ' * self.level)
                self.buf.write(line)
            self.buf.write('\n')
            self.is_new_line = True
        if last:
            if self.is_new_line:
                self.buf.write(' ' * self.level)
            self.buf.write(last)
            self.is_new_line = False
        else:
            self.is_new_line = True
        return self

    def getvalue(self):
        return self.buf.getvalue()


COL_TYPE_MAP = {
    -1: 'bytes',
    0: 'SeString',
    0x0001: 'bool',
    0x0002: 'int',
    0x0003: 'int',
    0x0004: 'int',
    0x0005: 'int',
    0x0006: 'int',
    0x0007: 'int',
    0x0009: 'float',
    0x000B: 'float',
    **{0x19 + i: 'int' for i in range(0, 8)}
}


class SimpleFieldDef:
    def __init__(self, sheet: Sheet, field_def, is_top_level=True):
        self.sheet = sheet
        self.field_def = field_def
        self.is_top_level = is_top_level

    def to_line(self, col_id, real_col_id=None):
        assert self.is_top_level
        real_col_id = real_col_id if real_col_id is not None else col_id
        res_type = COL_TYPE_MAP[self.sheet.header.columns[real_col_id].type]
        return f"{self.get_name(real_col_id)}: SimpleData[{res_type}] = SimpleData({col_id})\n"

    def to_class(self):
        return ""

    def build(self, real_col_id):
        ...

    def get_name(self, col_id):
        if 'name' in self.field_def:
            return to_field_name(self.field_def['name'])
        match self.sheet.header.columns[col_id].type:
            case 0 | -1:
                return "str"
            case 1:
                return "flag"
            case n if n <= 0xb:
                return "num"
            case n if 0x19 <= n < (0x19 + 8):
                return "flag"
            case _:
                return "unk"

    def get_col_size(self):
        return 1

    def to_py_type(self, col_id):
        return COL_TYPE_MAP[self.sheet.header.columns[col_id].type]

    def to_constructor(self):
        return "SimpleData"


class ArrayFieldDef:
    def __init__(self, sheet: Sheet, field_def, is_top_level=True):
        self.sheet = sheet
        self.field_def = field_def
        self.is_top_level = is_top_level
        self.element_def = parse_field_def(sheet, field_def['definition'], False)
        self.sep = 0

    def build(self, real_col_id):
        self.element_def.build(real_col_id)
        self.sep = self.element_def.get_col_size()

    def to_line(self, col_id, real_col_id=None):
        assert self.is_top_level
        real_col_id = real_col_id if real_col_id is not None else col_id
        el_py_type = self.element_def.to_py_type(real_col_id)
        el_constructor = self.element_def.to_constructor()
        return f"{self.get_name(real_col_id)}: ArrayData[{el_py_type}] = ArrayData({col_id}, {self.field_def['count']}, {self.sep}, {el_constructor})\n"

    def get_name(self, col_id):
        if 'name' in self.field_def:
            return to_field_name(self.field_def['name'])
        n = self.element_def.get_name(col_id)
        if not n.endswith('s'):
            n += 's'
        return n

    def to_class(self):
        return self.element_def.to_class()

    def get_col_size(self):
        return self.sep * self.field_def['count']

    def to_py_type(self, col_id):
        return f'ArrayData_[{self.element_def.to_py_type(col_id)}]'

    def to_constructor(self):
        return f'ArrayData.make({self.field_def["count"]}, {self.sep}, {self.element_def.to_constructor()})'


def normalize_name(name):
    # split by symbols and upper case
    s = re.sub(r'([A-Z])', r'_\1', name).lower()
    s = re.split(r'[^a-z0-9]', s)
    s = [part_ for part in s if (part_ := part.strip())]
    # join continuous single letter parts
    s_ = []
    for i, part in enumerate(s):
        if len(part) == 1 and i and len(s[i - 1]) == 1:
            s_[-1] += part
        elif part == 'p' and i and s_[-1] == 'pv':
            s_[-1] += part
        else:
            s_.append(part)
    s = s_
    if s[0][0].isdigit():
        s.insert(0, 'f')
    return s


def to_struct_name(name):
    return ''.join([part.capitalize() for part in normalize_name(name)])


field_name_map = {
    'class': 'class_job',
    'def': 'def_',
}


def to_field_name(name):
    s = '_'.join(normalize_name(name))
    return field_name_map.get(s, s)


class StructFieldDef:
    def __init__(self, sheet: Sheet, field_def, is_top_level=True):
        self.sheet = sheet
        self.field_def = field_def
        self.is_top_level = is_top_level
        self.members = [parse_field_def(sheet, member) for member in field_def['members']]
        self.col_size = 0
        self.class_def = ""
        self.struct_name = to_struct_name(self.get_name())

    def build(self, real_col_id):
        attrs = IndentWriter()
        structs = IndentWriter()
        index = 0
        for member in self.members:
            member_index = member.field_def.get("index", index)
            if isinstance(member, StructFieldDef):
                member.build(member_index + real_col_id)
                structs.write(member.to_class())
            attrs.write(member.to_line(member_index, member_index + real_col_id))
            index = max(index, member_index + 1)
        self.col_size = index

        cls = IndentWriter()
        cls.write(f'class {self.struct_name}(Struct):\n')
        with cls.push():
            cls.write(structs.getvalue())
            cls.write(attrs.getvalue())
        self.class_def = cls.getvalue()

    def to_line(self, col_id, real_col_id=None):
        return f"{self.get_name()}: StructData[{self.struct_name}] = StructData({col_id}, {self.struct_name})\n"

    def to_class(self):
        return self.class_def

    def get_name(self, col_id=None):
        if 'name' in self.field_def:
            return to_field_name(self.field_def['name'])
        return "data"

    def get_col_size(self):
        return self.col_size

    def to_py_type(self, col_id):
        return self.struct_name

    def to_constructor(self):
        return f'StructData.make({self.struct_name})'


def parse_field_def(sheet: Sheet, field_def, is_top_level=True):
    match field_def.get('type'):
        case None:
            return SimpleFieldDef(sheet, field_def, is_top_level)
        case "repeat":
            return ArrayFieldDef(sheet, field_def, is_top_level)
        case "group":
            if len(field_def['members']) == 1:
                return parse_field_def(sheet, field_def['members'][0], is_top_level)
            return StructFieldDef(sheet, field_def, is_top_level)
        case _:
            raise ValueError(f'Unknown field type: {field_def["type"]}')


def special_sheets(define):
    match define['sheet']:
        case "Item":
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('name') == "BaseParam"
            ))['definition']['name'] = "Param"
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('name') == "BaseParam{Special}"
            ))['definition']['name'] = "ParamSpecial"
        case "RelicNote":
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('name') == "MonsterNoteTarget{Common}"
            ))['definition']['name'] = "Target"
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('name') == "Fate"
            ))['definition']['name'] = "Fate"
        case "SpecialShop":
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('type') == 'repeat' and
                   f['definition']['members'][0]['definition'].get('name') == "Item{Receive}"
            ))['definition']['name'] = "Receive"
            next((
                f for f in define['definitions']
                if f.get('type') == 'repeat' and
                   f['definition'].get('type') == "group" and
                   f['definition']['members'] and
                   f['definition']['members'][0].get('type') == 'repeat' and
                   f['definition']['members'][0]['definition'].get('name') == "Item{Cost}"
            ))['definition']['name'] = "Cost"


def parse_define_file(sqpack: SqPack, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        define = json.load(f)
    special_sheets(define)
    sheet_name = define['sheet']
    sheet = sqpack.exd.get_sheet(sheet_name)
    attrs = IndentWriter()
    structs = IndentWriter()
    attrs.write(f'_sign = {sheet.get_sign()!r}\n')
    if display_col := define.get('defaultColumn'):
        attrs.write(f'_display = {display_col!r}\n')
    if define['definitions']:
        attrs.write("\n")
        index = 0
        for member in define['definitions']:
            field_def = parse_field_def(sheet, member)
            member_index = member.get("index", index)
            field_def.build(member_index)
            structs.write((s_ := field_def.to_class()) and s_ + '\n')
            attrs.write(field_def.to_line(member_index))
            index = max(index, member_index + 1)
    cls = IndentWriter()
    cls.write(f'@data_row_impl\n'
              f'class {sheet_name}(DataRow):\n')
    with cls.push():
        cls.write(structs.getvalue())
        cls.write(attrs.getvalue())
    return cls.getvalue()


def main():
    sqpack = SqPack(r'D:\game\ff14_res\history\i7.10')
    # print(parse_define_file(sqpack, saint_coinach_define_path / "ItemFood.json"))
    s = IndentWriter()
    s.write('from fps.utils.sestring import SeString\n')
    s.write('from fps.utils.sqpack.exd import DataRow\n')
    s.write('from fps.utils.sqpack.exd.data_row import SimpleData, ArrayData_, ArrayData, Struct, StructData\n')
    s.write('from fps.utils.sqpack.exd.row import data_row_impl\n')
    s.write('\n\n')

    for file_path in saint_coinach_define_path.glob('*.json'):
        try:
            s.write(parse_define_file(sqpack, file_path))
        except Exception as e:
            print(f'Error in {file_path}: {e}')
            raise
        s.write('\n\n')
    with open(cwd / 'sheets.py', 'w', encoding='utf-8') as f:
        f.write(s.getvalue().strip() + '\n')


if __name__ == '__main__':
    main()