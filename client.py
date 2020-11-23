#!/usr/bin/env python3

import sys  # For arg parsing
import socket  # For sockets
import select

def run_client():
    #if len(sys.argv) != 3:
        #print(f"Proper usage is {sys.argv[0]} [server name/address] [server port]")
        #sys.exit(0)

    # Create the TCP socket, connect to the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind takes a 2-tuple, not 2 arguments
    server_socket.connect(('localhost', int(sys.argv[1])))
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
    print(f"Received {recv_string} from the server")
    print(f"Decoding, received {recv_string.decode('utf-8')} from the server")

if __name__ == '__main__':
    run_client()