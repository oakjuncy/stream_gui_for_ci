import re
import csv
from collections import namedtuple
from functools import reduce

"""
@name:     the name of field
@addr:     the address of register
@desc:     the description of field

@fields:   expect [x] or [x:y], the raw fields
@bitmask:  the bitmask of $fields
@shift:    the shift of $fields

@group:    optional, the group info of field
@readonly: optional, if this field is readonly
@internal: optional, if this field is design for internal only
@default:  optional, the default value of field

"""
CSVFunction = namedtuple("CSVFunction", [
    "name", "addr", "bitmask", "shift",
    "readonly", "desc", "internal",
    "group", "default", "fields",
])

class _CSVRegisterMapper(object):
    def __init__(self):
        self._func_list = []

    def set_func(self, **kw):
        item = CSVFunction(**kw)
        self._func_list.append(item)

    def func_list(self):
        return list(self._func_list)

class CSVParserBase:
    CSVFunction = CSVFunction
    CSVRegisterMapper = _CSVRegisterMapper

    @staticmethod
    def _list2bitsmask(ls):
        val = 0
        for l in ls:
            val |= 1 << l
        return  val

    @staticmethod
    def _extract_bits(s):
        '''
        Here we support only have two types of the string:
        - "[x:y]" => range(y, x + 1)
        - "[x]"   => range(x, x + 1)
        so:
            range_i = nums[len(nums) - 1]
        '''
        num_list = list(map(int, filter(lambda x: x != "", re.findall("\d*", s))))
        high = num_list[0] + 1
        low = num_list[len(num_list) - 1]
        return range(low, high)

    @staticmethod
    def _extract_hex(s):
        res = re.findall("0[xX][0-9a-f,A-F]+", s)[0]
        if res == "":
            raise ValueError("Unknow hex format", res)
        return int(res, 16)

    @staticmethod
    def _extract_readonly(s):
        return s == "RD"

    @staticmethod
    def _extract_internal(s):
        return s == "internal"

    def __init__(self, file_path):
        self._file_path = file_path
        self._mapper = _CSVRegisterMapper()

    def functions(self):
        return self._mapper.func_list()

    def file(self):
        return self._file_path

    def _set_func(self, **kw):
        self._mapper.set_func(**kw)
