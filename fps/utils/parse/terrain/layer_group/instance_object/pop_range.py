import enum

from .utils import *


class PopRangeInstanceObject(InstanceObject):
    class PopType(enum.IntEnum):
        PC = 0X1
        NPC = 0X2
        BNPC = 0X2
        Content = 0X3

    pop_type = ctype.SField(ctype.c_uint32, 0X30)
    relative_positions: 'RelativePositions' = eval('0X34')
    inner_radius_ratio = ctype.SField(ctype.c_float, 0X3C)
    index = ctype.SField(ctype.c_uint8, 0X40)
    shuffle_count = ctype.SField(ctype.c_uint8, 0X41)

    @property
    def e_pop_type(self):
        return self.PopType(self.pop_type)
