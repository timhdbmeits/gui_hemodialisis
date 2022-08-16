import serial.tools.list_ports
import json
import warnings

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

# ngirim json mini pc ke master(teensy)

dataJSON = json.dumps(JSON_IN)
ser.write(bytes(dataJSON, 'utf-8'))
