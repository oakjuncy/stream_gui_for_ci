from .mdio import MdioBase
from .driver import Driver

@Driver.register("fake")
class Fake(MdioBase):
    HELP = "\n".join([
        "This is a fake mdio driver.",
        "URL: fake://phy_ids",
        "  phy_ids ::= Nil | phy_id[,phy_id]",
        "  phy_id ::= Hex",
    ])

    @staticmethod
    def _pack_key(phy, dev, reg):
        return (phy, dev, reg)

    @staticmethod
    def _log_info(op, phy, dev, reg, val):
        print("Fake: {op:5}| 0x{phy:02x}.0x{dev:02x}.0x{reg:04x} = 0x{val:04x}"
            .format(op = op, phy = phy, dev = dev, reg = reg, val = val))

    def _parse_args(self, url):
        args = self.fetch_args(url)
        ids = []
        if not args:
            ids.append(0x1a)
        else:
            [ids.append(int(phyid, 16)) for phyid in args.split(",")]

        print("Fake: Init with phy ids {}".format(ids))
        self.__phyids = ids
        self.__regs = dict()

    def open(self):
        print("Fake: open")

    def close(self):
        print("Fake: close")

    def _read(self, phy, reg):
        dev = 0
        # unsupported phy id
        if phy not in self.__phyids:
            val = 0
            self._log_info("read", phy, dev, reg, val)
            return val

        key = self._pack_key(phy, dev, reg)
        val = self.__regs.get(key, None)
        if val is None:
            val = 0
            self.__regs[key] = val

        self._log_info("read", phy, dev, reg, val)
        return val

    def _write(self, phy, reg, val):
        dev = 0
        # unsupported phy id
        if phy not in self.__phyids:
            self._log_info("write", phy, dev, reg, val)
            return val

        key = self._pack_key(phy, dev, reg)
        self.__regs[key] = val
        self._log_info("write", phy, dev, reg, val)
        return val
