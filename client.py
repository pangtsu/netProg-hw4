#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select

# python3 client.py [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]
# i.e.,: python3 client.py control 9000 client1 10 5 5


""" 
Sensors can send a WHERE message to the control server:
WHERE [SensorID/BaseID] to get the location of a particular base station or sensor ID from the control server. It should not take any other actions until it gets a THERE message back from the server.

NOTE: THIS IS A RUDIMENTARY ATTEMPT. CAN BE EDITED TO BE IMPROVED (maybe not)
Things I've done:
  1. Send a string with a (hardcoded) id

Things I haven't tested:
  1. Receiving a message
  2. Printing the received message
  3. Waiting for the message and then breaking loop

Things I haven't done:
  1. Using standard input to access the id
  2. Return the message
"""
def sendWhere(server_socket, inputs, outputs, id):
    # package where message
    send_string = "WHERE Just a random message " + str(id)
    
    # send WHERE message
    server_socket.sendall(send_string.encode('utf-8'))
    
    # wait for reply
    print("Just waiting for a message~")

    # receive THERE message
    while True:
        print("at the beginning of loop")
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                print("Hello!")
                #do nothing. Just copying Joann's code for now. Shouldn't be anything...
            else:
                message = s.recv(1024).decode("utf-8")
                if message:
                    stuff = message.split()
                    if (stuff[0] == "THERE"):
                        print("Message:")
                        print(stuff)
                        break
                    else:
                        print("Received non-there message:")
                        print(stuff)
                        break
                else:
                    print("Error in WHERE")
                    break
    
    return None



def run_client():
    if len(sys.argv) != 7:
        printf("Proper usage is {sys.argv[0]} [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]")
        sys.exit(0)

    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind takes a 2-tuple, not 2 arguments
    server_socket.connect(('localhost', int(sys.argv[2])))
    inputs = [sys.stdin, server_socket]
    outputs = []

    while True:
        print("at the beginning of loop")
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                line = sys.stdin.readline()
                command = line.split()
                if (command[0] == 'MOVE'):
                    print("MOVE")
                if (command[0] == 'SENDDATA'):
                    print("SENDDATA")
                    send_string = "WHERE"
                    server_socket.sendall(send_string.encode('utf-8'))
                    
                # ~~~~~~~ CJ's testing Code
                elif (command[0] == 'WHERE'):
                    print("This is a where~ ID is set to 10 for now~")
                    sendWhere(server_socket, inputs, outputs, 10)
                    
                # ~~~~~~~ end CJ's testing code
 
                elif (command[0] == 'QUIT'):
                    print("QUIT")
            else:
                message = s.recv(1024).decode("utf-8")
                if message:
                    command = message.split()
                    if (command[0] == 'DATAMESSAGE'):
                        print("WHERE")
                    #client_socket.send(message)
                else:
                    print("Client has closed")
                    #client_socket.close()
                    break

    # Disconnect from the server
    print("Closing connection to server")
    server_socket.close()

    # Print the response to standard output, both as byte stream and decoded text
    print("Received {recv_string} from the server")
    print("Decoding, received {recv_string.decode('utf-8')} from the server")

if __name__ == '__main__':
    run_client()
