import serial
import serial.tools.list_ports
import sys
import datetime
from PyQt5.QtWidgets import QLabel, QVBoxLayout

import time
import warnings
import numpy as np
# importing Qt widgets
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt

class Time2(QtWidgets.QMainWindow):

    submitted = pyqtSignal(str,float)

    def __init__(self):
        super().__init__()

        # self.mainWindow = Time()
        # Load the UI Page
        uic.loadUi("timewindow.ui", self)

        self.hours = None
        self.hours_str = None
        self.minutes = None
        self.minutes_str = None
        self.uftime = None
        self.uftime_str = None
        self.ok_btn.clicked.connect(lambda: self.ok())

    def ok(self):
        self.hours = self.h_spinbox.value()
        self.minutes = self.m_spinbox.value()
        self.hours_str = f'{self.hours}'
        self.minutes_str = f'{self.minutes}'
        # satuan detik(second) buat countdown
        self.uftime = (self.hours * 60 + self.minutes) * 60
        print(self.uftime,"second")
        print(self.minutes, "menit")
        if self.hours < 10:
            self.hours_str = f'0{self.hours}'
        if self.minutes < 10:
            self.minutes_str = f'0{self.minutes}'
        self.uftime_str = f'{self.hours_str}:{self.minutes_str}'
        # self.ok_btn.setText(self.uftime_str)
        # Time.uftime = self.total_tim
        # self.on_submit()

        self.submitted.emit(self.uftime_str,
                            self.uftime)
        self.close()


class Time(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Time, self).__init__(*args, **kwargs)
        self.w = None
        # Load the UI Page
        uic.loadUi("time2.ui", self)

        self.uftime = 0
        self.uftime_str = ''

        self.uftime_button.clicked.connect(lambda : self.add_window('1'))
        self.ufrmv_button.clicked.connect(lambda: self.add_window('2'))
        self.show()

    # @pyqtSlot(str,float)
    def update_time(self, uftime_str, uftime):
        self.uftime_str = uftime_str
        self.uftime = uftime

        if self.button == '1':
            self.uftime_button.setText(self.uftime_str)
        elif self.button == '2':
            self.ufrmv_button.setText(self.uftime_str)

    def add_window(self,button):
        self.button = button
        # if self.w is None:
        #     self.w = Time2()
        #     self.w.on_submit.connect(self.update_time)
        #     self.w.show()
        #
        # else:
        #     self.w.close()  # Close window.
        #     self.w = None  # Discard reference.
        self.dialog =  Time2()
        self.dialog.submitted.connect(self.update_time)
        self.dialog.show()



# app = QtWidgets.QApplication(sys.argv)
# w = Time()
# w.show()
# app.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Time()
    main.show()
    sys.exit(app.exec_())
