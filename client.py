#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select
import json
import math
# python3 client.py [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]
# i.e.,: python3 client.py control 8071 client1 10 5 5
# [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]


# Hey man there's an error in server. SendTHERE also needs to check for base stations
# I think my code's done. Debugged quite a bit. Kinda hard to test cause of sendThere and stuff

def sendWhere(server_socket, inputs, outputs, IDToSearch):
    # package where message
    send_string = "WHERE " + str(IDToSearch)
    
    # send WHERE message
    server_socket.sendall(send_string.encode('utf-8'))
    while True:
        data = server_socket.recv(4096).decode("utf-8")
        command = data.split()
        if (command[0] == 'THERE'):
            return data

# Calls recDataMessage. Might cause errors with printing stuff
def sendData(server_socket, inputs, outputs, ID, r, xPos, yPos, line):
    data = line.split(' ')
    assert data[0] == "SENDDATA", "message is not senddata. Message: " + line
    destID = data[1]
    hoplist = [ID]
    s = "DATAMESSAGE " + ID + " nextID " + destID + " 0 " + json.dumps(hoplist)
    recDataMessage(server_socket, inputs, outputs, ID, r, xPos, yPos, s)

def updatePosition(server_socket, inputs, outputs, ID, r, xPos, yPos):
     sendmessage = "UPDATEPOSITION"
     sendmessage += " " + ID
     sendmessage += " " + str(r)
     sendmessage += " " + str(xPos)
     sendmessage += " " + str(yPos)
     server_socket.sendall(sendmessage.encode('utf-8'))

     # they should receive a REACHABLE message
     while True:
        data = server_socket.recv(4096).decode("utf-8")
        command = data.split()
        if (command[0] == 'REACHABLE'):
            numReachable = command[1]
            string_data = data.split(" ", 2)[2]
            reachable = json.loads(string_data)
            return reachable


"""
Things I haven't done:
updatePosition: figure out what it returns??

test where

test this in general

"""
# DATAMESSAGE [OriginID] [NextID] [DestinationID] [HopListLength] [HopList]
def recDataMessage(server_socket, inputs, outputs, ID, r, xPos, yPos, message):
    dataMessage = message.split(' ', 5)
    assert len(dataMessage) == 6, "Incorrect length of message (length is " + str(len(dataMessage)) + ")"
    assert dataMessage[0] == "DATAMESSAGE", "message is not DATAMESSAGE"
    originID = dataMessage[1]
    nextID = dataMessage[2]
    destID = dataMessage[3]
    hopListLength = int(dataMessage[4])
    hopList = json.loads(dataMessage[5]) # might want to change to json.loads

    # Check if we're at destination
    if (ID == destID):
        print("" + ID + ": Message from " + originID + " to " + destID + " succesfully received.")
        return

    # Check reachable nodes
    reachableNodes = updatePosition(server_socket, inputs, outputs, ID, r, xPos, yPos)
    numReachable = len(reachableNodes)

    s = sendWhere(server_socket, inputs, outputs, destID)
    ary = s.split(' ')
    assert ary[0] == "THERE", "message is not THERE"
    destX = int(ary[2])
    destY = int(ary[3])

    # Find closest node
    closestID = "-9999"
    closestDist = math.inf
    for reachID in reachableNodes:
        reachX = reachableNodes[reachID]['x']
        reachY = reachableNodes[reachID]['y']
        if (not (reachID in hopList)):
            dist = math.sqrt((destX - reachX) ** 2 + (destY - reachY) ** 2)
            if (dist < closestDist or (dist == closestDist and reachID < closestID)):
                closestDist = dist
                closestID = reachID
                
    # Print result and send it
    if (closestID == "-9999" and math.isinf(closestDist)):
        print("" + ID + ": Message from " + originID + " to " + destID + " could not be delivered.")
    else:
        # Package result
        currentID = nextID
        nextID = closestID
        hopList.append(nextID)
        hopListLength += 1
        # hopList += "," + ID   # control will add nextID to hoplist
        # hopeListLength += 1
        if (ID == originID and nextID == destID):
            print("" + ID + ": Sent a new message directly to " + destID)
        elif (ID == originID):
            print("" + ID + ": Sent a new message bound for " + destID)
        else:
            print("" + ID + ": Message from " + originID + " to " + destID + " being forwarded through " + currentID)
            
        send_string = "DATAMESSAGE " + originID + " " + nextID + " " + destID + " " + str(hopListLength) + " " + json.dumps(hopList) # Might have an error: hoplist might need to be updated
        server_socket.sendall(send_string.encode('utf-8'))
    return

    

def run_client():
    if len(sys.argv) != 7:
        printf("Proper usage is {sys.argv[0]} [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]")
        sys.exit(0)
    ID = sys.argv[3]
    r = int(sys.argv[4])
    xPos = int(sys.argv[5])
    yPos = int(sys.argv[6])
    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind takes a 2-tuple, not 2 arguments
    server_socket.connect(('localhost', int(sys.argv[2])))


    inputs = [sys.stdin, server_socket]
    outputs = []

    # sends a UPDATEPOSITION to server once sensor starts up
    updatePosition(server_socket, inputs, outputs, ID, r, xPos, yPos)

    while True:
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                line = sys.stdin.readline().strip()
                command = line.split()
                if (command[0] == 'MOVE'):
                    print("client: MOVE")
                    xPos =int(command[1])
                    yPos = int(command[2])
                    updatePosition(server_socket, inputs, outputs, ID, r, xPos, yPos)

                if (command[0] == 'SENDDATA'):
                    print("client: SENDDATA")
                    sendData(server_socket, inputs, outputs, ID, r, xPos, yPos, line)
                    #send_string = "WHERE"
                    #server_socket.sendall(send_string.encode('utf-8'))

                elif (command[0] == 'WHERE'):
                    IDToSearch = command[1]
                    sendWhere(server_socket, inputs, outputs, IDToSearch)

                elif (command[0] == 'QUIT'):
                    print("QUIT")
                # THIS IS JUST FOR DEBUGGING: REMOVE THE FOLLOWING AFTER FINISHED TESTING
                elif (command[0] == 'DATAMESSAGE'):
                    print("server: DATAMESSAGE")
                    recDataMessage(server_socket, inputs, outputs, ID, r, xPos, yPos, line)
            else:
                message = s.recv(1024).decode("utf-8")
                if message:
                    command = message.split()
                    if (command[0] == 'DATAMESSAGE'):
                        print("server: DATAMESSAGE")
                        recDataMessage(server_socket, inputs, outputs, ID, r, xPos, yPos, message)
                else:
                    #print("Server has closed")
                    #client_socket.close()
                    break

    # Disconnect from the server
    print("Closing connection to server")
    server_socket.close()

if __name__ == '__main__':
    #recDataMessage("9001", "DATAMESSAGE 9000 2 9005 4 5")
    run_client()
