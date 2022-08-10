import socket
import json
from threading import Thread
import logging

class SGW:

    def __init__(self, max_entry, port, mme_port, t0):
        self.t0 = t0
        self.buffer = []
        self.enb_uids = []
        self.routing_table = {}
        self.max_entry = max_entry
        self.port = port
        self.mme_port = mme_port
        self.mme_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket for connecting to MME

    def __str__(self):
        return f"ENBs are: {self.uids}\nMaximum number of entries in the routing table is: {self.max_entry}\nRouting Table:\n{self.routing_table}"

    def ENB_SGW_connection(self, c):
        # handling messages for connections from ENBs
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "eNodeB-SGW Connection":
                uid = data["payload"]["uid"]
                self.enb_uids.append(uid)
                logging.info(f'SGW added eNodeB with uid {uid} to its eNodebs list.')

    def start_server(self):
        # starting server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        logging.critical(f'Server of SGW started on port {self.port}.')
        while True:
            c, addr = s.accept()
            Thread(target=self.ENB_SGW_connection, args=(c,)).start()
    
    def connect_mme(self):
        # connect to MME
        try:
            self.mme_socket.connect(('127.0.0.1', self.mme_port))
            logging.critical('SGW connected to MME.')
        except:
            logging.error('SGW cannot connect to MME!!!')
