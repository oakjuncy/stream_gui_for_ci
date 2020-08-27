from .interface import Interface, HasDriver

@Interface.register("mdio")
class Mdio(HasDriver):
    REG_PAGE = 31

    def __init__(self, driver, phy = 0x1a):
        super().__init__(driver)
        self._phy = phy

    def config_phyid(self, phyid):
        self._phy = phyid

    def phyid(self):
        return self._phy

    def set_page(self, page):
        return self.get_driver().write(self._phy, self.REG_PAGE, page)

    def get_page(self):
        return self.get_driver().read(self._phy, self.REG_PAGE)

    def read(self, reg, page = None):
        if page is not None:
            self.set_page(page)
        return self.get_driver().read(self._phy, reg)

    def write(self, reg, val, page = None):
        if page is not None:
            self.set_page(page)
        return self.get_driver().write(self._phy, reg, val)
