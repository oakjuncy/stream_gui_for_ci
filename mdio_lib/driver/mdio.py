import time

class MdioException(Exception): pass


class StoreCommand:
    start_time = time.time()

    def __str__(self):
        return "{time:>.9f}: {cmd}, {args}".format(
            time = self._time,
            cmd = self._cmd,
            args = self._args or "None"
        )

    def __init__(self, cmd, args):
        self._cmd = cmd
        self._args = args
        self._time = time.time() - self.start_time

    def command(self):
        return self._cmd

    def args(self):
        return self._args

    def timestamp(self):
        return self._time


class Storable:
    def __init__(self):
        self._storable = False
        self._store_queue = list()

    def store_enable(self, b=None):
        if type(b) == bool:
            self._storable = b
        return self._storable

    def store(self, command):
        if not self._storable:
            return
        self._store_queue.append(command)

    def store_clean(self):
        self._store_queue = list()

    def store_dump(self):
        return self._store_queue


def pack_mdio_info(phy, reg, val):
    p = "phy=0x{phy:02x} reg=0x{reg:04x} val=0x{val:04x}"
    return p.format(
        phy = phy,
        reg = reg,
        val = val
    )

class HasMdioCommand:

    class MdioRead(StoreCommand):
        def __init__(self, phy, reg, val):
            info = pack_mdio_info(phy, reg, val)
            super().__init__("read", info)


    class MdioWrite(StoreCommand):
        def __init__(self, phy, reg, val):
            info = pack_mdio_info(phy, reg, val)
            super().__init__("write", info)


class MdioBase(Storable, HasMdioCommand):
    HELP = "None"

    def __init__(self, url):
        super().__init__();
        self._parse_args(url)

    @staticmethod
    def fetch_args(url):
        infos = url.split("://")
        if len(infos) == 1:
            return None
        elif len(infos) == 2:
            return infos[-1]
        else:
            raise MdioException("Error url {}".format(url))

    def _parse_args(self, url):
        raise NotImplemented

    def _read(self, phy, reg):
        raise NotImplemented

    def _write(self, phy, reg, val):
        raise NotImplemented

    def open(self):
        raise NotImplemented

    def close(self):
        raise NotImplemented

    def read(self, phy, reg):
        val = self._read(phy, reg)
        self.store(self.MdioRead(phy, reg, val))
        return val

    def write(self, phy, reg, val):
        self._write(phy, reg, val)
        self.store(self.MdioWrite(phy, reg, val))
        return val
