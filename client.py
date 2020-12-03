#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select

# python3 client.py [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]
# i.e.,: python3 client.py control 9000 client1 10 5 5



def sendWhere(server_socket, inputs, outputs, IDToSearch):
    # package where message
    send_string = "WHERE " + str(IDToSearch)

    # send WHERE message
    server_socket.sendall(send_string.encode('utf-8'))




def run_client():
    if len(sys.argv) != 7:
        print(f"Proper usage is {sys.argv[0]} [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]")
        sys.exit(0)
    ID = sys.argv[3]
    r = int(sys.argv[4])
    xPos = int(sys.argv[5])
    yPos = int(sys.argv[6])
    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind takes a 2-tuple, not 2 arguments
    server_socket.connect(('localhost', int(sys.argv[2])))

    # sends a UPDATEPOSITION to server once sensor starts up
    tmp = "UPDATEPOSITION " + ID + " " + str(r) + " " + str(xPos) + " " + str(yPos)
    server_socket.sendall(tmp.encode('utf-8'))
    inputs = [sys.stdin, server_socket]
    outputs = []

    while True:
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                line = sys.stdin.readline()
                command = line.split()
                if (command[0] == 'MOVE'):
                    print("MOVE")
                    xPos =int(command[1])
                    yPos = int(command[2])
                    # senddata [SensorID] [SensorRange] [CurrentXPosition] [CurrentYPosition]
                    #self.senddata("UPDATEPOSITION",[self.sensor_id,self.sensor_range,self.x,self.y])
                    sendmessage = "UPDATEPOSITION"
                    sendmessage += " "+ID
                    sendmessage += " "+ str(r)
                    sendmessage += " "+ str(xPos)
                    sendmessage += " "+ str(yPos)
                    server_socket.send(sendmessage.encode('utf-8'))
                    # they should receive a REACHABLE message
                    while True:
                        data = server_socket.recv(4096)
                        if data.startswith("REACHABLE"):
                            break;
                if (command[0] == 'SENDDATA'):
                    print("SENDDATA")
                    send_string = "WHERE"
                    server_socket.sendall(send_string.encode('utf-8'))

                # ~~~~~~~ CJ's testing Code
                elif (command[0] == 'WHERE'):
                    IDToSearch = command[1]
                    sendWhere(server_socket, inputs, outputs, IDToSearch)

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

                    elif (command[0] == 'THERE'):
                        print("Receive THERE")
                        print(command)
                else:
                    print("Server has closed")
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
