import re
import csv
from .csv_parser import CSVParserBase

class RegCSVParser(CSVParserBase):
    __TYPE_EMPTYLINE = "EMPYY"
    __TYPE_COMMENT   = "COMMENT"
    __TYPE_HEADER    = "HEADER"
    __TYPE_FUNCTION  = "FUNCTION"
    __TYPE_UNKNOW    = "UNKNOW"
    __TYPE_TAG       = "TAG"

    def __init__(self, file_path):
        super().__init__(file_path)
        self._tag = None
        self._parse_csv()

    def _set_row(self, addr, row):
        fields = row[1]
        bits = self._extract_bits(row[1])
        default = self._extract_hex(row[2])
        readonly = self._extract_readonly(row[3])
        name = row[4].lower().strip()
        group = "NotImplemented"
        desc = "NotImplemented"
        internal = "NotImplemented"

        shift = min(bits)
        bitmask = self._list2bitsmask(bits)

        self._set_func(
            name = name,
            addr = addr,
            desc = desc,
            group = group,
            shift = shift,
            fields = fields,
            bitmask = bitmask,
            default = default,
            internal = internal,
            readonly = readonly,
        )

    def _set_tag(self, row):
        if self._tag:
            raise ValueError("Set Tag Twice")
        match = re.match("^\$ TAG:\s*(.*)\s*$", row[0])
        self._tag = match.group(1)

    def _parse_csv(self):
        '''
        head_line0
        func_line0
        ...
        func_lineN
        head_line1
        ...
        '''
        with open(self.file(), "r") as csvfile:
            spamreader = csv.reader(csvfile)
            reg_idx = 1
            reg = None
            for row in spamreader:
                row_type = self.__row_type(row)
                if row_type == self.__TYPE_HEADER:
                    reg = self._extract_hex(row[reg_idx])
                elif row_type == self.__TYPE_FUNCTION:
                    self._set_row(reg, row)
                elif row_type == self.__TYPE_TAG:
                    self._set_tag(row)
                # else ignore

    def __row_type(self, row):
        if len(row) == row.count(""):
            return self.__TYPE_EMPTYLINE

        if row[0] == "#":
            return self.__TYPE_COMMENT

        if re.match("^\$ TAG:.*$", row[0]):
            return self.__TYPE_TAG

        s = row[1]
        if re.match("^#\s*addr.*=.*$", s):
            return self.__TYPE_HEADER

        if re.match("\[.*\]$", s):
            return self.__TYPE_FUNCTION

        return self.__TYPE_UNKNOW

    def tag(self):
        return self._tag
