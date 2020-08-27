import time
import sys
import csv
import os
import math
import re
import threading

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

sys.path.append("..")
from stream_gui import *
from regfile_gen import *

# =============================================================================
# SMI(MDIO) library
sys.path.append("../lib")
sys.path.append("../lib/mdio_lib")
sys.path.append("../lib/mdio_lib/interface")
sys.path.append("../lib/mdio_lib/driver")
sys.path.append("../lib/mdio_lib/interface/regmap")

from mdio_lib import Driver
from mdio_lib import Interface


#------------------------------------------------------------
class QsetWindow(QWidget, Ui_stream_gui):

    def __init__(self, phydev = None, smi = None):
        super(QsetWindow, self).__init__()

        self.phydev = phydev
        self.smi = smi
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint) # remove frame

        self._center()
        self.connect_flag = 0
        self.enable_flag1 = 0
        self.enable_flag2 = 0
        self.enable_flag_all = 0
        self.suspend_flag1 = 0
        self.suspend_flag2 = 0
        self.suspend_flag_all = 0

        # Multi-thread
        self.work = WorkThread()
        self.execute()

    def __del__(self):
        pass

    def closeEvent(self, event):
    	event.accept()
     	os._exit(0)

    def execute(self):
        self.work.start()
        self.work.trigger.connect(self.refresh_view)

    def _center(self):
        frame_geometry = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(cp)
        self.move(frame_geometry.topLeft())

    def mousePressEvent(self, event):
        """
        get mouse point
        """
        if event.button()==Qt.LeftButton:
            self.m_flag=True
            self.m_Position=event.globalPos()-self.pos() # capture mouse point
            event.accept()
            self.setCursor(Qt.OpenHandCursor)  # change mouse icon

    def mouseMoveEvent(self, QMouseEvent):
        """
        move mouse position
        """
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos()-self.m_Position) # change position
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        """
        mouse cursor -> arrow
        """
        self.m_flag=False
        self.setCursor(Qt.ArrowCursor)


    def show_activitylog(self, mode, string):
        curr_time = time.strftime("%H:%M:%S", time.localtime())
        if(mode):
            # red
            self.log_info.append("<font color=\"#FF0000\">" + curr_time + "[Error] " + string + "</font>")
        else:
            # green
            self.log_info.append("<font color=\"#008000\">" + curr_time + "[Info] " +string + "</font>")


    #--------- gui event ---------------------
    @pyqtSlot(bool)
    def on_close_main_win_clicked(self):
        """
        close all wimdow
        """
        self.close()

    @pyqtSlot()
    def on_minimize_main_win_clicked(self):
        """
        minimize window
        """
        self.showMinimized()

    @pyqtSlot(bool)
    def on_btnClrLog_clicked(self):
        self.log_info.clear()

    @pyqtSlot(bool)
    def on_btnConnect_clicked(self):
        """
        open usb connect
        """
        print(self.connect_flag)
        # todo how to connect USB
        try:
            if(self.connect_flag == 0):
                self.smi.open()
                self.smi.dev_sel(3)
                self.phydev.config_phyid(0)
                self.btnConnect.setText('Close')
                self.mdio_is_connect = 1;
                print("Connect")
                self.show_activitylog(0, "MDIO dongle is connected.")
            else:
                self.smi.close()
                self.btnConnect.setText('Connect')
                self.mdio_is_connect = 0;
                print("Close")
                self.show_activitylog(0, "MDIO dongle is closed.")

            self.connect_flag = ~self.connect_flag
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")


    @pyqtSlot(bool)
    def on_btnSetConfig_clicked(self):
        """
        apply: get all config
        """
        try:
            self.get_gui_val()
            self.set_regfile_val()
            self.show_activitylog(0, "Config Success!")
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")


    def get_gui_val(self):
        self.get_payload     = self.payload_combo.currentIndex()
        self.get_length      = self.length_combo.currentIndex()
        self.get_type        = self.type_combo.currentIndex()
        self.get_send_mode   = self.send_combo.currentIndex()
        self.get_IPG1        = self.IPG1.text()
        self.get_IPG2        = self.IPG2.text()
        self.get_payload_val = self.payload_val.text()
        self.get_length_val  = self.length_val.text()
        self.get_pkt_num     = self.pkt_num.text()

    def set_regfile_val(self):
        print(self.get_payload)
        print(self.get_length)
        print(self.get_type)
        print(self.get_send_mode)
        print(self.get_IPG1)
        print(self.get_IPG2)
        print(self.get_payload_val)
        print(self.get_length_val)
        print(self.get_pkt_num)

        self.phydev.set_payload_mode(3 - int(self.get_payload))
        self.phydev.set_length_mode(1 - int(self.get_length))
        self.phydev.set_tx1_mode(1 - int(self.get_send_mode))
        self.phydev.set_tx2_mode(1 - int(self.get_send_mode))

        self.phydev.set_length_init(int(self.get_length_val))
        self.phydev.set_payload_init_val(int(self.get_payload_val, 16))

        # IPG clac
        if(self.get_type == 0):
            step1 = 100.0 / int(self.get_IPG1)
            step2 = 100.0 / int(self.get_IPG2)
        else:
            step1 = 10.0 / int(self.get_IPG1)
            step2 = 10.0 / int(self.get_IPG2)

        ipg_num1 = int(step1 * 12)
        ipg_num2 = int(step2 * 12)

        print(ipg_num1)
        print(ipg_num2)

        self.phydev.set_phy1_ipg(ipg_num1)
        self.phydev.set_phy2_ipg(ipg_num2)

        # tx pkt calc
        tx_pkt_lo = (int(self.get_pkt_num)) & 0xffff
        tx_pkt_mi = (int(self.get_pkt_num)>>16) & 0xffff
        tx_pkt_hi = (int(self.get_pkt_num)>>32) & 0xffff

        self.phydev.set_pkt_count_hi(tx_pkt_hi)
        self.phydev.set_pkt_count_mi(tx_pkt_mi)
        self.phydev.set_pkt_count_lo(tx_pkt_lo)

    #----------------------------------------------------
    def get_tx_count_val(self):
        tx1_count_hi = self.phydev.get_tx1_count_hi()
        tx1_count_mi = self.phydev.get_tx1_count_mi()
        tx1_count_lo = self.phydev.get_tx1_count_lo()
        self.tx1_count = tx1_count_hi*(2**32) + tx1_count_mi*(2**16) + tx1_count_lo

        tx2_count_hi = self.phydev.get_tx2_count_hi()
        tx2_count_mi = self.phydev.get_tx2_count_mi()
        tx2_count_lo = self.phydev.get_tx2_count_lo()
        self.tx2_count = tx2_count_hi*(2**32) + tx2_count_mi*(2**16) + tx2_count_lo

        self.tx_pkt_cnt.setText(str(self.tx1_count))
        self.tx_pkt_cnt_2.setText(str(self.tx2_count))

    def get_rx_count_val(self):
        rx1_count_hi = self.phydev.get_rx1_count_hi()
        rx1_count_mi = self.phydev.get_rx1_count_mi()
        rx1_count_lo = self.phydev.get_rx1_count_lo()
        self.rx1_count = rx1_count_hi*(2**32) + rx1_count_mi*(2**16) + rx1_count_lo

        rx2_count_hi = self.phydev.get_rx2_count_hi()
        rx2_count_mi = self.phydev.get_rx2_count_mi()
        rx2_count_lo = self.phydev.get_rx2_count_lo()
        self.rx2_count = rx2_count_hi*(2**32) + rx2_count_mi*(2**16) + rx2_count_lo

        rx1_crc_hi = self.phydev.get_rx1_crc_err_hi()
        rx1_crc_mi = self.phydev.get_rx1_crc_err_mi()
        rx1_crc_lo = self.phydev.get_rx1_crc_err_lo()
        self.rx1_crc = rx1_crc_hi*(2**32) + rx1_crc_mi*(2**16) + rx1_crc_lo

        rx2_crc_hi = self.phydev.get_rx2_crc_err_hi()
        rx2_crc_mi = self.phydev.get_rx2_crc_err_mi()
        rx2_crc_lo = self.phydev.get_rx2_crc_err_lo()
        self.rx2_crc = rx2_crc_hi*(2**32) + rx2_crc_mi*(2**16) + rx2_crc_lo

        self.rx_pkt_cnt.setText(str(self.rx1_count))
        self.rx_pkt_cnt_2.setText(str(self.rx2_count))
        self.rx_crc_cnt.setText(str(self.rx1_crc))
        self.rx_crc_cnt_2.setText(str(self.rx2_crc))

    def refresh_view(self):
        try:
            self.get_tx_count_val()
            self.get_rx_count_val()
        except:
            self.init_view()

    def init_view(self):
        self.tx_start_time.setText('0')
        self.tx_end_time.setText('0')
        self.tx_start_time_2.setText('0')
        self.tx_end_time_2.setText('0')
        self.tx_pkt_cnt.setText('0')
        self.tx_pkt_cnt_2.setText('0')
        self.rx_pkt_cnt.setText('0')
        self.rx_pkt_cnt_2.setText('0')
        self.rx_crc_cnt.setText('0')
        self.rx_crc_cnt_2.setText('0')

    @pyqtSlot(bool)
    def on_Send_clicked(self):
        """
        apply: start tx1 send
        """
        try:
            if(self.enable_flag1 == 0):
                self.phydev.set_tx1_enable(1)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_green_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send.setIcon(icon1)
                self.Send.setIconSize(QtCore.QSize(36, 36))

                # get current time
                curTime = QDateTime.currentDateTime()
                self.tx_start_time.setText(curTime.toString())
                self.tx_end_time.setText('0')

                self.show_activitylog(0, "Phy1 Stream Send!")

            else:
                self.phydev.set_tx1_enable(0)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send.setIcon(icon1)
                self.Send.setIconSize(QtCore.QSize(36, 36))

                # get current time
                curTime = QDateTime.currentDateTime()
                self.tx_end_time.setText(curTime.toString())

                self.show_activitylog(0, "Phy1 Stream Stop!")

            self.enable_flag1 = ~self.enable_flag1
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot(bool)
    def on_Send_2_clicked(self):
        """
        apply: start tx2 send
        """
        try:
            if(self.enable_flag2 == 0):
                self.phydev.set_tx2_enable(1)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_green_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send_2.setIcon(icon1)
                self.Send_2.setIconSize(QtCore.QSize(36, 36))

                # get current time
                curTime = QDateTime.currentDateTime()
                self.tx_start_time_2.setText(curTime.toString())
                self.tx_end_time_2.setText('0')

                self.show_activitylog(0, "Phy2 Stream Send!")
            else:
                self.phydev.set_tx2_enable(0)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send_2.setIcon(icon1)
                self.Send_2.setIconSize(QtCore.QSize(36, 36))

                # get current time
                curTime = QDateTime.currentDateTime()
                self.tx_end_time_2.setText(curTime.toString())

                self.show_activitylog(0, "Phy2 Stream Stop!")

            self.enable_flag2 = ~self.enable_flag2
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot(bool)
    def on_Send_all_clicked(self):
        """
        apply: start tx all send
        """
        try:
            if(self.enable_flag_all == 0):
                self.phydev.get_chip_ver()
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_green_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send_all.setIcon(icon1)
                self.Send_all.setIconSize(QtCore.QSize(36, 36))

                if(~self.enable_flag1):
                    self.on_Send_clicked()

                if(~self.enable_flag2):
                    self.on_Send_2_clicked()
            else:
                self.phydev.get_chip_ver()
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_play_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Send_all.setIcon(icon1)
                self.Send_all.setIconSize(QtCore.QSize(36, 36))

                if(self.enable_flag1):
                    self.on_Send_clicked()

                if(self.enable_flag2):
                    self.on_Send_2_clicked()

            self.enable_flag_all = ~self.enable_flag_all
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot(bool)
    def on_Stop_clicked(self):
        """
        apply: start tx1 suspend
        """
        try:
            if(self.suspend_flag1 == 0):
                self.phydev.set_tx1_suspend(1)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_red_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop.setIcon(icon1)
                self.Stop.setIconSize(QtCore.QSize(36, 36))
                self.show_activitylog(0, "Phy1 Stream Suspend!")
            else:
                self.phydev.set_tx1_suspend(0)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop.setIcon(icon1)
                self.Stop.setIconSize(QtCore.QSize(36, 36))
                self.show_activitylog(0, "Phy1 Stream Continue!")

            self.suspend_flag1 = ~self.suspend_flag1
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot(bool)
    def on_Stop_2_clicked(self):
        """
        apply: start tx2 suspend
        """
        try:
            if(self.suspend_flag2 == 0):
                self.phydev.set_tx2_suspend(1)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_red_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop_2.setIcon(icon1)
                self.Stop_2.setIconSize(QtCore.QSize(36, 36))
                self.show_activitylog(0, "Phy2 Stream Suspend!")
            else:
                self.phydev.set_tx2_suspend(0)
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop_2.setIcon(icon1)
                self.Stop_2.setIconSize(QtCore.QSize(36, 36))
                self.show_activitylog(0, "Phy2 Stream Continue!")

            self.suspend_flag2 = ~self.suspend_flag2
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot(bool)
    def on_Stop_all_clicked(self):
        """
        apply: start tx all send
        """
        try:
            if(self.suspend_flag_all == 0):
                self.phydev.get_chip_ver()
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_red_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop_all.setIcon(icon1)
                self.Stop_all.setIconSize(QtCore.QSize(36, 36))

                if(~self.suspend_flag1):
                    self.on_Stop_clicked()

                if(~self.suspend_flag2):
                    self.on_Stop_2_clicked()
            else:
                self.phydev.get_chip_ver()
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/pic/ic_pause_circle_outline_white_36dp.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
                self.Stop_all.setIcon(icon1)
                self.Stop_all.setIconSize(QtCore.QSize(36, 36))

                if(self.suspend_flag1):
                    self.on_Stop_clicked()

                if(self.suspend_flag2):
                    self.on_Stop_2_clicked()

            self.suspend_flag_all = ~self.suspend_flag_all
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot()
    def on_Clear_clicked(self):
        try:
            # clear time 0
            self.tx_start_time.setText('0')
            self.tx_end_time.setText('0')
            # clear FPGA count
            self.phydev.set_phy1_count_clr(1)
            self.phydev.set_phy1_count_clr(0)

            self.show_activitylog(0, "Phy1 Count Clear!")
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot()
    def on_Clear_2_clicked(self):
        try:
            # clear time 0
            self.tx_start_time_2.setText('0')
            self.tx_end_time_2.setText('0')
            # clear FPGA count
            self.phydev.set_phy2_count_clr(1)
            self.phydev.set_phy2_count_clr(0)

            self.show_activitylog(0, "Phy2 Count Clear!")
        except:
            self.show_activitylog(1, "Please plug in MDIO dongle!")

    @pyqtSlot()
    def on_Clear_all_clicked(self):
        self.on_Clear_clicked()
        self.on_Clear_2_clicked()

class WorkThread(QThread):
    trigger = pyqtSignal()

    def __int__(self):
        super(WorkThread, self).__init__()

    # Refresh Status
    def run(self):
        while True:
            time.sleep(1)
            self.trigger.emit()

"""
main
"""
def main():
    print("all interfaces:", Interface.list())

    driver = Driver.find("mcp2210://")
    target = Interface.equip(driver, "mdio", "reg_fields")

    print(driver)
    print(target)

    app = QtWidgets.QApplication(sys.argv)
    ui = QsetWindow(phydev = target, smi = driver)
    ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


