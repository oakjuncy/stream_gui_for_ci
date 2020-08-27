import sys
import time
from .interface import Interface

MAGIC_COPY = 0x8006
MAGIC_EXECUTE = 0x4000

class RCFDecoder(object):
    '''
    return firmware
    firmware: test.rcf format
     |  DataBlock 1
     |   |  data[0] # DATA[0], block address high
     |   |  data[1] # DATA[1], block address low
     |   |  data[2] # DATA[2] block data 0
     |   |  ...
     |   |  data[6] # DATA[6], block data 4
     |   |  data[7] # DATA[7], block data 5
     |   |  0x8006  # CONTROLL, op_copy(addr, data, len = 6)
     |  ...
     |  DataBlock n
     |  EndBlock:
     |   |  0xbeef  # indicate end of data
     |   |  ${pc-high} # DATA[0] pc-high
     |   |  ${pc-low}  # DATA[1] pc-low
     |   |  0x4000     # CONTROLL, execute firmware
    EndBlock:
        0xdeef      # indicate end of file
    '''

    END_OF_DATA = 0xbeef
    END_OF_FILE = 0xdeef

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

    class Firmware():
        BLOCK_SIZE_FIXED = True
        DATA_SIZE = 8 # pc(2) + data(6)
        OP_SIZE = 1

        BLOCK_SIZE = DATA_SIZE + OP_SIZE

        def __init__(self, data, pc, exec_code):
            self.data = data
            self.pc = pc
            self.exec_code = exec_code

        def blocks(self):
            '''
            return [
                ([addr_high, addr_low, data0, ...], op),
                ...
            ]
            '''
            blocks = list()
            if not self.BLOCK_SIZE_FIXED:
                return

            offset = 0

            while offset + self.BLOCK_SIZE <= len(self.data):
                d = self.data[offset: offset + self.DATA_SIZE]
                o = self.data[offset + self.DATA_SIZE]
                offset += self.BLOCK_SIZE
                if o != MAGIC_COPY:
                    raise Exception("Error: sending data size must be 6")
                blocks.append((d, o))

            return blocks

    def __init__(self, file_name):
        self._name = file_name
        self._file = None
        self._load_firmware()

        self._idx = 0
        self._fw_list = None
        self._split_firmware()

    def next_firmware(self):
        if self._idx >= len(self._fw_list):
            return None

        fw = self._fw_list[self._idx]
        self._idx += 1
        return fw

    def _load_firmware(self):
        with open(self._name, "r") as f:
            self._file = f.read()

    def _split_firmware(self):
        # except end of file
        lines = self._file.split("\n")
        data = list(map(self.bin2int, lines))
        assert(data[-1] == self.END_OF_FILE)

        fw_list = list()

        size = len(data)
        blk_size = self.Firmware.BLOCK_SIZE
        offset = 0
        l = list()
        while offset + blk_size < size:
            l.extend(data[offset:offset + blk_size])
            offset += blk_size

            if data[offset] != self.END_OF_DATA:
                continue

            pc = (data[offset + 1], data[offset + 2])
            exec_code = data[offset + 3]
            assert(exec_code == MAGIC_EXECUTE)
            fw_list.append(self.Firmware(l, pc, exec_code))
            offset += 4
            l = list()

        self._fw_list = fw_list

    def firmware_number(self):
        return len(self._fw_list)

@Interface.register("sram-loader", dep = ["mdio"])
class SramLoader:
    PAGE_LOADER = 18

    STATUS_RUNNING = 0x08
    STATUS_FAILED  = 0x10
    STATUS_SUCCESS = 0x20

    CPU_IDX = 16
    DATA_BASE = 17


    def __write(self, reg, value):
        return self.write(reg, value)

    def __read(self, reg):
        return self.read(reg)

    def __copy_fw_to_sram(self):
        # control reg & data reg
        creg = self._sram_target()
        dreg = self.DATA_BASE
        fw = self._fw
        idx = 0
        for b in fw.blocks():
            data = b[0]
            op = b[1]
            for i in range(len(data)):
                self.__write(dreg + i, data[i])
            self.__write(creg, op)
            ret = self.__read(creg)
            if ret != 0:
                print(data, ret)
                raise Exception
            idx += 1

    def __exec(self):
        # control reg & data reg
        creg = self._sram_target()
        dreg = self.DATA_BASE
        fw = self._fw
        self.__write(dreg, fw.pc[0])
        self.__write(dreg + 1, fw.pc[1])
        self.__write(creg, fw.exec_code)

    def sram_load(self):
        self.set_page(self.PAGE_LOADER)
        if not self._sram_has_firmware():
            raise Exception("You should config firmware before")

        self.__copy_fw_to_sram()
        self.__exec()

    def sram_status(self):
        self.set_page(self.PAGE_LOADER)
        status = self.__read(self._sram_target())
        return (status >> 4) & 0x3f

    def _sram_target(self):
        return self.CPU_IDX

    def sram_set_firmware(self, path):
        fw = RCFDecoder(path).next_firmware()
        self._fw = fw

    def _sram_has_firmware(self):
        fw = getattr(self, "_fw", None)
        return fw is not None
