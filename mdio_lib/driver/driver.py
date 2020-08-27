from .mdio import MdioBase

class DriverException(Exception): pass

class Driver:
    _driver_classes = {}

    @classmethod
    def register(cls, name):
        """
        usage:
        @Driver.register("name")
        """
        def inner(kls):
            # make sure kls is instance of MdioBase
            if not issubclass(kls, MdioBase):
                err = "Error {} is not instance of {}".format(kls, MdioBase)
                raise DriverException(err)

            key = str(name).lower()
            if key in cls._driver_classes:
                raise DriverException("Dubplicated driver {}".foramt(name))

            cls._driver_classes[key] = kls
            return kls
        return inner

    @classmethod
    def list(cls):
        return cls._driver_classes.keys()

    @classmethod
    def help(cls):
        for name, dkls in cls._driver_classes.items():
            print("--------")
            print("{name}:".format(name = name))
            print(dkls.HELP)

    @classmethod
    def find(cls, url):
        """
        URL: name://arg[0],arg[1],arg[2],...
        """
        infos = url.split("://")
        key = str(infos[0]).lower()
        dkls = cls._driver_classes.get(key, None)
        if not dkls:
            return None

        try:
            driver = dkls(url)
            return driver
        except:
            print(dlks.HELP)
            return None

