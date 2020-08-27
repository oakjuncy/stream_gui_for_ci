import hid

from .mdio import MdioBase
from .driver import Driver

import os

is_win = os.name == 'nt'







CMD_CANCEL    = [0x0] * is_win + \
                [0x11, 0x00, 0x00, 0x00]
CMD_CHIP_CFG_READ  = [0x0] * is_win + \
                [0x20] + [0] * 63

CMD_CHIP_CFG  = [0x0] * is_win + \
                [0x21, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x00, 
                 0x00, 0x00, 0x00, 0x00, 
                 0x00, 0xfe, 0x01, 0x00, 
                 0x00]

CMD_CFG       = [0x0] * is_win + \
                [0x40, 0x00, 0x00, 0x00, 
                 0x20, 0xa1, 0x07, 0x00,
                 0xff, 0x01, 0x00, 0x00,
                 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0x08, 0x00,
                 0x00, 0x00, 0x00, 0x00]
CMD_CFG_READ  = [0x0] * is_win + \
                [0x41] + [0] * 63

CMD_RW_HEAD   = [0x0] * is_win + [0x42, 0x08, 0x00, 0x00,
                 0xff, 0xff, 0xff, 0xff]

CMD_RW_TAIL   = [0xff, 0xff]

@Driver.register("mcp2210")
class Mcp2210Mdio(MdioBase):
    HELP = "\n".join([
        "Control Mdio Over ftdi",
        "URL: mcp2210://",
    ])

    def _parse_args(self, url):
        args = self.fetch_args(url)
        print(args)

        self._mcp2210 = None

    def open(self):
        self.hid = hid.device()
        self.hid.open(0x04d8, 0x00de)
        
        self.hid.write(CMD_CANCEL)
        rsp = self.hid.read(64)
        assert(rsp[1] == 0)
        # print(", ".join(map(lambda x: '0x%02x' %x, rsp)))
        
        # self.hid.write(CMD_CHIP_CFG_READ)
        # rsp = self.hid.read(64)
        # print(", ".join(map(lambda x: '0x%02x' %x, rsp)))
        self.hid.write(CMD_CHIP_CFG)
        rsp = self.hid.read(64)
        assert(rsp[1] == 0)
        # print(rsp)
            
        # self.hid.write(CMD_CFG_READ)
        # rsp = self.hid.read(64)
        # print(", ".join(map(lambda x: '0x%02x' %x, rsp)))
        self.hid.write(CMD_CFG)
        rsp = self.hid.read(64)
        assert(rsp[1] == 0)
        # print(rsp)

    def close(self):
        self.hid.close()

    def _read(self, phy, reg):
        op_phy_reg = (0x6 << 12) | ((phy & 0x1f) << 7) | ((reg & 0x1f)  << 2) | 0x2
        cmd = CMD_RW_HEAD + [(op_phy_reg >> 8), (op_phy_reg & 0xFF)] + CMD_RW_TAIL

        received = 0
        expect = 8
        buf = list()

        while received < expect:
            self.hid.write(cmd)
            rsp = self.hid.read(64)
            if rsp[1] != 0:
                raise Exception("Error when HID write")
            else:
                length = rsp[2]
                received += length
                buf += rsp[4:4+length]

        #print(cmd[4+is_win:10+is_win], buf[:6])
        assert(cmd[4+is_win:10+is_win] == buf[:6])
        return (buf[6] << 8) | (buf[7])

    def _write(self, phy, reg, val):
        op_phy_reg = (0x5 << 12) | ((phy & 0x1f) << 7) | ((reg & 0x1f)  << 2) | 0x2
        cmd = CMD_RW_HEAD + [(op_phy_reg >> 8), (op_phy_reg & 0xFF), (val >> 8) & 0xff, val & 0xff]

        received = 0
        expect = 8
        buf = list()

        while received < expect:
            self.hid.write(cmd)
            rsp = self.hid.read(64)
            if rsp[1] != 0:
                raise Exception("Error when HID write")
            else:
                length = rsp[2]
                received += length
                buf += rsp[4:4+length]

        assert(cmd[4+is_win:12+is_win] == buf[:8])

    def dev_sel(self, dev):
        assert(dev >= 0 and dev < 8)
        cfg = CMD_CHIP_CFG[:]
        cfg[13+is_win] = 0xFF ^ (1 << dev)

        self.hid.write(cfg)
        rsp = self.hid.read(64)
        assert(rsp[1] == 0)

if __name__ == '__main__':
    mdio_inst = Mcp2210Mdio() 
    mdio_inst.dev_sel(1)
   # print(hex(mdio_inst._read(0, 0)))
