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
def reachable(IDToSearch, clients, base_stations):

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

    return(reachableList)

#similar to above function. But specifically for what is reachable from a base station. 
# I.e A base station is only reachable to another base station if they are directly linked
# Also, base stations have infinite range so they're range is not considered
def reachableFromBaseStation(IDToSearch, clients, base_stations):
    reachableList = {}
    curX = base_stations[IDToSearch]["x"]
    curY = base_stations[IDToSearch]["y"]

    # loop through every sensor
    for ID in clients:
        destR = clients[ID]["r"]
        destX = clients[ID]["x"]
        destY = clients[ID]["y"]
        d = getDistance(curX, curY, destX, destY)
        if (destR >= d and ID != IDToSearch):
            reachableList[ID] = {}
            reachableList[ID]["d"] = d
            reachableList[ID]["x"] = destX
            reachableList[ID]["y"] = destY

    # loop through every base station
    for bs in base_stations:
        if bs in base_stations[IDToSearch]["linkList"]:
            reachableList[bs] = {}
            reachableList[bs]["x"] = base_stations[bs]["x"]
            reachableList[bs]["y"] = base_stations[bs]["y"]
    return(reachableList)


# Take in a list of reachable sensors/base-stations and remove items in the hoplist from reachableList
# Returns the ID of item in reachableList that is closest to destination and NOT in hopList
def getClosestValidReachable(reachableList, destX, destY, hopList):
    for ID in hopList:
        if ID in reachableList:
            reachableList.pop(ID)
    minDistance = -1
    closestId= ''
    for ID in reachableList:
        itemDistance = getDistance(reachableList[ID]['x'], reachableList[ID]['y'], destX, destY)
        if minDistance == -1 or itemDistance < minDistance:
            minDistance = itemDistance
            closestID = ID

    return closestID

#gets x,y locaitons of client or base station that is being inquired about
def getLocation(IDToSearch, clients, base_stations):
    x = -1 
    y = -1
    if IDToSearch in base_stations:
        x = base_stations[IDToSearch]["x"]
        y = base_stations[IDToSearch]["y"]
    else:
        x = clients[IDToSearch]["x"]
        y = clients[IDToSearch]["y"]
    return x,y

# Sends THERE string to client with x,y location of client or base station that is being inquired about
def sendTHERE(client_socket, IDToSearch, clients, base_stations):
    x,y = getLocation(IDToSearch, clients, base_stations)
    finalString = "THERE " + IDToSearch + " " + str(x) + " " + str(y)
    client_socket.sendall(finalString.encode('utf-8'))

#Takes in full DATAMESSAGE string and decides next move base do what is given
def handleDataMessage(dataMessage, base_stations, clients):
    print(dataMessage)
    dataMessage = dataMessage.split(' ', 5)
    originID = dataMessage[1]
    nextID = dataMessage[2]
    destID = dataMessage[3]
    hopListLength = int(dataMessage[4])
    hopList = json.loads(dataMessage[5])



    
    if nextID in clients:
        hopList.append(nextID)
        hopListLength += 1
        dataMessage = 'DATAMESSAGE ' + originID + ' ' + nextID + ' ' + destID + ' ' + str(len(hopList)) + ' ' + json.dumps(hopList)
        clients[nextID]["socket"].sendall(dataMessage.encode('utf-8'))
        #update hopList
        #SEND to correct client here

    else:
        while nextID in base_stations:
            reachableList = reachableFromBaseStation(nextID, clients, base_stations)
            destX, destY = getLocation(destID, clients, base_stations)
            newNextID = getClosestValidReachable(reachableList.copy(), destX, destY, hopList)
            if nextID == destID:
                print("{}: message from  {} to {} successfully received".format(destID, originID, destID))
                break
            elif newNextID == '':
                print('{}: Message from {} to {} could not be delivered.'.format(nextID, originID, destID))
                break
            else:
                print('{}: Message from {} to {} being forwarded through {}'.format(nextID, originID, destID, NextID))
                hopList.append(newNextID)
                nextID = newNextID
                if nextID in clients:
                     dataMessage = 'DATAMESSAGE ' + originID + ' ' + nextID + ' ' + destID + ' ' + str(len(hopList)) + ' ' + json.dumps(hopList)
                     clients[nextID]["socket"].sendall(dataMessage.encode('utf-8'))
                     break









    return

def run_server():
    if len(sys.argv) != 3:
        print("Proper usage is {sys.argv[0]} [control port] [base station file]")
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

                    '''
                    If the [OriginID] is CONTROL then when deciding the next hop, all base stations should be considered
                    reachable, and the [NextID] must be a base station
                    '''
                    if originID == 'CONTROL':
                        destX, destY = getLocation(destID, clients, base_stations)
                        nextID = getClosestValidReachable(base_stations.copy(), destX, destY, [])
                        hopList = [originID, nextID]
                        datamessage = 'DATAMESSAGE ' + originID + ' ' + nextID + ' '+  destID + ' ' + str(len(hopList)) + ' ' + json.dumps(hopList)
                        handleDataMessage(datamessage, base_stations, clients)
                    
 
                    else:
                        '''
                        If the [OriginID] is a base station, then the
                        next hop should be decided based on what is reachable from the base station with that [BaseID]. The
                        [OriginID] will never be a sensor in this command.
                        '''

                        destX, destY = getLocation(destID, clients, base_stations)
                        reachableList = reachableFromBaseStation(originID, clients, base_stations)
                        nextID = getClosestValidReachable(reachableList.copy(), destX, destY, [])
                        hopList = [originID, nextID]
                        datamessage = 'DATAMESSAGE ' + originID + ' ' + nextID + ' ' + destID + ' ' + str(len(hopList)) + ' ' + json.dumps(hopList)
                        if(nextID == destID):
                            print('{}: Sent a new message directly to {}.'.format(originID, destID))
                        else:
                            print('{}: Sent a new message bound for {}.'.format(originID, destID ))
                        handleDataMessage(datamessage, base_stations, clients)
                        




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
                        sendTHERE(s, command[1], clients, base_stations)

                    elif (command[0] == 'UPDATEPOSITION'):
                        print("client: " + message)
                        args = message.split()
                        clients[args[1]] = {}
                        clients[args[1]]["r"] = int(args[2])
                        clients[args[1]]["x"] = int(args[3])
                        clients[args[1]]["y"] = int(args[4])
                        clients[args[1]]["socket"] = s
                        reachableList = reachable( command[1], clients, base_stations)
                        send_string = "REACHABLE " + str(len(reachableList)) + " "
                        # simply serialize the dictionary? or using format specified in the instructions?
                        data_string = json.dumps(reachableList)
                        send_string += data_string
                        s.sendall(send_string.encode('utf-8'))

                    elif (command[0] == 'DATAMESSAGE'):
                        handleDataMessage(message, base_stations, clients)

                else:
                    #print("Client has closed")
                    #client_socket.close()
                    break

if __name__ == '__main__':
    run_server()
