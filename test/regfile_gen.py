class RegAccessor(object):
    '''
    @autogen at 2020 Aug 27, based on doc/EthStream_RegMap_Rev-0.14.csv
    '''


    def get_chip_ver(self):
        """
        CHIP_VER
        """
        res = self.read(0x1)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_length_init(self):
        """
        pkt length initial val (64)
        """
        res = self.read(0x3)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_length_mode(self):
        """
        0: fixed len 
        1: random
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x200) >> 0x9

    def get_payload_init_val(self):
        """
        fixed payload val
        """
        res = self.read(0x4)
        if res is None:
            return None
        return (res & 0xff) >> 0x0

    def get_payload_mode(self):
        """
        0: fixed,    1: incr, 
        2: decr, 3: random
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0xc00) >> 0xa

    def get_phy1_count_clr(self):
        """
        1 -> 0 : clear count
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x4) >> 0x2

    def get_phy1_ipg(self):
        """
        phy1 ipg [15:0]
        """
        res = self.read(0x1a)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_phy2_count_clr(self):
        """
        1 -> 0 : clear count
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x8) >> 0x3

    def get_phy2_ipg(self):
        """
        phy2 ipg [15:0]
        """
        res = self.read(0x1b)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_pkt_count_hi(self):
        """
        send count [47:31]
        """
        res = self.read(0x5)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_pkt_count_lo(self):
        """
        send count [15:0]
        """
        res = self.read(0x7)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_pkt_count_mi(self):
        """
        send count [32:16]
        """
        res = self.read(0x6)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_count_hi(self):
        """
        phy1 total receive cnt [47:32]
        """
        res = self.read(0xe)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_count_lo(self):
        """
        phy1 total receive cnt [15:0]
        """
        res = self.read(0x10)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_count_mi(self):
        """
        phy1 total receive cnt [31:16]
        """
        res = self.read(0xf)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_crc_err_hi(self):
        """
        phy1 crc error cnt [47:32]
        """
        res = self.read(0xb)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_crc_err_lo(self):
        """
        phy1 crc error cnt [15:0]
        """
        res = self.read(0xd)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx1_crc_err_mi(self):
        """
        phy1 crc error cnt [31:16]
        """
        res = self.read(0xc)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_count_hi(self):
        """
        phy2 total receive cnt [47:32]
        """
        res = self.read(0x17)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_count_lo(self):
        """
        phy2 total receive cnt [15:0]
        """
        res = self.read(0x19)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_count_mi(self):
        """
        phy2 total receive cnt [31:16]
        """
        res = self.read(0x18)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_crc_err_hi(self):
        """
        rx2 crc error cnt [47:32]
        """
        res = self.read(0x14)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_crc_err_lo(self):
        """
        rx2 crc error cnt [15:0]
        """
        res = self.read(0x16)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_rx2_crc_err_mi(self):
        """
        rx2 crc error cnt [31:16]
        """
        res = self.read(0x15)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx1_count_hi(self):
        """
        total tx1 count [47:32]
        """
        res = self.read(0xa)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx1_count_lo(self):
        """
        total tx1 count [15:0]
        """
        res = self.read(0x8)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx1_count_mi(self):
        """
        total tx1 count [31:16]
        """
        res = self.read(0x9)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx1_done(self):
        """
        1: pkt send done
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x1) >> 0x0

    def get_tx1_enable(self):
        """
        1: start send pkt
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x8000) >> 0xf

    def get_tx1_mode(self):
        """
        0: fixed count of pkts 
        1: continuous
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x4000) >> 0xe

    def get_tx1_suspend(self):
        """
        0: continuous 
        1: suspend
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x100) >> 0x8

    def get_tx2_count_hi(self):
        """
        total tx2 count [47:32]
        """
        res = self.read(0x13)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx2_count_lo(self):
        """
        total tx2 count [15:0]
        """
        res = self.read(0x11)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx2_count_mi(self):
        """
        total tx2 count [31:16]
        """
        res = self.read(0x12)
        if res is None:
            return None
        return (res & 0xffff) >> 0x0

    def get_tx2_done(self):
        """
        1: pkt send done
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x2) >> 0x1

    def get_tx2_enable(self):
        """
        1: start send pkt
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x2000) >> 0xd

    def get_tx2_mode(self):
        """
        0: fixed count of pkts 
        1: continuous
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x1000) >> 0xc

    def get_tx2_suspend(self):
        """
        0: continuous 
        1: suspend
        """
        res = self.read(0x2)
        if res is None:
            return None
        return (res & 0x80) >> 0x7

    def set_length_init(self, val, raw = False):
        """
        pkt length initial val (64)
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x3)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x3, v)
        return True

    def set_length_mode(self, val, raw = False):
        """
        0: fixed len 
        1: random
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x200 == 0xffff)
        v = (val << 0x9) & 0x200

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x200
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_payload_init_val(self, val, raw = False):
        """
        fixed payload val
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xff == 0xffff)
        v = (val << 0x0) & 0xff

        v_ori = 0 if raw else self.read(0x4)
        if v_ori is None:
            return False

        v_ori &= ~0xff
        v = v | v_ori
        self.write(0x4, v)
        return True

    def set_payload_mode(self, val, raw = False):
        """
        0: fixed,    1: incr, 
        2: decr, 3: random
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xc00 == 0xffff)
        v = (val << 0xa) & 0xc00

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0xc00
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_phy1_count_clr(self, val, raw = False):
        """
        1 -> 0 : clear count
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x4 == 0xffff)
        v = (val << 0x2) & 0x4

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x4
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_phy1_ipg(self, val, raw = False):
        """
        phy1 ipg [15:0]
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x1a)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x1a, v)
        return True

    def set_phy2_count_clr(self, val, raw = False):
        """
        1 -> 0 : clear count
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x8 == 0xffff)
        v = (val << 0x3) & 0x8

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x8
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_phy2_ipg(self, val, raw = False):
        """
        phy2 ipg [15:0]
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x1b)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x1b, v)
        return True

    def set_pkt_count_hi(self, val, raw = False):
        """
        send count [47:31]
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x5)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x5, v)
        return True

    def set_pkt_count_lo(self, val, raw = False):
        """
        send count [15:0]
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x7)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x7, v)
        return True

    def set_pkt_count_mi(self, val, raw = False):
        """
        send count [32:16]
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0xffff == 0xffff)
        v = (val << 0x0) & 0xffff

        v_ori = 0 if raw else self.read(0x6)
        if v_ori is None:
            return False

        v_ori &= ~0xffff
        v = v | v_ori
        self.write(0x6, v)
        return True

    def set_tx1_enable(self, val, raw = False):
        """
        1: start send pkt
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x8000 == 0xffff)
        v = (val << 0xf) & 0x8000

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x8000
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_tx1_mode(self, val, raw = False):
        """
        0: fixed count of pkts 
        1: continuous
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x4000 == 0xffff)
        v = (val << 0xe) & 0x4000

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x4000
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_tx1_suspend(self, val, raw = False):
        """
        0: continuous 
        1: suspend
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x100 == 0xffff)
        v = (val << 0x8) & 0x100

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x100
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_tx2_enable(self, val, raw = False):
        """
        1: start send pkt
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x2000 == 0xffff)
        v = (val << 0xd) & 0x2000

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x2000
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_tx2_mode(self, val, raw = False):
        """
        0: fixed count of pkts 
        1: continuous
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x1000 == 0xffff)
        v = (val << 0xc) & 0x1000

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x1000
        v = v | v_ori
        self.write(0x2, v)
        return True

    def set_tx2_suspend(self, val, raw = False):
        """
        0: continuous 
        1: suspend
        """
        # Check whether bitmask is 0xffff
        raw = raw or (0x80 == 0xffff)
        v = (val << 0x7) & 0x80

        v_ori = 0 if raw else self.read(0x2)
        if v_ori is None:
            return False

        v_ori &= ~0x80
        v = v | v_ori
        self.write(0x2, v)
        return True

    def __init__(self, spi):
        self._spi = spi


    def read(self, reg):
        return self._spi.read(reg)


    def write(self, reg, val):
        self._spi.write(reg, val)
