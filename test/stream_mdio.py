import sys
import time
sys.path.append("../")
from mdio_lib import Driver 
from mdio_lib import Interface
from regfile_gen import *

class StreamMdio(RegAccessor):
    def __init__(self):
        self.driver = Driver.find("mcp2210://")
        self.target = Interface.equip(self.driver, "mdio", "sram-loader-tiny", "reg_fields")
        self.driver.open()
        self.driver.dev_sel(3)
        self.target.config_phyid(0)
        self.mdio = self.target
        super().__init__(self.target)

    def verify_spi(self):
        print(hex(self.get_chip_ver()))

    def tx_enable(self):
        self.set_tx_enable(1)

    def tx_disable(self):
        self.set_tx_enable(0)

    def tx_suspend(self):
        self.set_tx_suspend(1)

    def tx_awaken(self):
        self.set_tx_suspend(0)

    def tx_count_clr(self):
        self.set_phy1_count_clr(1)
        self.set_phy2_count_clr(1)
        time.sleep(0.1)
        self.set_phy1_count_clr(0)
        self.set_phy2_count_clr(0)

    def tx_config_send(self):
        self.tx_count_clr()
        time.sleep(0.1)
        self.set_tx1_mode(1)
        self.set_tx2_mode(1)
        self.set_length_mode(0)
        self.set_payload_mode(0)
        self.set_tx2_enable(1)
        self.set_tx1_enable(1)

    def set_pkt_count(self, val):
        tx_count_hi = self.set_pkt_count_hi((val>>32)&0xffff)
        tx_count_mi = self.set_pkt_count_mi((val>>16)&0xffff)
        tx_count_lo = self.set_pkt_count_lo(val&0xffff)

    def get_tx1_count(self):
        tx_count_hi = self.get_tx1_count_hi()
        tx_count_mi = self.get_tx1_count_mi()
        tx_count_lo = self.get_tx1_count_lo()
        tx_count = tx_count_hi*(2**32) + tx_count_mi*(2**16) + tx_count_lo
        return tx_count

    def get_rx1_count(self):
        rx_count_hi = self.get_rx1_count_hi()
        rx_count_mi = self.get_rx1_count_mi()
        rx_count_lo = self.get_rx1_count_lo()
        rx_count = rx_count_hi*(2**32) + rx_count_mi*(2**16) + rx_count_lo
        return rx_count

    def get_tx2_count(self):
        tx_count_hi = self.get_tx2_count_hi()
        tx_count_mi = self.get_tx2_count_mi()
        tx_count_lo = self.get_tx2_count_lo()
        tx_count = tx_count_hi*(2**32) + tx_count_mi*(2**16) + tx_count_lo
        return tx_count

    def get_rx2_count(self):
        rx_count_hi = self.get_rx2_count_hi()
        rx_count_mi = self.get_rx2_count_mi()
        rx_count_lo = self.get_rx2_count_lo()
        rx_count = rx_count_hi*(2**32) + rx_count_mi*(2**16) + rx_count_lo
        return rx_count

    def get_rx1_err_count(self):
        rx_crc_hi = self.get_rx1_crc_err_hi()
        rx_crc_mi = self.get_rx1_crc_err_mi()
        rx_crc_lo = self.get_rx1_crc_err_lo()
        rx_crc = rx_crc_hi*(2**32) + rx_crc_mi*(2**16) + rx_crc_lo
        return rx_crc

    def get_rx2_err_count(self):
        rx_crc_hi = self.get_rx2_crc_err_hi()
        rx_crc_mi = self.get_rx2_crc_err_mi()
        rx_crc_lo = self.get_rx2_crc_err_lo()
        rx_crc = rx_crc_hi*(2**32) + rx_crc_mi*(2**16) + rx_crc_lo
        return rx_crc

    def set_tx_enable(self, val):
        self.set_tx1_enable(val)
        self.set_tx2_enable(val)

    def print_count(self):
        self.set_tx_enable(0)
        time.sleep(0.1)
        print("tx1 count", hex(self.get_tx1_count()))
        print("rx1 count", hex(self.get_rx1_count()))
        print("rx1 crc", hex(self.get_rx1_err_count()))
        print("tx2 count", hex(self.get_tx2_count()))
        print("rx2 count", hex(self.get_rx2_count()))
        print("rx2 crc", hex(self.get_rx2_err_count()))


if __name__ == "__main__":
    chip = StreamMdio()
    chip.driver.dev_sel(3)
    chip.verify_spi()
    chip.set_pkt_count(0x1234)
    chip.tx_config_send()
    time.sleep(10)
    chip.print_count()
