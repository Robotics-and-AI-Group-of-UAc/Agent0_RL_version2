from middleware_impl import REQ,REP
import time
import ast
import zmq

class ZMQSocket():
    def __init__(self,host:str,port:int,type:int):
        self.host = host
        self.port = port
        context = zmq.Context()
        con = "tcp://" + host + ":" + str(port)
        if type == REQ:
            self.s = context.socket(zmq.REQ)
            self.s.connect(con)
        else:
            self.s = context.socket(zmq.REP)
            self.s.bind(con)

    def send_msg(self, value):
        self.s.send_string(value)


    def recv_msg(self):
        data = self.s.recv_string()
        # test
        # print('Data received', data)
        return data

    def disconnect(self):
        self.s.disconnect()

    def execute(self,action:str,value:str,sleep_t = 0.5)-> object:
        self.s.send_string(action+" "+value)
        data = self.s.recv_string()
        # test
        # print('Data received', data)
        time.sleep(sleep_t)
        return data
