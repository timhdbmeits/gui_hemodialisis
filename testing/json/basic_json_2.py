import serial
import serial.tools.list_ports
import sys
import time
import warnings
import numpy as np
import traceback
import json
# importing Qt widgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt, QTimer, QTime

import cgitb

cgitb.enable(format='text')

UFTIME_VAL = 0
UFTIME_STR = ''


# Port Detection START
# List Comprehension ( expression for item in iterable if condition)
ports = [
    port.device
    for port in serial.tools.list_ports.comports()
    if 'USB' in port.description
]
if not ports:
    raise IOError("There is no device exist on serial port!")

if len(ports) > 1:
    warnings.warn('Connected....')

ser = serial.Serial(ports[0], 115200)

# Port Detection END


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


    #Initialise signal
    T3 = pyqtSignal(float)
    EC = pyqtSignal(float)



class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.run = True

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        while self.run:
            line = ser.readline().decode().rstrip('\r\n')
            sensor = json.loads(line)

            # initialise variable sensor for arduino read
            sensor_t3 = sensor["T3"]
            sensor_ec = sensor["EC"]

            #emit signals to be read in main GUI
            self.signals.T3.emit(sensor_t3)
            self.signals.EC.emit(sensor_ec)
        self.signals.finished.emit()


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("basic_ui_json.ui", self)


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
        global JSON_IN
        JSON_IN = {
            "MODE": 0,
            "DUR": 0,
            "FLOW": [0.0, 0.0],
            "VOL": 0.0,
            "MIX": [20.13, 36.83],
            "BYPS": 0,
            "ALRT": 0,
            "SND": 0,
            "START": 0,
            "CLAMP": 0,
            "BUBBLE": 0,
            "SP_COND": 0,
            "BP_COND": 0,
        }

        # connect Button
        self.uftime_button.clicked.connect(lambda: self.addWindow('uftime'))
        self.ufobj_button.clicked.connect(lambda: self.addWindow('ufobj'))
        self.startcd_btn.clicked.connect(self.showLED)

        self.threadpool = QThreadPool()
        self.readData()

#TODO mengirim data ke teensy
    def showLED(self):

        if JSON_IN["MODE"] == 0:
            JSON_IN["MODE"] = 1
        elif JSON_IN["MODE"] == 1:
            JSON_IN["MODE"] = 0

        dataJSON = json.dumps(JSON_IN)
        ser.write(bytes(dataJSON, 'utf-8'))
        print(dataJSON)

    def readData(self):
        self.worker = Worker()
        self.worker.signals.T3.connect(self.showT3)
        self.worker.signals.EC.connect(self.showEC)

        self.threadpool.start(self.worker)


    def showT3(self, s):
        self.temp_edit.setText(str(s))

    def showEC(self, s):
        self.ec_edit.setText(str(s))




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

        #mulai jalan setiap menit
        if self.start and (UFTIME_VAL%60 == 0):
            # getting text from count
            self.hours = int(UFTIME_VAL/3600)
            self.minutes = int((UFTIME_VAL%3600)/60)
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

        if button == 'uftime' :
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
