#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select


# python3 server.py [control port] [base station file]
# i.e.,: python3 server.py 9000 base_stations.txt

def handleWHERE(client_socket, IDToSearch, ):
    finalString = "THERE " + IDToSearch + " " + sensorLocations[IDToSearch]["x"] + " " + sensorLocations[IDToSearch]["y"]
    client_socket.sendAll(finalString)

def run_server():
    if len(sys.argv) != 3:
        printf("Proper usage is {sys.argv[0]} [control port] [base station file]")
        sys.exit(0)

    sensorLocations = {}
    base_stations = {}
    # Reads the base station file and parse each line
    filepath = sys.argv[2]
    with open(filepath) as fp:
        for line in fp:
            commands = line.split()
            base_stations[commands[0]] = {}
            base_stations[commands[0]]["x"] = commands[1]
            base_stations[commands[0]]["y"] = commands[2]
            base_stations[commands[0]]["numLinks"] = commands[3]
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
        print("at the beginning of loop")
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                line = sys.stdin.readline()
                command = line.split()

                if (command[0] == 'SENDDATA'):
                    print("SENDDATA")

                elif (command[0] == 'QUIT'):
                    print("QUIT")

            elif s is listening_socket:
                (client_socket, address) = s.accept()
                client_socket.setblocking(0)
                inputs.append(client_socket)
                sockets.append(client_socket)
                print("new socket added")

            else:
                # needs to encode bystring to string
                message = s.recv(1024).decode('utf-8')
                if message:
                    command = message.split()
                    if (command[0] == 'WHERE'):
                        print("WHERE:")
                        print(command)

                        # This is where you call the THERE function. I think

                    elif (command[0] == 'UPDATEPOSITION'):
                        print("UPDATEPOSITION")

                    elif (command[0] == 'DATAMESSAGE'):
                        print("DATAMESSAGE")
                        printf("Server received {len(message)} bytes: \"{message}\"")

                    elif (command[0]) == 'WHERE':
                        print('WHERE')
                        handleWHERE(s, command[1])
                    #client_socket.send(message)
                else:
                    print("Client has closed")
                    #client_socket.close()
                    break

if __name__ == '__main__':
    run_server()
