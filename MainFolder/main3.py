import serial
import serial.tools.list_ports
import sys
import time
import warnings
import numpy as np
# importing Qt widgets
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QTimer, QTime

import cgitb

cgitb.enable(format='text')

UFTIME_VAL = 0
UFTIME_STR = ''


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("tes.ui", self)

        # getting current value
        current_time = QTime.currentTime()
        # converting QTime object to string
        label_time = current_time.toString('hh:mm')
        # showing it to the label
        self.time_label.setText(label_time)

        # # declare variabel start Countdown
        # self.start = False
        # self.startcd_btn.clicked.connect(self.countdown)
        # declare variabel start timer_time
        self.start = False
        self.startcd_btn.clicked.connect(self.startDia)

        # creating a timer_time object, adding action to timer_time, update the timer_time every second
        self.timer_time = QTimer(self)
        self.timer_time.timeout.connect(self.showTime)
        self.timer_time.start(1000)

        # state Variabel
        self.time = None
        self.time_str = None

        # connect Button
        self.uftime_button.clicked.connect(lambda: self.addWindow('uftime'))
        self.ufobj_button.clicked.connect(lambda: self.addWindow('ufobj'))
        self.ufdata_button.clicked.connect(self.showUFData)
        self.setting_button.clicked.connect(self.showSetting)


    def showSetting(self):
        self.ufdata_button.setStyleSheet("font: 50pt;"
                                         "color: #333;"
                                         "background: #C4C4C4;"
                                         "border: 1px solid #FFFFFF;"
                                         "box-sizing: border-box;"
                                         "box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);"
                                         "border-radius: 5px;")
        self.data_stackedWidget.setCurrentIndex(1)
        if self.data_stackedWidget.CurrentIndex == 1:
            self.ufdata_button.setStyleSheet("font: 50pt;"
                                             "color: #333;"
                                             "background: #5555FF;"
                                             "border: 1px solid #FFFFFF;"
                                             "box-sizing: border-box;"
                                             "box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);"
                                             "border-radius: 5px;")

    def showUFData(self):
        self.ufdata_button.setStyleSheet("font: 50pt;"
                                         "color: #333;"
                                         "background: #C4C4C4;"
                                         "border: 1px solid #FFFFFF;"
                                         "box-sizing: border-box;"
                                         "box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);"
                                         "border-radius: 5px;")
        self.data_stackedWidget.setCurrentIndex(0)


    def showTime(self):
        # getting current value
        current_time = QTime.currentTime()
        # converting QTime object to string
        label_time = current_time.toString('hh:mm')
        # showing it to the label
        self.time_label.setText(label_time)

    def startDia(self):
        # creating a timer_time object, adding action to timer_time, update the timer_time every minutes
        self.timer_dia = QTimer(self)
        self.timer_dia.timeout.connect(self.timeDia)
        self.timer_dia.start(10)

        self.text = UFTIME_STR

        self.start = True

        if UFTIME_VAL == 0:
            self.start = False

    def timeDia(self):
        global UFTIME_VAL
        global UFTIME_STR
        global uftime_hours
        global uftime_minutes
        # checking if flag is true for countdown
        if self.start:
            # incrementing the counter
            UFTIME_VAL -= 1
            print(UFTIME_VAL)
            # timer_time is completed
            if UFTIME_VAL == 0:
                # making flag false
                self.start = False
                self.cd_edit.setText('0')

        # mulai jalan setiap menit
        if self.start and (UFTIME_VAL % 60 == 0):
            # getting text from count
            self.hours = int(UFTIME_VAL / 3600)
            self.minutes = int((UFTIME_VAL % 3600) / 60)
            # if self.hours < uftime_hours:

            self.text = f'{self.hours:02}:{self.minutes:02}'

        # showing text
        self.cd_edit.setText(self.text)

    # @pyqtSlot(str,float)
    def updateData(self, string, value):
        self.time_str = string
        self.time = value

        if self.button == 'uftime':
            global UFTIME_VAL
            global UFTIME_STR
            UFTIME_VAL = self.time
            UFTIME_STR = self.time_str
            self.uftime_button.setText(UFTIME_STR)
            self.countdown_edit.setText(UFTIME_STR)
            self.cd_edit.setText(UFTIME_STR)

        elif self.button == 'ufobj':
            self.ufobj_button.setText(self.time_str)

    def addWindow(self, button):
        self.button = button

        if button == 'uftime':
            self.dialog = TimeWindow()
        else:
            self.dialog = LiterWindow()

        self.dialog.submitted.connect(self.updateData)
        self.dialog.show()


class TimeWindow(QtWidgets.QMainWindow):
    submitted = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()

        # Load the UI Page
        uic.loadUi("timewindow.ui", self)

        self.hours = None
        self.hours_str = None
        self.minutes = None
        self.minutes_str = None
        self.time = None
        self.time_str = None
        self.ok_btn.clicked.connect(lambda: self.ok())

    def ok(self):
        self.hours = self.h_spinbox.value()
        self.minutes = self.m_spinbox.value()
        self.hours_str = f'{self.hours}'
        self.minutes_str = f'{self.minutes}'
        # satuan menit buat countdown

        if self.hours < 10:
            self.hours_str = f'0{self.hours}'
        if self.minutes < 10:
            self.minutes_str = f'0{self.minutes}'

        # jumlah detik value total
        self.time = (self.hours * 60 + self.minutes) * 60
        self.time_str = f'{self.hours_str}:{self.minutes_str}'
        print(self.time, "menit")

        self.submitted.emit(self.time_str,
                            self.time)
        self.close()


class LiterWindow(QtWidgets.QMainWindow):
    submitted = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()

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
