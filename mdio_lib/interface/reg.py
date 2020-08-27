from .interface import Interface
from .regmap.reg_parser import RegCSVParser
from .fields import FieldsCreatorBase, FieldsBase, FieldsDumper, get_csv_path

class RegFunctionCreatorImpl(FieldsCreatorBase):
    def _create_getter(self, field):
        def getter(self):
            page = (field.addr >> 5)
            reg = (field.addr & 0x1f)
            res = self.read(page=page, reg=reg)
            if res is None:
                return None
            return (res & field.bitmask) >> field.shift
        return "get_{}".format(field.name), getter

    def _create_setter(self, field):
        def setter(self, val):
            page = (field.addr >> 5)
            reg = (field.addr & 0x1f)
            v = (val << field.shift) & field.bitmask
            v_ori = self.read(page=page, reg=reg)
            v_ori &= ~field.bitmask
            v = v | v_ori
            self.write(page=page, reg=reg, val=v)
        return "set_{}".format(field.name), setter

    def _create_doc(self, field):
        def doc(self):
            return field.desc
        return "doc_{}".format(field.name), doc

@Interface.register("reg_fields", dep = ["mdio"])
class RegFields(FieldsBase, FieldsDumper):
    __PARSER__ = RegCSVParser(get_csv_path("regfile.csv"))
    __CREATOR__ = RegFunctionCreatorImpl()
    AUTOGEN_PATTERN = [
        "^set_",
        "^get_",
    ]
