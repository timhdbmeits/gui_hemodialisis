import time

import serial.tools.list_ports
import sys
import warnings
import json

# ports = [
#     port.device
#     for port in serial.tools.list_ports.comports()
#     if 'USB' in port.description
# ]
# if not ports:
#     raise IOError("There is no device exist on serial port!")
#
# if len(ports) > 1:
#     warnings.warn('Connected....')
#
# ser = serial.Serial(ports[0], 9600)
# ser.reset_input_buffer()

# state JSON
JSON_IN = {
    "MODE": 1,
    "DUR": 1440055555511,
    "FLOW": [300.0, 5.0],
    "VOL": 50.0,
    "MIX": [20.13, 36.83],
    "PUMP": [1, 1],
    "BYPS": 0,
    "ALRT": 0,
    "SND": 0,
    "CLAMP": 0,
    "START": 0,
}
send_teensy1 = str([*JSON_IN.values()])
specialchar = "[] "
for i in specialchar:
    send_teensy1 = send_teensy1.replace(i, '')
send_teensy1= '<' + send_teensy1 + '>\n'
send_teensy = str([*JSON_IN.values()])
send_teensy = send_teensy.replace('[', '')
send_teensy = send_teensy.replace(']', '')
send_teensy = send_teensy.replace(' ', '')
send_teensy = '<' + send_teensy + '>\n'
print(send_teensy1)
print(send_teensy)
jsoni ='<1,14400,340.0,5.0,50.0,20.13,36.83,1,1,0,0,0,0,0>\n'
# ngirim json mini pc ke master(teensy)
JSON_IN["MODE"] = 0
dataJSON = json.dumps(JSON_IN)
# while True:
#     ser.write(send_teensy.encode('ascii'))
#     time.sleep(0.1)
# ser.write(dataJSON)
# ser.write(bytes(b'1'))
# print(ser.readline())
# ser.write(bytes(dataJSON.encode('ascii')))
# print(ser.readline().decode().rstrip('\r\n'))
print(send_teensy.encode('ascii'))
# print(bytes(dataJSON,'ascii'))