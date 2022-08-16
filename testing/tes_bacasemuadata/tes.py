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

    # Initialise signal :ex(T3s) s = signal
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
            # Float
            T3 = sensor["T3"]
            EC = sensor["EC"]
            # PH = sensor["PH"]
            # FM = sensor["FM"]
            # # Int
            # VD = sensor["VD"]
            # # Bool
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
            V12 = sensor["V"][0]
            # V13 = sensor["V"][12]
            # BUBBLE = sensor["BUBBLE"]
            # # Float
            # PDVal = sensor["PRESS"][0]
            # PAVal = sensor["PRESS"][1]
            # PVVal = sensor["PRESS"][2]
            # #Int
            # ERR = sensor["ERR"]

            # emit signals to be read in main GUI
            self.signals.T3s.emit(T3)
            self.signals.ECs.emit(EC)
            # self.signals.PHs.emit(PH)
            # self.signals.FMs.emit(FM)
            # self.signals.VDs.emit(VD)
            # self.signals.BDs.emit(BD)
            # self.signals.HTs.emit(HT)
            # self.signals.CL.emit(CL)
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
            self.signals.V12s.emit(V12)
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
        self.dialyse_button.clicked.connect(self.startDia)

        # creating a timer_time object, adding action to timer_time, update the timer_time every second
        self.timer_time = QTimer(self)
        self.timer_time.timeout.connect(self.showTime)
        self.timer_time.start(1000)

        # state Variabel
        self.value = None
        self.string = None

        # connect Button
        self.uftime_button.clicked.connect(lambda: self.addWindow('uftime'))
        self.ufobj_button.clicked.connect(lambda: self.addWindow('ufobj'))
        self.ufdata_button.clicked.connect(self.showUFData)
        self.setting_button.clicked.connect(self.showSetting)

        self.threadpool = QThreadPool()
        self.readData()

    def showSetting(self):
        self.setting_button.setStyleSheet("font: 50pt;"
                                         "color: #333;"
                                         "background: #C4C4C4;"
                                         "border: 1px solid #FFFFFF;"
                                         "box-sizing: border-box;"
                                         "box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);"
                                         "border-radius: 5px;")
        self.data_stackedWidget.setCurrentIndex(1)


    def showUFData(self):
        self.ufdata_button.setStyleSheet("font: 50pt;"
                                         "color: #333;"
                                         "background: #C4C4C4;"
                                         "border: 1px solid #FFFFFF;"
                                         "box-sizing: border-box;"
                                         "box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);"
                                         "border-radius: 5px;")
        self.data_stackedWidget.setCurrentIndex(0)

    def readData(self):
        self.worker = Worker()
        self.worker.signals.T3s.connect(self.showT3)
        self.worker.signals.ECs.connect(self.showEC)
        # self.worker.signals.PHs.connect(self.showPH)
        self.worker.signals.FMs.connect(self.showFM)
        # self.worker.signals.VDs.connect(self.showVD)
        # self.worker.signals.BDs.connect(self.showBD)
        # self.worker.signals.HTs.connect(self.showHT)
        # self.worker.signals.CLs.connect(self.showCL)
        # self.worker.signals.V12s.connect(self.showV12)
        # self.worker.signals.BUBBLEs.connect(self.BUBBLE)
        # self.worker.signals.PDVals.connect(self.PDVal)
        # self.worker.signals.PAVals.connect(self.PAVal)
        # self.worker.signals.PVVals.connect(self.PVVal)

        self.threadpool.start(self.worker)

    def showT3(self, s):
        self.temp_edit.setText(str(s))

    def showEC(self, s):
        self.ec_edit.setText(str(s))

    def showFM(self, s):
        self.fm_edit.setText(str(s))

    def showV12(self, s):
        self.v12_edit.setText(str(s))

    def showPDVal(self, s):
        self.pdval_edit.setText(str(s))

    def showTime(self):
        # getting current value
        self.current_time = QTime.currentTime()
        # converting QTime object to string
        self.label_time = self.current_time.toString('hh:mm')
        # showing it to the label
        self.time_label.setText(self.label_time)

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

    def updateData(self, string, value):
        self.string = string
        self.value = value

        if self.button == 'uftime':
            global UFTIME_VAL
            global UFTIME_STR
            UFTIME_VAL = self.value
            UFTIME_STR = self.string
            uffinish_time = self.current_time.addSecs(UFTIME_VAL)
            uffinish_time_label = uffinish_time.toString('hh:mm')
            self.uftime_button.setText(UFTIME_STR)
            self.uffinish_edit.setText(uffinish_time_label)
            self.dialeft_edit.setText(UFTIME_STR)

        elif self.button == 'ufobj':
            global UFOBJ_VAL
            global UFOBJ_STR
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

        if button == 'uftime':
            dialog = TimeWindow()
        else:
            dialog = LiterWindow()

        dialog.submitted.connect(self.updateData)
        dialog.show()


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
