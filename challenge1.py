import time


import paho.mqtt.client as paho
from paho import mqtt
import random




# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)




# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))




# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))




# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="client1", userdata=None, protocol=paho.MQTTv5)
client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="client2", userdata=None, protocol=paho.MQTTv5)
client3 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="client3", userdata=None, protocol=paho.MQTTv5)

pclients = [client, client2]
clients = [client, client2, client3]
client.username_pw_set("ecsong@ucsd", "Popo6245")
client2.username_pw_set("testStudent@ucsd", "Esong6245")
client3.username_pw_set("testStudent2@ucsd", "Niko6245")

for c in clients:
    c.on_connect = on_connect

    # enable TLS for secure connection
    c.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password

    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    c.connect("36e313d0c9b347f790dba49bb2b44de1.s1.eu.hivemq.cloud", 8883)


    # setting callbacks, use separate functions like above for better visibility
    c.on_subscribe = on_subscribe
    c.on_message = on_message
    c.on_publish = on_publish



prevTime = time.time()



client.loop_start()
client2.loop_start()
client3.loop_start()

client3.subscribe("random/#", qos=1)

while(True):
    currentTime = time.time()
    if((currentTime - prevTime) > 3):
        for c in pclients:
            message = str(random.randint(0,1000))

            c.publish("random/number", payload=message, qos=1)
            
            prevTime = currentTime

client.loop_stop()
client2.loop_stop()

