import time
from .ftd2xx import ftd2xx
from .ftd2xx.ftd2xx import FTD2XX

__INNER_DEBUG__ = False

class FTD232HLConfig():
    class FTDConfigError(Exception): pass
    class ErrorInvalidOP(FTDConfigError): pass
    class ErrorInvalidType(FTDConfigError): pass
    class ErrorInvalidValue(FTDConfigError): pass

    LOW_BYTES  = 0
    HIGH_BYTES = 1

    LEVEL_LOW  = 0
    LEVEL_HIGH = 1

    # OP code config
    EDGE_FALLING = 1
    EDGE_RISING  = 0

    ENABLE  = 1
    DISABLE = 0

    MODE_BIT   = 1
    MODE_BYTES = 0

    ORDER_MSB = 0
    ORDER_LSB = 1

    # bitmode
    BITMODE_RESET = 0x00
    BITMODE_MPSSE = 0x02

    # some op code
    OP_CONFIG_DIVSIOR = 0x86
    OP_SEND_IMMEDIATE = 0x87
    OP_3PHASE_DISABLE = 0x8d
    OP_3PHASE_ENABLE  = 0x8c
    OP_DIVIDE_5_TURN_ON  = 0x8b
    OP_DIVIDE_5_TURN_OFF = 0x8a
    OP_ADAPTIVE_CLK_ENABLE  = 0x96
    OP_ADAPTIVE_CLK_DISABLE = 0x97

    class GPIO():
        def __init__(self, site, bit):
            #assert(site in [self.LOW_BYTES, self.HIGH_BYTES])
            #assert(bit in range(8))
            self._val = (site, bit)

        def val(self):
            return self._val

    GPIO_CLK  = GPIO(LOW_BYTES, 0)
    GPIO_MOSI = GPIO(LOW_BYTES, 1)
    GPIO_MISO = GPIO(LOW_BYTES, 2)
    GPIO_CS   = GPIO(LOW_BYTES, 3)
    GPIO_LE   = GPIO(HIGH_BYTES, 0)

    @classmethod
    def ftdi_gen_opcode(cls, **kw):
        tsm_data = 0
        reserve  = 0
        mode     = kw.get("mode"    , cls.MODE_BYTES)
        order    = kw.get("order"   , cls.ORDER_LSB)
        data_in  = kw.get("data_in" , cls.DISABLE)
        data_out = kw.get("data_out", cls.DISABLE)
        edge_in  = kw.get("edge_in" , cls.EDGE_RISING)
        edge_out = kw.get("edge_out", cls.EDGE_RISING)

        if __INNER_DEBUG__:
            if order not in [cls.ORDER_MSB, cls.ORDER_LSB]:
                raise cls.ErrorInvalidType
            if mode not in [cls.MODE_BIT, cls.MODE_BYTES]:
                raise cls.ErrorInvalidType
            if data_in  not in [cls.ENABLE, cls.DISABLE]:
                raise cls.ErrorInvalidType
            if data_out not in [cls.ENABLE, cls.DISABLE]:
                raise cls.ErrorInvalidType
            if edge_in  not in [cls.EDGE_FALLING, cls.EDGE_RISING]:
                raise cls.ErrorInvalidType
            if edge_out  not in [cls.EDGE_FALLING, cls.EDGE_RISING]:
                raise cls.ErrorInvalidType
        opcode = 0x00
        opcode |= edge_out << 0
        opcode |= mode     << 1
        opcode |= edge_in  << 2
        opcode |= order    << 3
        opcode |= data_out << 4
        opcode |= data_in  << 5
        opcode |= tsm_data << 6
        opcode |= reserve  << 7
        return opcode

    @staticmethod
    def ftdi_prepare_write_buf(cmd, data):
        '''
        cmd: uint8
        data: uint8[]
        '''
        buf = list()
        nsend = len(data)
        length = nsend - 1
        buf.append(cmd)
        buf.append(length & 0xff)
        buf.append((length >> 8) & 0Xff)
        buf.extend(data)
        return buf

    @classmethod
    def ftdi_prepare_gpio_out(cls, byte_type, bit_dict):
        '''
        byte_type: LOW_BYTES | HIGH_BYTES
        bit_dict = {bit(0~7):level(0 | 1) ..}
        '''
        if (type(bit_dict) != dict): raise cls.ErrorInvalidType
        op_dict = {
            cls.LOW_BYTES:  0x80,
            cls.HIGH_BYTES: 0x82,
        }
        op = op_dict.get(byte_type, None)
        if op is None:
            raise cls.ErrorInvalidValue

        value = 0x00
        direction = 0x00
        for bit, level in bit_dict.items():
            direction |= 1 << bit
            value     |= level << bit

        buf = [op, value, direction]
        return buf

    @classmethod
    def ftdi_prepare_gpio_in(cls, byte_type):
        '''
        byte_type: LOW_BYTES | HIGH_BYTES
        '''
        op_dict = {
            cls.LOW_BYTES:  0x81,
            cls.HIGH_BYTES: 0x83,
        }
        op = op_dict.get(byte_type, None)
        if op is None:
            raise cls.ErrorInvalidValue
        return [op]

class FTD232HL(FTD232HLConfig):
    def __init__(self):
        self._dev = None
        self.divisor = 0x001d
        self.timeout_read  = 100
        self.timeout_write = 5000
        self.op_divide_5_on = self.OP_DIVIDE_5_TURN_OFF
        self.op_adaptive_clk_en = self.OP_ADAPTIVE_CLK_DISABLE
        self.op_3phase_en = self.OP_3PHASE_DISABLE

        self._gpio_config = {}

    @staticmethod
    def _wait():
        time.sleep(0.005)

    @staticmethod
    def _long_wait():
        time.sleep(0.05)

    @staticmethod
    def str2arr(s):
        return [c for c in s]

    @staticmethod
    def arr2str(arr):
        blist = map(lambda x: 0xff & x, arr)
        return bytes(bytearray(blist))

    @staticmethod
    def int2uint8s(num, length = 4):
        l = []
        for i in range(length):
            l.append(num & 0xff)
            num >>= 8
        l.reverse()
        return l

    @staticmethod
    def int2bits(num, length = 32):
        l = []
        for i in range(length):
            l.append(num & 0x1)
            num >>= 1
        l.reverse()
        return l

    @staticmethod
    def __open_device(dev = 0):
        dev = ftd2xx.open(dev)
        return dev

    @staticmethod
    def list_devices(flags = 0):
        return ftd2xx.listDevices(flags)

    def open(self, dev = 0):
        self._dev = self.__open_device(dev)
        self.__config_device()

    def close(self):
        self._dev.close()

    def ftdi_gpio_init(self, gpio, level):
        assert(isinstance(gpio, self.GPIO))
        assert(level in [self.LEVEL_LOW, self.LEVEL_HIGH])
        self._gpio_config[gpio.val()] = level

    def ftdi_write(self, buf):
        s = self.arr2str(buf)
        return self._dev.write(s)

    def ftdi_raw_read(self, nbytes):
        rbuf = self._dev.read(nbytes)
        return self.str2arr(rbuf)

    def ftdi_read(self, nbytes):
        timeout = 5
        while(self._dev.getQueueStatus() < nbytes and timeout >= 0):
            self._wait()
            timeout -= 1

        total_read = self._dev.getQueueStatus()
        if (total_read < nbytes):
            raise Exception("Couldn't read enough bytes")

        rarr = self.ftdi_raw_read(total_read)
        return rarr

    def ftdi_dump_dev_info(self):
        print(self._dev.getModemStatus())
        print(self._dev.getQueueStatus())
        print(self._dev.getStatus())
        print(self._dev.getEventStatus())
        print(self._dev.getLatencyTimer())
        print(self._dev.getBitMode())
        print(self._dev.getDeviceInfo())
        print(self._dev.getDriverVersion())

    def __config_device(self):
        dev = self._dev
        dev.resetDevice()
        before_read = dev.getQueueStatus()
        if (before_read > 0):
            dev.read(before_read)

        dev.setTimeouts(self.timeout_read, self.timeout_write)
        dev.setBitMode(0x00, self.BITMODE_RESET)
        dev.setBitMode(0x0b, self.BITMODE_MPSSE)
        self._wait()

        buf = list()
        buf.append(self.op_divide_5_on)
        buf.append(self.op_adaptive_clk_en)
        buf.append(self.op_3phase_en)
        self.ftdi_write(buf)
        self._wait()

        divisor = self.divisor
        gpio_config = self.__gpio_config()

        buf = list()
        buf.extend(gpio_config)
        buf.extend([self.OP_CONFIG_DIVSIOR, divisor & 0xff, divisor >> 8])
        self.ftdi_write(buf)
        self._wait()

        dev.purge()
        self._long_wait()
        return dev

    def __gpio_config(self):
        gpio_dict = {
            self.LOW_BYTES:{},
            self.HIGH_BYTES:{},
        }

        cfg = self._gpio_config
        for gpio, level in cfg.items():
            site, bit = gpio
            d = gpio_dict[site]
            d[bit] = level

        buf = list()
        for site in [self.LOW_BYTES, self.HIGH_BYTES]:
            d = gpio_dict[site]
            if len(d.items()) == 0:
                continue
            gpio_code = self.ftdi_prepare_gpio_out(site, gpio_dict[site])
            buf.extend(gpio_code)

        return buf
