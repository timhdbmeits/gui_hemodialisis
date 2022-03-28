import serial
import serial.tools.list_ports
import sys
import time
import warnings

# importing Qt widgets
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

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
    intReady = pyqtSignal(str)  # unbound PYQT_SIGNAL String

    @pyqtSlot()
    def __init__(self):
        super(Worker, self).__init__()
        self.working = True  # indikator membaca serial

    def work(self):
        while self.working:  # jika perintah membaca serial = true
            line = ser.readline().decode().rstrip('\r\n')  # baca serial
            print(line)
            time.sleep(0.1)
            self.intReady.emit(line)  # bound PYQT_SIGNAL String
        self.finished.emit()


class Gui(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("gui.ui", self)

        self.thread = None
        self.worker = None  # dibuat none biar tidak langsung membaca saat menjalankan aplikasi
        self.pushButton.clicked.connect(self.start_loop)  # Start loop
        self.label.setText('PORT :' + ports[0])  # Menampilkan koneksi ke port

        self.pushButton_3.clicked.connect(self.control_led)

    def loop_finished(self):
        print('Loop Finished')

    def start_loop(self):
        self.worker = Worker()  # a new worker to perform those tasks
        self.thread = QThread()  # a new thread to run our background tasks in
        self.worker.moveToThread(
            self.thread)  # move the worker into the thread, do this first before connecting the signals

        self.thread.started.connect(self.worker.work)  # begin our worker object's loop when the thread starts running

        self.worker.intReady.connect(self.onIntReady)  # menambahkan serial string ke text edit

        self.pushButton_2.clicked.connect(self.stop_loop)  # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion

        self.thread.start()

    def stop_loop(self):
        self.worker.working = False

    def onIntReady(self, i):
        i = i.split('a')
        self.textEdit.clear()
        self.textEdit_2.clear()
        self.textEdit.append("{}".format(i[0]))
        self.textEdit_2.append("{}".format(i[1]))
        print(i)

    def control_led(self):
        data = b'1'
        n = ser.write(bytes(data))
        self.textEdit_2.append(str(n))

def run():
    app = QtWidgets.QApplication(sys.argv)
    main = Gui()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
