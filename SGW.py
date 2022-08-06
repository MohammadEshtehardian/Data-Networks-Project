import socket
import json
from threading import Thread

class SGW:

    def __init__(self, max_entry, port, mme_port):
        self.buffer = []
        self.enb_uids = []
        self.routing_table = {}
        self.max_entry = max_entry
        self.port = port
        self.mme_port = mme_port
        self.mme_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return f"ENBs are: {self.uids}\nMaximum number of entries in the routing table is: {self.max_entry}\nRouting Table:\n{self.routing_table}"

    def ENB_SGW_connection(self, c):
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "eNodeB-SGW Connection":
                uid = data["payload"]["uid"]
                self.enb_uids.append(uid)

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        while True:
            c, addr = s.accept()
            Thread(target=self.ENB_SGW_connection, args=(c,)).start()
    
    def connect_mme(self):
        self.mme_socket.connect(('127.0.0.1', self.mme_port))