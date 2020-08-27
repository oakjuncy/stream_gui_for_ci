from .interface import Interface

@Interface.register("raw", dep = ["mdio"])
class Raw:
    def raw_read(self, phy, reg):
        return self.get_driver().read(phy, reg)

    def raw_write(self, phy, reg, val):
        return self.get_driver().write(phy, reg, val)
