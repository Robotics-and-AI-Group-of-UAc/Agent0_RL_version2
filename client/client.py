#!/usr/bin/env python3
import socket
import time
from middleware_impl.zmq_socket import ZMQSocket
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001      # The port used by the server
from middleware_impl import REQ

class Client:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.sock = ZMQSocket(host,port,REQ)

    def execute(self,action,value):
        return self.sock.execute(action,value)


    def print_message(self, data):
        print("Data:", data)


def main():
    client = Client()
    while True:
        command = input("Insert action value pairs:").split()
        if len(command) != 2:
            action, value = "", ""
        else:
            action, value = command
            print("Action Value pair:", action, ":", value)
            msg = client.execute(action, value)
            # test
            client.print_message(msg)


if __name__ == "__main__":
    main()
