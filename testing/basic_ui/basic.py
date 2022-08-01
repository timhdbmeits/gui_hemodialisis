import serial
import serial.tools.list_ports
import sys
import time
import warnings
import numpy as np
# importing Qt widgets
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QTimer

import cgitb

cgitb.enable(format='text')
global dia_time_hours
global dia_time_minutes
global str_dia_time_hours
global str_dia_time_minutes


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("basic_ui.ui", self)
        self.w = None
        self.uftime = 0
        self.uftime_button.clicked.connect(lambda: self.add_window('1'))

        self.start = False
        self.startcd_btn.clicked.connect(self.countdown)
        # creating a timer_time object
        timer = QTimer(self)

        # adding action to timer_time
        timer.timeout.connect(self.showTime)

        # update the timer_time every tenth second(dalam satuan milisecond)
        timer.start(1000 * 60)

        # self.ufobj_button.clicked.connect(self.start_loop)  # Start loop
        # self.pump_btn.clicked.connect(self.control_pump)
        # self.heater_btn.clicked.connect(self.control_heater)

    def showTime(self):

        # checking if flag is true
        if self.start:
            # incrementing the counter
            self.uftime -= 60
            print(self.uftime)
            # timer_time is completed
            if self.uftime == 0:
                # making flag false
                self.start = False

                # setting text to the label
                self.cd_edit.setText("Completed !!!! ")

        if self.start:
            # getting text from count
            text = str(self.uftime) + " s"

            # showing text
            self.cd_edit.setText(text)

    def countdown(self):
        self.start = True
        text = str(self.uftime)
        self.cd_edit.setText(text)

        if self.uftime == 0:
            self.start = False

    # def cd(self, val):
    #     self.countdown_edit.setText(val)
    #     self.cd_edit.setText(val)

    # @pyqtSlot(str,float)
    def update_time(self, uftime_str, uftime):
        self.uftime_str = uftime_str
        #update menit
        self.uftime = int(uftime/60)



        if self.button == '1':
            self.uftime_button.setText(self.uftime_str)
            self.countdown_edit.setText(self.uftime_str)

    def add_window(self, button):
        self.button = button
        # if self.w is None:
        #     self.w = Time2()
        #     self.w.on_submit.connect(self.update_time)
        #     self.w.show()
        #
        # else:
        #     self.w.close()  # Close window.
        #     self.w = None  # Discard reference.
        if button == '1' or button == '2' or button == '3' or button == '4':
            self.dialog = TimeWindow()
        else:
            self.dialog = LiterWindow()

        self.dialog.submitted.connect(self.update_time)
        self.dialog.show()


class TimeWindow(QtWidgets.QMainWindow):
    submitted = pyqtSignal(str, int)

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
        print(self.uftime, "second")
        print(self.minutes, "menit")
        if self.hours < 10:
            self.hours_str = f'0{self.hours}'
        if self.minutes < 10:
            self.minutes_str = f'0{self.minutes}'
        self.uftime_str = f'{self.hours_str}:{self.minutes_str}'
        # self.ok_btn.setText(self.uftime_str)
        # Time.uftime = self.total_time
        # self.on_submit()

        self.submitted.emit(self.uftime_str,
                            self.uftime)
        self.close()


class LiterWindow(QtWidgets.QMainWindow):
    submitted = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()

        # self.mainWindow = Time()
        # Load the UI Page
        uic.loadUi("literwindow.ui", self)

        self.liters = None
        self.liters_str = None

        self.ok_btn.clicked.connect(lambda: self.ok())

    def ok(self):
        self.liters = self.l_spinbox.value()
        self.liters_str = f'{self.liters}'

        self.submitted.emit(self.liters_str,
                            self.liters)
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Gui()
    main.show()
    sys.exit(app.exec_())
