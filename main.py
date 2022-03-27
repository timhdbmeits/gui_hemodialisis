from PyQt5 import QtWidgets, uic
# from pyqtgraph import PlotWidget, plot
# import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
# import os
# import numpy as np
# import pdb # For debugging
import math
import serial
import time


# importing Qt widgets
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi("gui.ui", self)

        self.koneksi()

        # self.getValue()
        # button = QPushButton('button_1')
        # button.clicked.connect(self.on_button_click)
        # timer = QTimer(self)
        # timer.timeout.connect(self.koneksi)
        # timer.start()

    # def showtime(self):
    #     datetime = QDateTime.currentDateTime()
    #     text = datetime.toString()
    #     self.label.setText("   "+ text)

    def koneksi(self):
        ser = serial.Serial('COM3', baudrate=115200, timeout=1)
        time.sleep(3)
        # pressure_data = 3
        # pressArray = [0] * pressure_data
        ser.write(b'g')
        arduinoData = ser.readline().decode().rstrip('\r\n')
        # return arduinoData
        prevarduinoData = 0
        if arduinoData != prevarduinoData:
            prevarduinoData = arduinoData
            print(arduinoData)
            self.pot_edit.setText(prevarduinoData)
        # while (1):
        # UserInput = input()
        # if UserInput == 'pressure':
        #     for i in range(0, len(pressArray)):
        #         data = int(getValue())
        #         pressArray[i] = data
        # print(pressArray)
        # data = int(getValue())
        # print(data)

    def on_button_click(self):
        # self.koneksi()
        # prevarduinoData = 0
        # if arduinoData != prevarduinoData:
        #     prevarduinoData = arduinoData
        #     self.servo_edit.setText(prevarduinoData)
        # print("Tombol diklik!")
        # self.pot_edit.set_text(prevarduinoData)
        ser = serial.Serial('COM3', baudrate=115200, timeout=1)
        time.sleep(3)
        # pressure_data = 3
        # pressArray = [0] * pressure_data
        ser.write(b'g')
        arduinoData = ser.readline().decode().rstrip('\r\n')
        # return arduinoData
        prevarduinoData = 0
        if arduinoData != prevarduinoData:
            prevarduinoData = arduinoData
            self.pot_edit.setText(prevarduinoData)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
