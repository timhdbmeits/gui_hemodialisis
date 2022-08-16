import serial
import time
import json

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)

dat = {
    "flowrate1" : 1.0,
    "flowrate2" : 20.0,
    "mixinga" : 300.0,
    "mixingb" : 400.0,
    "duration" : 300,
    "mode" : 1,
    "start/stop" : 1,
    "bypass" : 0,
    "alert" : True,
    "sound" : False
}

send = json.dumps(dat)
arduino.reset_input_buffer

def write_read():
    data = arduino.readline()
    if data is not None:
        time.sleep(0.01)
        string = str(data)
        return string

arduino.write(bytes(send,'utf-8'))
while True:
    # arduino.write(bytes(send,'utf-8'))
    pr = write_read()
    if pr[2:-5] != '':
        y = json.loads(pr[2:-5])
        print(y)
        time.sleep(0.1)