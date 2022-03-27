import serial
import time

ser = serial.Serial('COM3', baudrate=115200, timeout=1)
time.sleep(3)
pressure_data = 3
pressArray = [0] * pressure_data


def getValue():
    ser.write(b'g')
    arduinoData = ser.readline().decode().rstrip('\r\n')
    return arduinoData


while (1):
    # UserInput = input()
    # if UserInput == 'pressure':
    #     for i in range(0, len(pressArray)):
    #         data = int(getValue())
    #         pressArray[i] = data
    # print(pressArray)
    data = int(getValue())
    print(data)
