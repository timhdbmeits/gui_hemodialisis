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

    # Initialise signal :ex(T3s) s = signal
    T1s = pyqtSignal(float)
    T2s = pyqtSignal(float)
    T3s = pyqtSignal(float)
    ECs = pyqtSignal(float)
    PHs = pyqtSignal(float)
    FMs = pyqtSignal(float)
    VDs = pyqtSignal(int)
    BDs = pyqtSignal(bool)
    HTs = pyqtSignal(bool)
    CLs = pyqtSignal(bool)
    V1s = pyqtSignal(bool)
    V2s = pyqtSignal(bool)
    V3s = pyqtSignal(bool)
    V4s = pyqtSignal(bool)
    V5s = pyqtSignal(bool)
    V6s = pyqtSignal(bool)
    V7s = pyqtSignal(bool)
    V8s = pyqtSignal(bool)
    V9s = pyqtSignal(bool)
    V10s = pyqtSignal(bool)
    V11s = pyqtSignal(bool)
    V12s = pyqtSignal(bool)
    V13s = pyqtSignal(bool)
    BUBBLEs = pyqtSignal(bool)
    PDVals = pyqtSignal(float)
    PAVals = pyqtSignal(float)
    PVVals = pyqtSignal(float)
    ERRs = pyqtSignal(int)


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
            T1 = sensor["T"][0]
            T2 = sensor["T"][1]
            T3 = sensor["T"][2]
            EC = sensor["EC"]
            PH = sensor["PH"]
            FM = sensor["FM"]
            # VD = sensor["VD"]
            # BD = sensor["BD"]
            # HT = sensor["HT"]
            # CL = sensor["CL"]
            # V1 = sensor["V"][0]
            # V2 = sensor["V"][1]
            # V3 = sensor["V"][2]
            # V4 = sensor["V"][3]
            # V5 = sensor["V"][4]
            # V6 = sensor["V"][5]
            # V7 = sensor["V"][6]
            # V8 = sensor["V"][7]
            # V9 = sensor["V"][8]
            # V10 = sensor["V"][9]
            # V11 = sensor["V"][10]
            # V12 = sensor["V"][11]
            # V13 = sensor["V"][12]
            # BUBBLE = sensor["BUBBLE"]
            # PDVal = sensor["PRESS"][0]
            # PAVal = sensor["PRESS"][1]
            # PVVal = sensor["PRESS"][2]
            # ERR = sensor["ERR"]

            # emit signals to be read in main GUI
            self.signals.T1s.emit(T1)
            self.signals.T2s.emit(T2)
            self.signals.T3s.emit(T3)
            self.signals.ECs.emit(EC)
            self.signals.PHs.emit(PH)
            self.signals.FMs.emit(FM)
            # self.signals.VDs.emit(VD)
            # self.signals.BDs.emit(BD)
            # self.signals.HTs.emit(HT)
            # self.signals.CLs.emit(CL)
            # self.signals.V1s.emit(V1)
            # self.signals.V2s.emit(V2)
            # self.signals.V3s.emit(V3)
            # self.signals.V4s.emit(V4)
            # self.signals.V5s.emit(V5)
            # self.signals.V6s.emit(V6)
            # self.signals.V7s.emit(V7)
            # self.signals.V8s.emit(V8)
            # self.signals.V9s.emit(V9)
            # self.signals.V10s.emit(V10)
            # self.signals.V11s.emit(V11)
            # self.signals.V12s.emit(V12)
            # self.signals.V13s.emit(V13)
            # self.signals.BUBBLEs.emit(BUBBLE)
            # self.signals.PDVals.emit(PDVal)
            # self.signals.PAVals.emit(PAVal)
            # self.signals.PVVals.emit(PVVal)
            # self.signals.ERRs.emit(ERR)

        self.signals.finished.emit()


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("../UIdesign/main.ui", self)

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
        self.timer_time.timeout.connect(self.function_Time)
        self.timer_time.start(1000)

        # state Variabel
        self.value = None
        self.string = None

        # state JSON
        global JSON_IN
        JSON_IN = {
            "MODE": 0,
            "DUR": 0,
            "FLOW": [0.0, 0.0],
            "VOL": 0.0,
            "MIX": [20.13, 36.83],
            "BYPS": False,
            "ALRT": False,
            "SND": False,
            "START": False,
            "CLAMP": False,
            "BUBBLE": False,
            "SP_COND": False,
            "BP_COND": False,
        }

        # connect Button
        self.uftime_button.clicked.connect(lambda: self.addWindow('uftime'))
        self.ufobj_button.clicked.connect(lambda: self.addWindow('ufobj'))
        self.ufdata_button.clicked.connect(self.function_UFData)
        self.setting_button.clicked.connect(self.function_Setting)
        # self.dialyse_button.clicked.connect(self.function_Dialyse)
        # self.bypass_button.clicked.connect(self.function_Bypass)
        # self.drain_button.clicked.connect(self.function_Drain)

        self.threadpool = QThreadPool()
        self.readData()

    def function_Time(self):
        # getting current value
        self.current_time = QTime.currentTime()
        # converting QTime object to string
        self.label_time = self.current_time.toString('hh:mm')
        # Showing it to the label
        self.time_label.setText(self.label_time)

    def function_UFData(self):
        # self.ufdata_button.setStylesheet
        self.data_stackedWidget.setCurrentIndex(0)

    def function_Setting(self):
        self.data_stackedWidget.setCurrentIndex(1)

    # TODO tes fungsi tiap komponen
    def readData(self):
        self.worker = Worker()
        # self.worker.signals.T1s.connect(self.function_T1)
        # self.worker.signals.T2s.connect(self.function_T2)
        # self.worker.signals.T3s.connect(self.function_T3)
        # self.worker.signals.ECs.connect(self.function_EC)
        # self.worker.signals.PHs.connect(self.function_PH)
        # self.worker.signals.FMs.connect(self.function_FM)
        # self.worker.signals.VDs.connect(self.function_VD)
        # self.worker.signals.BDs.connect(self.function_BD)
        # self.worker.signals.HTs.connect(self.function_HT)
        # self.worker.signals.CLs.connect(self.function_CL)
        # self.worker.signals.V12s.connect(self.function_V1)
        # self.worker.signals.V12s.connect(self.function_V2)
        # self.worker.signals.V12s.connect(self.function_V3)
        # self.worker.signals.V12s.connect(self.function_V4)
        # self.worker.signals.V12s.connect(self.function_V5)
        # self.worker.signals.V12s.connect(self.function_V6)
        # self.worker.signals.V12s.connect(self.function_V7)
        # self.worker.signals.V12s.connect(self.function_V8)
        # self.worker.signals.V12s.connect(self.function_V9)
        # self.worker.signals.V12s.connect(self.function_V10)
        # self.worker.signals.V12s.connect(self.function_V11)
        # self.worker.signals.V12s.connect(self.function_V12)
        # self.worker.signals.V12s.connect(self.function_V13)
        # self.worker.signals.BUBBLEs.connect(self.function_BUBBLE)
        # self.worker.signals.PDVals.connect(self.function_PDVal)
        # self.worker.signals.PAVals.connect(self.function_PAVal)
        # self.worker.signals.PVVals.connect(self.function_PVVal)

        self.threadpool.start(self.worker)

    def function_T3(self, s):
        self.t3_edit.setText(str(s))

    def function_EC(self, s):
        self.ec_edit.setText(str(s))

    def function_FM(self, s):
        self.fm_edit.setText(str(s))

    def function_V12(self, s):
        self.v12_edit.setText(str(s))

    def function_BUBBLE(self, s):
        global BUBBLE_STATE
        BUBBLE_STATE = s
        JSON_IN["BUBBLE"] = BUBBLE_STATE

    def function_PDVal(self, s):
        self.pdval_edit.setText(str(s))

    def function_PAVal(self, s):
        self.paval_edit.setText(str(s))

    def function_PVVal(self, s):
        self.pvval_edit.setText(str(s))

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

        # Showing text
        self.cd_edit.setText(self.text)

    def updateData(self, string, value):
        global UFTIME_VAL
        global UFTIME_STR
        global UFOBJ_VAL
        global UFOBJ_STR
        self.string = string
        self.value = value

        if self.button == 'uftime':
            UFTIME_VAL = self.value
            UFTIME_STR = self.string
            uffinish_time = self.current_time.addSecs(UFTIME_VAL)
            uffinish_time_label = uffinish_time.toString('hh:mm')
            self.uftime_button.setText(UFTIME_STR)
            self.uffinish_edit.setText(uffinish_time_label)
            self.dialeft_edit.setText(UFTIME_STR)

        elif self.button == 'ufobj':

            UFOBJ_VAL = self.value
            UFOBJ_STR = self.string
            self.ufobj_button.setText(UFOBJ_STR)

        if (UFTIME_VAL != 0) and (UFOBJ_VAL != 0):
            # *3600 = hours
            global UFRATE_VAL
            global UFRATE_STR
            UFRATE_VAL = UFOBJ_VAL / UFTIME_VAL * 3600
            UFRATE_STR = str(UFRATE_VAL)
            self.ufrate_button.setText(UFRATE_STR)

    def addWindow(self, button):
        self.button = button
        if self.button == 'uftime':
            dialog = TimeWindow()
        else:
            dialog = LiterWindow()

        dialog.submitted.connect(self.updateData)
        dialog.show()

    # TODO tes ngirim data ke microcontroller
    def sendData(self):
        # ngirim json mini pc ke master(teensy)
        dataJSON = json.dumps(JSON_IN)
        ser.write(bytes(dataJSON, 'utf-8'))


class TimeWindow(QtWidgets.QMainWindow):
    submitted = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()

        # Load the UI Page
        uic.loadUi("../UIdesign/timewindow.ui", self)

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
        uic.loadUi("../UIdesign/literwindow.ui", self)

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
