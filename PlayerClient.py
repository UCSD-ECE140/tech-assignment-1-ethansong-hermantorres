import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random

def moveInput(client, data, isPlayer, name):

        if(isPlayer):
            if(name == player_1):
                command = ""
                inputOkay = False
                while(not inputOkay):
                    command = input("Enter Your Move: ")
                    if(command not in commands):
                        print("Invalid input")
                    else:
                        inputOkay = True

        
                if(command != "STOP"):
                    client.publish(f"games/{lobby_name}/{name}/move", command)
                else:
                    client.publish(f"games/{lobby_name}/start", "STOP")
        else:
            botMove = -1
            currentPos = data["currentPosition"]
            if data["coin3"] != None or data["coin2"] != None or data["coin1"] != None:
                coins = []
                coins.append(data["coin3"])
                coins.append(data["coin2"])
                coins.append(data["coin1"])
                for coin in coins:
                    for coinPos in coin:
                        if(coinPos == [currentPos[0]-1, currentPos[1]]):
                            botMove = 0
                            break
                        elif(coinPos == [currentPos[0]+1, currentPos[1]]):
                            botMove = 1
                            break
                        elif(coinPos == [currentPos[0], currentPos[1]-1]):
                            botMove = 2
                            break
                        elif(coinPos == [currentPos[0], currentPos[1]+1]):
                            botMove = 3
                            break
                if(botMove == -1):
                    botMove = random.randint(0,3)
            client.publish(f"games/{lobby_name}/{name}/move", commands[botMove])
            time.sleep(.05)

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

    if "game_state" in msg.topic:
        isPlayer = True
        playerName = msg.topic.split("/")[2]
        if playerName in bots:
            isPlayer = False
        else:
            print(str(msg.payload))
        moveInput(client, json.loads(msg.payload), isPlayer, playerName)
    else: 
        print(msg.payload)
        if("lobby" in msg.topic):
            if(b'Game Over' in msg.payload):
                client.disconnect()





if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = input("Enter Lobby Name: ")

    player = False
    player_1 = ""
    if(input("Are you playing? (YES or NO): ") == "YES"):
        player = True
        player_1 = input("Enter Player Name: ")

    numBots = int(input("Enter Number of Bots: "))
    bots = []
    for i in range(1,numBots+1, 1):
        aBot = "Bot" + str(i)
        bots.append(aBot)
    



    if(player):
        client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    botTeam = 'B'
    for bot in bots:
        client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                                'team_name': botTeam + 'Team',
                                                'player_name' : bot}))
        if(botTeam == 'A'):
            botTeam = 'B'
        else:
            botTeam = 'A'

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    time.sleep(1) # Wait a second to resolve game start
    input("Press Enter to Start The Game... ")
    client.publish(f"games/{lobby_name}/start", "START")



    commands = ["UP", "DOWN", "LEFT", "RIGHT", "STOP"]

    if(player):
        command = ""
        inputOkay = False
        while(not inputOkay):
            command = input("Enter Your Move: ")
            if(command not in commands):
                print("Invalid input")
            else:
                inputOkay = True

    
        if(command != "STOP"):
            client.publish(f"games/{lobby_name}/{player_1}/move", command)
        else:
            client.publish(f"games/{lobby_name}/start", "STOP")
    for bot in bots:
        botMove = random.randint(0,3)
        client.publish(f"games/{lobby_name}/{bot}/move", commands[botMove])
        time.sleep(.5)


    client.loop_forever()
