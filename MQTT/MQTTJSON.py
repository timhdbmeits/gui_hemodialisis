import paho.mqtt.client as mqtt
import json
import time
import random



def init():
    def on_log(client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_dc(client, userdata, rc):
        client.connect(broker, 1883, 60)

    broker = "broker.hivemq.com"

    client = mqtt.Client("python1")
    client.on_connect = on_connect
    client.on_log = on_log
    client.on_disconnect = on_dc

    print("Connecting to broker ",broker)

    client.connect(broker,1883,60)
    return client

def send_mqtt (dict,topic,client):
    send = json.dumps(dict)
    client.publish(topic, send+'\n', 0)
    print(send)
    # time.sleep(.1)

# rnd = random.random()
# fl1 = rnd * 10.0
# fl1 = round(fl1, 2)
# dict = {
#     "UF": [round(random.random()*10, 2), round(random.random()*10, 2)],
#     "Press": [round(random.random()*1000, 2), round(random.random()*1000, 2), round(random.random()*1000, 2)],
#     "Temp": round(random.random()*100, 2),
#     "Cond": round(random.random()*100, 2),
#     "Flow": [round(random.random()*10, 2), round(random.random()*1000, 2), round(random.random()*1000, 2)]
# }