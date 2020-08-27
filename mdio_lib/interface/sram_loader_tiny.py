import sys
import time
from .interface import Interface

MAGIC_COPY = 0x8006
MAGIC_EXECUTE = 0x4000

class RCFDecoder(object):
    '''
    return firmware
    firmware: test.rcf format
     data[0]
     ctrl[0]
     ...
     data[n]
     ctrl[n]
     ...
     0xbeef
    '''
    END_OF_FILE = 0xdead

    MAGIC_EXEC = 0x4000

    @staticmethod
    def bin2int(s):
        if len(s) != 16:
            return None

        bits = map(lambda x: x == "1" and 1 or 0, s)
        val = 0
        for bit in bits:
            val = val << 1
            val += bit
        return val

    def __init__(self, file_name):
        self._name = file_name
        self._file = None
        self._load_firmware()

        self._idx = 0
        self._fw_list = None
        self._split_firmware()

    def get_firmware(self):
        return self._fw

    def _load_firmware(self):
        with open(self._name, "r") as f:
            self._file = f.read()

    def _split_firmware(self):
        # except end of file
        lines = self._file.split("\n")
        data = list(map(self.bin2int, lines))
        assert(data[-1] == self.END_OF_FILE)
        self._fw = data[0:-1]

@Interface.register("sram-loader-tiny", dep = ["mdio"])
class SramLoader:
    PAGE_LOADER = 128

    STATUS_RUNNING = 0x08
    STATUS_FAILED  = 0x10
    STATUS_SUCCESS = 0x20

    ADDR_CTRL = 27
    ADDR_DATA = 28

    def __write(self, reg, value):
        return self.write(reg, value)

    def __read(self, reg):
        return self.read(reg)

    def _wait_op_done(self):
        timeout = 2
        for i in range(timeout):
            cval = self.__read(self.ADDR_CTRL)
            if cval == 0:
                break
        else:
            raise ValueError("timeout")

    def __load_fw_to_sram(self):
        bins = self._fw

        for i in range(0, len(bins), 2):
            data = bins[i]
            ctrl = bins[i+1]
            self.__write(self.ADDR_DATA, data)
            self.__write(self.ADDR_CTRL, ctrl)
            if (ctrl == RCFDecoder.MAGIC_EXEC):
                break

            self._wait_op_done()
            print(i)

    def sram_load(self):
        self.set_page(self.PAGE_LOADER)
        if not self._sram_has_firmware():
            raise Exception("You should config firmware before")

        self.__load_fw_to_sram()

    def sram_status(self):
        self.set_page(self.PAGE_LOADER)
        status = self.__read(self.ADDR_CTRL)
        return (status >> 4) & 0x3f

    def sram_set_firmware(self, path):
        fw = RCFDecoder(path).get_firmware()
        self._fw = fw

    def _sram_has_firmware(self):
        fw = getattr(self, "_fw", None)
        return fw is not None
