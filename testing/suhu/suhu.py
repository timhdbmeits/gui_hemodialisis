import serial
import serial.tools.list_ports
import sys
import time
import warnings
import numpy as np
# importing Qt widgets
from PyQt5 import QtWidgets, uic, QtSerialPort
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt



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
            print(line)
            i = line.split('a')

            # print(i)
            # value.sleep(0.1)
            self.progress.emit(line)  # bound PYQT_SIGNAL String
            self.bar1.emit(float(i[0]))  # bound PYQT_SIGNAL String
            self.bar2.emit(float(i[1]))  # bound PYQT_SIGNAL String
            # self.bar3.emit(int(i[2]))  # bound PYQT_SIGNAL String
            # self.progress3.emit(line)  # bound PYQT_SIGNAL String
        self.finished.emit()


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("suhu.ui", self)

        self.thread = None
        self.worker = None  # dibuat none biar tidak langsung membaca saat menjalankan aplikasi
        self.heater = 0
        self.pump = 0
        self.start_btn.clicked.connect(self.start_loop)  # Start loop
        self.pump_btn.clicked.connect(self.control_pump)
        self.heater_btn.clicked.connect(self.control_heater)

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
        self.stop_btn.clicked.connect(self.stopbaca)  # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)  # tell the thread it's value to stop running
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Gui()
    main.show()
    sys.exit(app.exec_())
