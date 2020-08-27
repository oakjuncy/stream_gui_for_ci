class InterfaceException(Exception): pass


class HasDriver(object):
    def __init__(self, driver):
        self._driver = driver

    def get_driver(self):
        return self._driver


class Interface:
    _interface_classes = {}

    @classmethod
    def register(cls, name, dep = None):
        """
        usage:
        @Interface.register("name")
        """
        def inner(kls):
            key = str(name).lower()
            if key in cls._interface_classes:
                raise InterfaceException("Dubplicated interface {}".foramt(name))

            if (dep is not None) and (type(dep) != list):
                raise InterfaceException("Error dependency input")

            cls._interface_classes[key] = (kls, dep)
            return kls
        return inner

    @classmethod
    def list(cls):
        return cls._interface_classes.keys()

    @classmethod
    def equip(cls, driver, *wrapper_names):
        def find_class(name):
            kls, _ = cls._interface_classes[name]
            return kls

        def find_dep(name):
            _, dep = cls._interface_classes[name]
            return dep


        def find_all(total, names):
            if names is None:
                return

            for n in names:
                if n in total: continue

                total.append(n)
                dep = find_dep(n)
                find_all(total, dep)

        names = list()
        find_all(names, wrapper_names)
        classes = list(map(find_class, names))

        has_init_list = list(
            filter(
                lambda kls: issubclass(kls, HasDriver),
                classes
            )
        )
        if len(has_init_list) >= 2:
            raise InterfaceException(
                "You have more than one class implemented HasDriver {}"
                .format(has_init_list))
        elif len(has_init_list) == 0:
            classes.append(HasDriver)
        else: # len(has_init_list) == 1:
            pass

        class Temp(*classes):
            pass
        return Temp(driver)
