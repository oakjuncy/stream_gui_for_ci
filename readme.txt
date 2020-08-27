FPGA必须下载好代码, 或者烧写好flash,否则mdio不工作.

1.$ cd test
2.$ ipython3
3.执行下列命令
	In [1]: from stream_mdio import *
	In [2]: chip = StreamMdio()
	In [3]: hex(chip.get_chip_ver())
	Out[3]: '0xbeef'
	In [4]: chip.tx_config_send()
	In [5]: chip.print_count()
	tx1 count 0xfa0d0
	rx1 count 0x15ad29
	rx1 crc 0x0
	tx2 count 0x15ad29
	rx2 count 0xfa0d0
	rx2 crc 0x0
	In [6]: 

