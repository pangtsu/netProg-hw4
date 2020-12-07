#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select
import math
import json
# python3 server.py [control port] [base station file]
# i.e.,: python3 server.py 8071 base_stations.txt

def getDistance(x1, y1, x2, y2):
    # Loop through the client list and find the distance between the 
    # sensor and every other sensor/bsae station
    # it is reachable if both ranges are greater than or equal 
    distance = math.sqrt(((x1-x2)**2)+((y1-y2)**2))
    return distance

# Loop through the client list and find the distance between the 
# sensor and every other sensor/bsae station
# it is reachable if both ranges are greater than or equal 
def reachable(client_socket, IDToSearch, clients, base_stations):

    reachableList = {}
    curR = clients[IDToSearch]["r"]
    curX = clients[IDToSearch]["x"]
    curY = clients[IDToSearch]["y"]

    # loop through every sensor
    for ID in clients:
        destR = clients[ID]["r"]
        destX = clients[ID]["x"]
        destY = clients[ID]["y"]
        d = getDistance(curX, curY, destX, destY)
        if (curR >= d and destR >= d and ID != IDToSearch):
            reachableList[ID] = {}
            reachableList[ID]["d"] = d
            reachableList[ID]["x"] = destX
            reachableList[ID]["y"] = destY

    # loop through every base station
    for bs in base_stations:
        destX = base_stations[bs]["x"]
        destY = base_stations[bs]["y"]
        d = getDistance(curX, curY, destX, destY)
        if (curR >= d and bs != IDToSearch):
            reachableList[bs] = {}
            reachableList[bs]["d"] = d
            reachableList[bs]["x"] = destX
            reachableList[bs]["y"] = destY

    send_string = "REACHABLE " + str(len(reachableList)) + " "

    # simply serialize the dictionary? or using format specified in the instructions?
    data_string = json.dumps(reachableList)
    send_string += data_string
    
    client_socket.sendall(send_string.encode('utf-8'))

# Take in a list of reachable sensors/base-stations and remove items in the hoplist from reachableList
# Returns the ID of item in reachableList that is closest to destination and NOT in hopList
def getClosestValidReachable(reachableList, destX, destY, hopList):
    for ID in reachableList:
        if ID in hopList:
            reachableList.remove(ID)
    minDistance = -1
    closestId= ''
    for ID in reachableList:
        itemDistance = getDistance(reachableList[ID][x], reachableList[ID][y], destX, destY)
        if minDistance == -1 or itemDistance < minDistance:
            minDistance = itemDistance
            closestID = ID

    return closestID

    

    


def sendTHERE(client_socket, IDToSearch, clients):
    finalString = "THERE " + IDToSearch + " " + str(clients[IDToSearch]["x"]) + " " + str(clients[IDToSearch]["y"])
    print(finalString)
    client_socket.sendall(finalString.encode('utf-8'))

def handleDataMessage():


def run_server():
    if len(sys.argv) != 3:
        printf("Proper usage is {sys.argv[0]} [control port] [base station file]")
        sys.exit(0)

    base_stations = {}
    clients = {}
    # Reads the base station file and parse each line
    filepath = sys.argv[2]
    with open(filepath) as fp:
        for line in fp:
            commands = line.split()
            base_stations[commands[0]] = {}
            base_stations[commands[0]]["x"] = int(commands[1])
            base_stations[commands[0]]["y"] = int(commands[2])
            base_stations[commands[0]]["numLinks"] = int(commands[3])
            base_stations[commands[0]]["linkList"] = []
            for i in range(4, len(commands)):
                base_stations[commands[0]]["linkList"].append(commands[i])

    # Create a TCP socket
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.setblocking(0)

    # Set the socket to listen on localhost, on the specified port
    # bind takes a 2-tuple, not 2 arguments
    listening_socket.bind(('localhost', int(sys.argv[1])))
    listening_socket.listen(5)
    inputs = [sys.stdin, listening_socket]
    sockets = [listening_socket]
    outputs = []

    while True:
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:

            if s is sys.stdin:
                line = sys.stdin.readline()
                command = line.split()

               
                if (command[0] == 'SENDDATA'):
                    originID = command[1]
                    destID = command[2]
                    hopListLength = 0
                    hopList = []
                    nextID = ''

                     '''
                    If the[OriginID] is CONTROL then when deciding the next hop, all base stations should be considered
                    reachable, and the [NextID] must be a base station
                     '''
                    if originID == 'CONTROL':
                        
                    
                    '''
                     If the [OriginID] is a base station, then the
                    next hop should be decided based on what is reachable from the base station with that [BaseID]. The
                    [OriginID] will never be a sensor in this command.
                    '''
                    else:




                elif (command[0] == 'QUIT'):
                    print("server: QUIT")

            # if new socket connection
            elif s is listening_socket:
                (client_socket, address) = s.accept()
                client_socket.setblocking(0)
                inputs.append(client_socket)
                sockets.append(client_socket)
                print("new socket added")

            # if one of the sockets receives something
            else:
                message = s.recv(1024).decode('utf-8') # needs to encode bystring to string
                if message:
                    command = message.split()
                    if (command[0] == 'WHERE'):
                        print("client: " + message)
                        sendTHERE(s, command[1], clients)

                    elif (command[0] == 'UPDATEPOSITION'):
                        print("client: " + message)
                        args = message.split()
                        clients[args[1]] = {}
                        clients[args[1]]["r"] = int(args[2])
                        clients[args[1]]["x"] = int(args[3])
                        clients[args[1]]["y"] = int(args[4])
                        reachable(s, command[1], clients, base_stations)

                    elif (command[0] == 'DATAMESSAGE'):
                        print("client: DATAMESSAGE")
                        printf("Server received {len(message)} bytes: \"{message}\"")

                else:
                    #print("Client has closed")
                    #client_socket.close()
                    break

if __name__ == '__main__':
    run_server()
