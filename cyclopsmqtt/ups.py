# Import
import paho.mqtt.client as mqtt
import time
from pyopenups import *
import options

# Variables
publish_interval = 1 # 1 sec

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("robot/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# Get UPS property
def get_ups_property():
    ups = {}
    state = get_ups_state()
    if state == BATTERY_STATE:
        ups["state"] = "Battery"
    elif state == VIN_STATE:
        ups["state"] = "VIn"
    elif state == USB_STATE:
        ups["state"] = "USB"
    else:
        ups["state"] = "Error"
    
    ups["pout"] = get_ups_output_power()
    ups["vin"] = get_ups_vin()
    ups["vbat"] = get_ups_vbat()
    ups["vout"] = get_ups_vout()
    ups["acharge"] = get_ups_ccharge()
    ups["adischarge"] = get_ups_cdischarge()
    ups["ain"] = get_ups_cin()
    ups["temp"] = get_ups_temperature()
    vcell = ""
    for i in range(0,6):
        vcell += str(get_ups_vcell(i))
        if i != 5:
            vcell += ", "
    ups["vcell"] = vcell
    return ups

if __name__ == "__main__":
    try:
        if ups_open_device(1000):
            time.sleep(0.5)
            print "COnnected to UPS."
        else:
            raise Exception("Couldn't connect to UPS.")

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set("milk3dfx","Ss198811")

        client.connect(options.broker["host"], 8883, 60)

        # Start publishing
        client.loop_start()
        while True:
                ups = get_ups_property ()
                for prop in ups:
                    client.publish("robot/ups/" + prop, ups[prop])
                time.sleep (publish_interval)
                
    except KeyboardInterrupt:
        # Clean up
        client.loop_stop()
        ups_close_device()