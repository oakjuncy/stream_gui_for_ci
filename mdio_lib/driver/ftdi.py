from .ftd232hl import FTD232HL
from .mdio import MdioBase
from .driver import Driver


class FtdiCore(FTD232HL):
    def __init__(self):
        FTD232HL.__init__(self)

        self.divisor = 0x000d
        self.timeout_read  = 100
        self.timeout_write = 5000
        self.op_divide_5_on = self.OP_DIVIDE_5_TURN_OFF
        self.op_adaptive_clk_en = self.OP_ADAPTIVE_CLK_DISABLE
        self.op_3phase_en = self.OP_3PHASE_ENABLE

        # config default gpio level
        self.ftdi_gpio_init(self.GPIO_CLK, self.LEVEL_HIGH)
        self.ftdi_gpio_init(self.GPIO_MOSI, self.LEVEL_HIGH)

    def __gen_mdio22(self, mode, phy, reg, data = None):
        if mode == "read":
            code = 0x60
            data = [0xff, 0xff]
        else:
            code = 0x50
            data = [data >> 8, data]

        preamble = [0xff, 0xff, 0xff, 0xff]
        addr = [
            (0x0f & (phy >> 1)) | code,
            (phy << 7) | (reg << 2) | 0x02]
        end = [0x7f, 0x87]
        return preamble + addr + data + end

    def __gen_mdio45(self, mode, phy, devtype, reg, data = None):
        addr_code = 0x00

        if mode == "read":
            code = 0x30
            data = [0xff, 0xff]
        else:
            code = 0x10
            data = [data >> 8, data]

        reg = [reg >> 8, reg]

        preamble = [0xff, 0xff, 0xff, 0xff]
        dev_cmd = [
            (0x0f & (phy >> 1)) | addr_code,
            (phy << 7) | (devtype << 2) | 0x02]

        op_cmd = [
            (0x0f & (phy >> 1)) | code,
            (phy << 7) | (devtype << 2) | 0x02]

        return (preamble + dev_cmd + reg,
                preamble + op_cmd + data)

    def write_mdio45(self, phy, dev, reg, data):
        opcode = self.ftdi_gen_opcode(
            order = self.ORDER_MSB,
            mode = self.MODE_BYTES,
            data_out = self.ENABLE,
            edge_out = self.EDGE_RISING,
        )
        addr_cmd, value_cmd = self.__gen_mdio45("write", phy, dev, reg, data)

        addr_buf = self.ftdi_prepare_write_buf(opcode, addr_cmd)
        value_buf = self.ftdi_prepare_write_buf(opcode, value_cmd)

        return self.ftdi_write(addr_buf + value_buf)

    def read_mdio45(self, phy, dev, reg):
        addr_opcode = self.ftdi_gen_opcode(
            order = self.ORDER_MSB,
            mode = self.MODE_BYTES,
            data_out = self.ENABLE,
            edge_out = self.EDGE_RISING,
        )

        value_opcode = self.ftdi_gen_opcode(
            order = self.ORDER_MSB,
            mode = self.MODE_BYTES,
            data_out = self.ENABLE,
            edge_out = self.EDGE_RISING,
            data_in = self.ENABLE,
            edge_in = self.EDGE_FALLING,
        )
        addr_cmd, value_cmd = self.__gen_mdio45("read", phy, dev, reg)

        addr_buf = self.ftdi_prepare_write_buf(addr_opcode, addr_cmd)
        value_buf = self.ftdi_prepare_write_buf(value_opcode, value_cmd)

        self.ftdi_write(addr_buf + value_buf)

        nsend = len(value_cmd)
        timeout = 5
        while (self._dev.getQueueStatus() < nsend and timeout >= 0):
            self._wait()
            timeout -= 1

        total_read = self._dev.getQueueStatus()
        if (total_read < nsend):
            raise Exception("Couldn't read enough bytes")

        rarr = self.ftdi_raw_read(total_read)
        rdata = rarr[6] << 8 | rarr[7];
        return rdata

    def write_mdio22(self, phy, reg, data):
        opcode = self.ftdi_gen_opcode(
            order = self.ORDER_MSB,
            mode = self.MODE_BYTES,
            data_out = self.ENABLE,
            edge_out = self.EDGE_RISING,
        )
        data = self.__gen_mdio22("write", phy, reg, data)
        wbuf = self.ftdi_prepare_write_buf(opcode, data)
        return self.ftdi_write(wbuf)

    def read_mdio22(self, phy, reg):
        opcode = self.ftdi_gen_opcode(
            order = self.ORDER_MSB,
            mode = self.MODE_BYTES,
            data_out = self.ENABLE,
            edge_out = self.EDGE_RISING,
            data_in = self.ENABLE,
            edge_in = self.EDGE_FALLING,
        )
        data = self.__gen_mdio22("read", phy, reg)
        nsend = len(data)
        wbuf = self.ftdi_prepare_write_buf(opcode, data)
        self.ftdi_write(wbuf)

        timeout = 5
        while (self._dev.getQueueStatus() < nsend and timeout >= 0):
            self._wait()
            timeout -= 1

        total_read = self._dev.getQueueStatus()
        if (total_read < nsend):
            raise Exception("Couldn't read enough bytes")

        rarr = self.ftdi_raw_read(total_read)
        rdata = rarr[6] << 8 | rarr[7];
        return rdata


@Driver.register("ftdi")
class FtdiMdio(MdioBase):
    HELP = "\n".join([
        "Control Mdio Over ftdi",
        "URL: ftdi://dev_idx",
        "  dev_id ::= Nil | Int"
    ])

    def _parse_args(self, url):
        args = self.fetch_args(url)
        dev = 0
        if args:
            dev = int(args, 10)
        else:
            devices = FtdiCore.list_devices() or []
            if devices:
                dev = devices[0]
            if not dev:
                dev = 0

        self._dev = dev
        self._ftdi = FtdiCore()

    def open(self):
        self._ftdi.open(self._dev)

    def close(self):
        self._ftdi.close()

    def _read(self, phy, reg):
        return self._ftdi.read_mdio22(phy, reg)

    def _write(self, phy, reg, val):
        return self._ftdi.write_mdio22(phy, reg, val)
