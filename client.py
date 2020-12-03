#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select

# python3 client.py [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]
# i.e.,: python3 client.py control 9000 client1 10 5 5
# [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]
class sensor:
    def __init__(self,ctrl_address,ctrl_port,sensor_id,sensor_range,x,y):
        self.ctrl_address = ctrl_address
        self.ctrl_port = ctrl_port
        self.sensor_id = sensor_id
        self.sensor_range = sensor_range
        self.x = x
        self.y = y
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def move(new_x,new_y):
            self.x = new_x
            self.y = new_y
            # senddata [SensorID] [SensorRange] [CurrentXPosition] [CurrentYPosition]
            self.senddata("UPDATEPOSITION",[self.sensor_id,self.sensor_range,self.x,self.y])

        def senddata(message,parameters):
            sendmessage = message
            for p in parameters:
                sendmessage += str(p)
            self.socket.send(sendmessage)









def run_client():
    if len(sys.argv) != 7:
        print(f"Proper usage is {sys.argv[0]} [control address] [control port] [SensorID] [SensorRange] [InitalXPosition] [InitialYPosition]")
        sys.exit(0)
    cur_sensor = sensor(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])

    # Create the TCP socket, connect to the server

    # bind takes a 2-tuple, not 2 arguments
    self.socket.connect(('localhost', int(sys.argv[2])))
    inputs = [sys.stdin, self.socket]
    outputs = []

    while True:
        print("at the beginning of loop")
        readable, writeable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is sys.stdin:
                line = sys.stdin.readline()
                command = line.split()
                if (command[0] == 'MOVE'):
                    NewXPosition = command[1]
                    NewYPosition =  command[2]

                    print("MOVE")
                if (command[0] == 'SENDDATA'):
                    print("SENDDATA")
                    send_string = "WHERE"
                    self.socket.sendall(send_string.encode('utf-8'))

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
    self.socket.close()

    # Print the response to standard output, both as byte stream and decoded text
    print(f"Received {recv_string} from the server")
    print(f"Decoding, received {recv_string.decode('utf-8')} from the server")

if __name__ == '__main__':
    run_client()
