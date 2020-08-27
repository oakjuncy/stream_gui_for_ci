import os
import re
import inspect
import datetime
from six import with_metaclass

def get_csv_path(name):
    basedir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(basedir, "regmap", name)
    return path


class FieldsException(Exception): pass


class FunctionCreatorBase:
    def create_functions(self, flist):
        raise NotImplementedError


class FunctionConstructor(type):
    """
    The is just glue-class. Fetch `__PARSER__` and `__CREATOR__` to create
    functions.
    - The __CREATOR__ must have the create_functions(flist). Such as the
      subclass of `FunctionCreatorBase`
    - optional: The __PARSER__ must have functions(). Such as the subclass of
      `.regmap.CSVParserBase`
    - optional: The __ATTACH__ attatches some extra informations.
        def attach(cls, name, base, attrs, flist): pass

    Note:
    - This is the metaclass of FieldsBase.
    - if __PARSER__ is not implemented, we just send an empty list into creator.
    """

    def __new__(cls, name, bases, attrs):
        """
        Class Constructor. Adding additonal functions into target class.
        """
        """
        We find __PARSER__ and __CREATOR__ only in current class.
        It prevents generating functions many times.
        """
        parser = attrs.get("__PARSER__", None)
        creator = attrs.get("__CREATOR__", None)
        # The attach can be inherited by subclass of FunctionBase.
        attach = cls._find_attribute(bases, attrs, "__ATTACH__")

        if (creator is None) or (creator is NotImplemented):
            return type.__new__(cls, name, bases, attrs)

        # Calling parser
        if parser is not None:
            flist = parser.functions()
        else:
            flist = []

        # Calling creator
        funcs = creator.create_functions(flist)
        attrs = cls.merge_dict(attrs, funcs)

        if attach is not None:
            attach(cls, name, bases, attrs, flist)

        return type.__new__(cls, name, bases, attrs)

    @staticmethod
    def _find_attribute(bases, attrs, kw):
        a = attrs.get(kw, None)
        if a is not None:
            return a

        for b in bases:
            a = getattr(b, kw, None)
            if a is not None and a is not NotImplemented:
                return a
        return None

    @staticmethod
    def merge_dict(x, y):
        z = x.copy()
        z.update(y)
        return z


class FunctionBase(with_metaclass(FunctionConstructor)):
    __PARSER__ = None
    __CREATOR__ = None
    __ATTACH__ = None


class FieldsBase(FunctionBase):
    """
    Attach extra informations for FieldsDumper
    """

    @staticmethod
    def __ATTACH__(cls, name, base, attrs, flist):
        autopattern = attrs.get("AUTOGEN_PATTERN", None)
        func_list = flist
        func_dict = dict()
        for func in func_list:
            if func_dict.get(func.name, None):
                raise FieldsException("Duplicate function name: {}"
                        .format(func.name))
            func_dict[func.name] = func

        attrs["_func_list_{}".format(name)] = func_list
        attrs["_func_dict_{}".format(name)] = func_dict
        attrs["_dump_pattern_{}".format(name)] = autopattern


class FieldsCreatorBase(FunctionCreatorBase):
    """
    Interface of FunctionCreator;
    The users should implement below functions:
      - _create_getter()
      - _create_setter()
      - _create_doc()

    Fixme Later:
      For the pourpose of dumpping codes out.
      The user MUST pass the first argument with name `field`.
    """

    def create_functions(self, flist):
        """
        @flist: list of CSVFunction(.regmap.csv_parser.CSVFunction)
        """
        d = dict()
        for f in flist:
            d.update(self._create_one_field(f))
        return d

    def _create_getter(self, field):
        raise NotImplementedError

    def _create_setter(self, field):
        raise NotImplementedError

    def _create_doc(self, field):
        raise NotImplementedError

    def _create_one_field(self, field):
        funcs = dict()
        name, func = self._create_getter(field)
        funcs[name] = func

        readonly = getattr(field, "readonly")
        if readonly is not True:
            name, func = self._create_setter(field)
            funcs[name] = func

        name, func = self._create_doc(field)
        funcs[name] = func
        return funcs


class FieldsDumper:
    """
    This is an OPTIONAL trait for FieldsBase.
    Dump functions in this class to a file.
    This class should be mixed into a subclass of FieldsBase.

    This class is depended on attributes `cls._func_list` and
    `cls._func_dict` which are inserted by `FieldsCreatorBase`.
    """

    """
    The User should OVERRIDE pattern.
    Such as, ^get, ^set, ^xxx.
    """
    AUTOGEN_PATTERN = []

    @classmethod
    def generate_code(cls, path):
        """
        """
        code = cls._generate_code(cls)
        with open(path, "w") as f:
            f.write(code)

    @classmethod
    def generate_doc(cls, path):
        doc = cls._generate_doc()
        with open(path, "w") as f:
            f.write(doc)

    @classmethod
    def __get_func_dict(cls):
        def pick(name):
            return name.startswith("_func_dict")
        dlist = list(filter(pick, dir(cls)))
        d = {}
        for dname in dlist:
            d.update(getattr(cls, dname))
        return d

    @classmethod
    def __get_pattern_list(cls):
        def pick(name):
            return name.startswith("_dump_pattern")
        plist = list(filter(pick, dir(cls)))
        ps = []
        for pname in plist:
            ps.extend(getattr(cls, pname))
        return ps

    @classmethod
    def __get_func_list(cls):
        pattern_list = cls.__get_pattern_list()
        def pick(name):
            for p in pattern_list:
                if re.match(p, name):
                    return True
            return False

        flist = list(filter(pick, dir(cls)))
        return flist

    @classmethod
    def _generate_code(cls, subcls):
        code_list = (cls.__format_header() +
                    cls.__format_autogen_code() +
                    cls.__format_additional_code())
        code = "\n\n".join(code_list)
        return code

    @classmethod
    def _generate_doc(cls):
        manual = getattr(cls, "MANUAL_PATTERN", [])
        doc_list = []
        doc_list.append("## Function List")
        doc_list.append("\n### Manully")
        for f in manual:
            doc_list.append("- {}".format(f))

        doc_list.append("\n### Auto Gen Pattern")
        for p in cls.AUTOGEN_PATTERN:
            doc_list.append("- {}".format(p))

        func_dict = cls.__get_func_dict()
        doc_list.append("\n## Register List")
        for _, v in func_dict.items():
            item = "\n{}".format(cls.__pretty_doc(v))
            doc_list.append(item)

        doc = "\n".join(doc_list)
        doc = doc.replace("\r\n", "\n")
        return doc

    @staticmethod
    def __pretty_doc(tfunc):
        info = (
        "### name:`{0}`\n"
        "addr:{1:#x}, shift:{2}, bitmask:0x{3:0>4x}\n"
        "readonly:{4}, internal:{5}, group:{6}\n"
        "desc:"
        "     {7}"
        ).format(
            tfunc.name, tfunc.addr, tfunc.shift, tfunc.bitmask,
            tfunc.readonly, tfunc.internal, tfunc.group,
            tfunc.desc)
        return info

    @classmethod
    def __format_additional_code(cls):
        manual = getattr(cls, "MANUAL_PATTERN", [])
        return [inspect.getsource(getattr(cls, func))
                for func in manual]

    @classmethod
    def __format_header(cls):
        today = datetime.date.today().strftime("%Y %b %d")
        header = (
        "class {0}(object):\n" +
        "    '''\n" +
        "    @autogen at {1}, based on {2}\n" +
        "    '''\n")
        return [header.format(cls.__name__, today, cls.__PARSER__.file())]

    @classmethod
    def __funcode(cls, func_dict, func_name):
        func = getattr(cls, func_name)
        code = inspect.getsource(func)
        code = cls.__format_code_indent(code)
        code = cls.__format_code_info(func_dict, func_name, code)
        return code

    @staticmethod
    def __format_code_indent(code):
        line_list = code.splitlines()

        # fetch definition of function and format it
        def_line = list(filter(lambda x:"def" in x, line_list))[0]
        new_def_line = re.sub("^\s*", "    ", def_line)

        # gen new line fmt
        diff = len(def_line) - len(new_def_line)
        pattern = "^\s{{{}}}".format(diff)
        fmt = lambda line: re.sub(pattern, "", line)

        # apply fmt for each lines
        new_line_list = map(fmt, line_list)
        return "\n".join(new_line_list)

    @staticmethod
    def __format_extract_name(func_name):
        return re.findall("[sg]et_(.*)$", func_name)[0]

    @classmethod
    def __format_code_info(cls, func_dict, func_name, code):
        name = cls.__format_extract_name(func_name)
        info = func_dict.get(name, None)
        # escape get/set function not in dict
        if not info:
            return ""

        def rename(match_object):
            return "def {}(".format(func_name)

        def comment(match_object):
            c = '''"""\n{}\n"""'''.format(info.desc)
            c_list = map(lambda l: "        {}".format(l),
                         c.splitlines())
            c = "\n".join(c_list)

            return "{}\n{}".format(match_object.group(0), c)

        def replace(match_object):
            '''
            We will got `info.xxx` here.
            kw is `xxx`
            '''
            kw = match_object.group(0).split(".")[-1]
            val = getattr(info, kw)
            if type(val) == int:
                return "{:#x}".format(val)
            else:
                return "{}".format(val)

        # rename function
        code = re.sub("def.*\(", rename, code)

        # add comments
        code = re.sub("def.*", comment, code)

        # replace variables
        code = re.sub("field\.\w+", replace, code)
        return code

    @classmethod
    def __format_autogen_code(cls):
        flist = cls.__get_func_list()
        fdict = cls.__get_func_dict()
        return [cls.__funcode(fdict, f) for f in flist]
