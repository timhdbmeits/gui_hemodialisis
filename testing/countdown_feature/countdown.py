import serial
import serial.tools.list_ports
import sys
import time
import warnings
import numpy as np
# importing Qt widgets
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt

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

uftime = 0
# Port Detection END

#Read_serial Thread
class Worker(QObject):
    finished = pyqtSignal()  # unbound PYQT_SIGNAL
    progress = pyqtSignal(str)  # unbound PYQT_SIGNAL String
    bar1 = pyqtSignal(float)
    bar2 = pyqtSignal(float)
    # bar3 = pyqtSignal(int)

    # progress3 = pyqtSignal(str)
    @pyqtSlot()
    def __init__(self):
        super(Worker, self).__init__()
        self.working = True  # indikator membaca serial

    def work(self):
        while self.working:  # jika perintah membaca serial = true
            line = ser.readline().decode().rstrip('\r\n')  # baca serial
            # print(line)
            i = line.split('a')
            # print(i)
            # time.sleep(0.1)
            self.progress.emit(line)  # bound PYQT_SIGNAL String
            self.bar1.emit(float(i[0]))  # bound PYQT_SIGNAL String
            self.bar2.emit(float(i[1]))  # bound PYQT_SIGNAL String
            # self.bar3.emit(int(i[2]))  # bound PYQT_SIGNAL String
            # self.progress3.emit(line)  # bound PYQT_SIGNAL String
        self.finished.emit()

class Worker2(QObject):
    finished = pyqtSignal()  # unbound PYQT_SIGNAL
    progress = pyqtSignal(str)  # unbound PYQT_SIGNAL String
    # bar3 = pyqtSignal(int)

    # progress3 = pyqtSignal(str)
    @pyqtSlot()
    def __init__(self):
        super(Worker2, self).__init__()
        self.working = True  # indikator membaca serial

    def work(self, line=uftime):
        while self.working:  # jika perintah membaca serial = true

            print(str(line))
            # print(i)
            # time.sleep(0.1)
            while line>0:
                self.progress.emit(str(line))  # bound PYQT_SIGNAL String
                line-=1
                time.sleep(1)
        self.finished.emit()

class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("countdown.ui", self)
        self.w = None
        self.thread = None
        self.worker = None  # dibuat none biar tidak langsung membaca saat menjalankan aplikasi
        self.heater = 0
        self.pump = 0
        self.start_loop()

        self.uftime = 0
        self.uftime_button.clicked.connect(lambda : self.add_window('1'))
        self.ufrate_button.clicked.connect(lambda: self.add_window('2'))
        self.start_button.clicked.connect(lambda: self.add_window('3'))
        self.end_button.clicked.connect(lambda: self.add_window('4'))
        self.ufobj_button.clicked.connect(lambda: self.add_window('5'))
        self.ufrmv_button.clicked.connect(lambda: self.add_window('6'))


        # self.ufobj_button.clicked.connect(self.start_loop)  # Start loop
        # self.pump_btn.clicked.connect(self.control_pump)
        # self.heater_btn.clicked.connect(self.control_heater)
        self.startcd_btn.clicked.connect(self.countdown)

    def countdown(self):
        self.worker2 = Worker2()  # a new worker to perform those tasks
        self.thread2 = QThread()  # a new thread to run our background tasks in
        self.worker2.moveToThread(
            self.thread2)  # move the worker into the thread, do this first before connecting the signals

        self.thread2.started.connect(self.worker2.work)  # begin our worker object's loop when the thread starts running
        self.worker2.progress.connect(self.cd)  # menambahkan serial string ke text edit

        self.worker2.finished.connect(self.thread2.quit)  # tell the thread it's time to stop running
        self.worker2.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread2.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion

        self.thread2.start()

    def cd(self,val):
        self.countdown_edit.setText(val)
        self.cd_edit.setText(val)


    def loop_finished(self):
        print('Loop Finished')

    def start_loop(self):
        self.worker = Worker()  # a new worker to perform those tasks
        self.thread = QThread()  # a new thread to run our background tasks in
        self.worker.moveToThread(
            self.thread)  # move the worker into the thread, do this first before connecting the signals

        self.thread.started.connect(self.worker.work)  # begin our worker object's loop when the thread starts running
        self.worker.progress.connect(self.bacadata)  # menambahkan serial string ke text edit
        self.worker.bar1.connect(self.databar1)
        self.worker.bar2.connect(self.databar2)
        # self.worker.bar3.connect(self.databar3)
        # self.uftime_button.clicked.connect(self.stopbaca)  # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion

        self.thread.start()

    def stopbaca(self):
        self.worker.working = False

    def bacadata(self, i):
        i = i.split('a')
        self.s1_edit.setText(i[0])
        self.s2_edit.setText(i[1])
        # self.s3_edit.setText(i[2])
        # self.s1_bar.setValue(i[0])
        # print(i)

    def databar1(self, i):
        self.s1_bar.setValue(int(i))

    def databar2(self, i):
        self.s2_bar.setValue(int(i))

    def databar3(self, i):
        self.s3_bar.setValue(i)

    # led
    def control_pump(self):
        if self.pump == 0:
            ser.write(bytes(b'2'))
            self.pump_label.setText('ON')
            self.pump = 1
        elif self.pump == 1:
            ser.write(bytes(b'1'))
            self.pump_label.setText('OFF')
            self.pump = 0

    # motorservo
    def control_heater(self):
        if self.heater == 0:
            ser.write(bytes(b'4'))
            self.heater_label.setText("ON")
            self.heater = 1
        elif self.heater == 1:
            ser.write(bytes(b'3'))
            self.heater_label.setText("OFF")
            self.heater = 0

    # @pyqtSlot(str,float)
    def update_time(self, uftime_str, uftime):
        self.uftime_str = uftime_str
        self.uftime = uftime

        if self.button == '1':
            self.uftime_button.setText(self.uftime_str)
            self.countdown_edit.setText(str(self.uftime))
        elif self.button == '2':
            self.ufrate_button.setText(self.uftime_str)
        elif self.button == '3':
            self.start_button.setText(self.uftime_str)
        elif self.button == '4':
            self.end_button.setText(self.uftime_str)
        elif self.button == '5':
            self.ufobj_button.setText(self.uftime_str)
        elif self.button == '6':
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
        if button == '1' or button == '2' or button == '3' or button == '4':
            self.dialog =  TimeWindow()
        else :
            self.dialog= LiterWindow()

        self.dialog.submitted.connect(self.update_time)
        self.dialog.show()

class TimeWindow(QtWidgets.QMainWindow):

    submitted = pyqtSignal(str,int)

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

class LiterWindow(QtWidgets.QMainWindow):

    submitted = pyqtSignal(str,float)

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
